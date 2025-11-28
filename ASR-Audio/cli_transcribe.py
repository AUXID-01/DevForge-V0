#!/usr/bin/env python3
"""
Whisper AI CLI Transcription Tool
Supports multiple audio formats, batch processing, model selection, and translation
"""

import argparse
import whisper
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

# Available Whisper models: tiny, base, small, medium, large
MODEL_SIZES = ["tiny", "base", "small", "medium", "large", "tiny.en", "base.en", "small.en", "medium.en"]

# Supported languages (partial list - Whisper supports 96+ languages)
SUPPORTED_LANGUAGES = [
    "en", "zh", "de", "es", "ru", "ko", "fr", "ja", "pt", "tr", "pl", "ca", "nl", 
    "ar", "sv", "it", "id", "hi", "fi", "vi", "he", "uk", "el", "ms", "cs", "ro", 
    "da", "hu", "ta", "no", "th", "ur", "hr", "bg", "lt", "la", "mi", "ml", "cy", 
    "sk", "te", "fa", "lv", "bn", "sr", "az", "sl", "kn", "et", "mk", "br", "eu", 
    "is", "hy", "ne", "mn", "bs", "kk", "sq", "sw", "gl", "mr", "pa", "si", "km", 
    "sn", "yo", "so", "af", "oc", "ka", "be", "tg", "sd", "gu", "am", "yi", "lo", 
    "uz", "fo", "ht", "ps", "tk", "nn", "mt", "sa", "lb", "my", "bo", "tl", "mg", 
    "as", "tt", "haw", "ln", "ha", "ba", "jw", "su"
]


def create_output_files(result: dict, audio_file: Path, output_dir: Optional[Path] = None):
    """
    Create TXT, SRT, and JSON output files for transcription results.
    
    Args:
        result: Whisper transcription result dictionary
        audio_file: Path to the original audio file
        output_dir: Optional directory for output files (default: same as audio file)
    """
    if output_dir is None:
        output_dir = audio_file.parent
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = audio_file.stem
    
    # 1. TXT file - Plain text transcript
    txt_file = output_dir / f"{base_name}.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(result['text'].strip())
    print(f"  ✓ Created: {txt_file.name}")
    
    # 2. SRT file - Subtitle format with timestamps
    srt_file = output_dir / f"{base_name}.srt"
    with open(srt_file, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result['segments'], start=1):
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")
    print(f"  ✓ Created: {srt_file.name}")
    
    # 3. JSON file - Structured data with all details
    json_file = output_dir / f"{base_name}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Created: {json_file.name}")


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm)
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def transcribe_audio(
    audio_files: List[Path],
    model_name: str = "small",
    language: Optional[str] = None,
    task: str = "transcribe",
    output_dir: Optional[Path] = None,
    verbose: bool = False
):
    """
    Transcribe one or more audio files using Whisper AI.
    
    Args:
        audio_files: List of audio file paths
        model_name: Whisper model size (tiny, base, small, medium, large)
        language: Language code (auto-detect if None)
        task: 'transcribe' or 'translate' (translate to English)
        output_dir: Directory for output files
        verbose: Show detailed progress
    """
    # Load Whisper model
    print(f"\n🔄 Loading Whisper '{model_name}' model...")
    try:
        model = whisper.load_model(model_name)
        print(f"✓ Model loaded successfully\n")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        sys.exit(1)
    
    # Process each audio file
    total_files = len(audio_files)
    for idx, audio_file in enumerate(audio_files, start=1):
        print(f"[{idx}/{total_files}] Processing: {audio_file.name}")
        
        if not audio_file.exists():
            print(f"  ❌ File not found: {audio_file}")
            continue
        
        try:
            # Transcribe with specified options
            transcribe_options = {
                "task": task,
                "verbose": verbose,
            }
            
            if language:
                transcribe_options["language"] = language
                print(f"  Language: {language}")
            else:
                print(f"  Language: Auto-detect")
            
            if task == "translate":
                print(f"  Task: Translate to English")
            
            print(f"  🎙️  Transcribing...")
            result = model.transcribe(str(audio_file), **transcribe_options)
            
            # Display detected language
            detected_lang = result.get('language', 'unknown')
            print(f"  ✓ Detected language: {detected_lang}")
            
            # Create output files
            create_output_files(result, audio_file, output_dir)
            
            # Show preview of transcript
            preview_text = result['text'].strip()[:100]
            if len(result['text']) > 100:
                preview_text += "..."
            print(f"  📝 Preview: {preview_text}\n")
            
        except Exception as e:
            print(f"  ❌ Error processing {audio_file.name}: {e}\n")
            continue
    
    print(f"✅ Completed processing {total_files} file(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Whisper AI CLI - Transcribe audio files with OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe single audio file
  python cli_transcribe.py audio.wav
  
  # Transcribe multiple files
  python cli_transcribe.py audio1.wav audio2.mp3 audio3.mp4
  
  # Use medium model for better quality
  python cli_transcribe.py audio.wav --model medium
  
  # Specify language manually
  python cli_transcribe.py german.wav --language de
  
  # Translate foreign language to English
  python cli_transcribe.py german.wav --task translate
  
  # Save outputs to specific directory
  python cli_transcribe.py audio.wav --output-dir ./transcripts
  
  # Show detailed progress
  python cli_transcribe.py audio.wav --verbose

Model sizes (tiny < base < small < medium < large):
  - tiny:   fastest, lowest quality (~1GB VRAM)
  - base:   fast, decent quality (~1GB VRAM)
  - small:  balanced (default) (~2GB VRAM)
  - medium: slower, better quality (~5GB VRAM)
  - large:  slowest, best quality (~10GB VRAM)
  
Output files created:
  - .txt: Plain text transcript
  - .srt: Subtitle file with timestamps
  - .json: Structured data with segments and metadata
        """
    )
    
    parser.add_argument(
        'audio_files',
        nargs='+',
        type=str,
        help='Audio file(s) to transcribe (WAV, MP3, MP4, etc.)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='small',
        choices=MODEL_SIZES,
        help='Whisper model size (default: small)'
    )
    
    parser.add_argument(
        '--language',
        type=str,
        choices=SUPPORTED_LANGUAGES,
        help='Audio language code (auto-detect if not specified)'
    )
    
    parser.add_argument(
        '--task',
        type=str,
        default='transcribe',
        choices=['transcribe', 'translate'],
        help='Task to perform: transcribe or translate to English (default: transcribe)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for transcription files (default: same as audio file)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed transcription progress'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'Whisper CLI v1.0 (whisper {whisper.__version__})'
    )
    
    args = parser.parse_args()
    
    # Convert file paths
    audio_files = [Path(f).resolve() for f in args.audio_files]
    output_dir = Path(args.output_dir).resolve() if args.output_dir else None
    
    # Validate audio files exist
    valid_files = []
    for f in audio_files:
        if f.exists():
            valid_files.append(f)
        else:
            print(f"⚠️  Warning: File not found: {f}")
    
    if not valid_files:
        print("❌ No valid audio files found")
        sys.exit(1)
    
    # Display configuration
    print("=" * 60)
    print("Whisper AI CLI Transcription Tool")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Task: {args.task}")
    print(f"Files: {len(valid_files)}")
    if args.language:
        print(f"Language: {args.language}")
    print("=" * 60)
    
    # Run transcription
    transcribe_audio(
        audio_files=valid_files,
        model_name=args.model,
        language=args.language,
        task=args.task,
        output_dir=output_dir,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()
