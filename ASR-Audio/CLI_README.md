# Whisper AI CLI Transcription Tool

A command-line interface for transcribing audio files using OpenAI's Whisper AI. Supports 96+ languages, batch processing, multiple output formats, and translation to English.

## Features

- 🎙️ **Multi-format Support**: WAV, MP3, MP4, FLAC, and more
- 🌍 **96+ Languages**: Auto-detect or specify language manually
- 📦 **Batch Processing**: Transcribe multiple files at once
- 🎯 **Model Selection**: Choose from 5 model sizes (tiny to large)
- 📝 **Multiple Outputs**: TXT, SRT (subtitles), and JSON formats
- 🔄 **Translation**: Translate any language to English
- ⚡ **GPU Acceleration**: Automatic CUDA support if available

## Installation

The CLI tool is already set up in your environment. All dependencies are installed.

## Quick Start

### Basic Usage

Transcribe a single audio file:
```bash
python cli_transcribe.py audio.wav
```

Transcribe multiple files:
```bash
python cli_transcribe.py audio1.wav audio2.mp3 audio3.mp4
```

### Model Selection

Choose different model sizes for quality vs speed trade-offs:

```bash
# Fast, lower quality (default: small)
python cli_transcribe.py audio.wav --model tiny

# Balanced (recommended)
python cli_transcribe.py audio.wav --model small

# Better quality
python cli_transcribe.py audio.wav --model medium

# Best quality (requires more GPU memory)
python cli_transcribe.py audio.wav --model large
```

**Model Comparison:**

| Model  | Speed    | Quality | VRAM     |
|--------|----------|---------|----------|
| tiny   | Fastest  | Low     | ~1GB     |
| base   | Fast     | Decent  | ~1GB     |
| small  | Balanced | Good    | ~2GB     |
| medium | Slow     | Better  | ~5GB     |
| large  | Slowest  | Best    | ~10GB    |

### Language Specification

Auto-detect language (default):
```bash
python cli_transcribe.py audio.wav
```

Specify language manually for better accuracy:
```bash
python cli_transcribe.py german.wav --language de
python cli_transcribe.py spanish.wav --language es
python cli_transcribe.py japanese.wav --language ja
```

**Common Language Codes:**
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean
- `ru` - Russian
- `ar` - Arabic
- `hi` - Hindi

### Translation

Translate foreign language audio to English:
```bash
python cli_transcribe.py german.wav --task translate
python cli_transcribe.py french.mp3 --task translate
```

**Note:** Translation currently only supports output in English.

### Output Directory

Save transcriptions to a specific folder:
```bash
python cli_transcribe.py audio.wav --output-dir ./transcripts
```

### Verbose Mode

Show detailed transcription progress:
```bash
python cli_transcribe.py audio.wav --verbose
```

## Output Files

For each audio file, the tool creates three output files:

### 1. TXT File (Plain Text)
```
This is the transcribed text without timestamps.
Perfect for reading or text analysis.
```

### 2. SRT File (Subtitles)
```srt
1
00:00:00,000 --> 00:00:03,500
This is the first subtitle segment.

2
00:00:03,500 --> 00:00:07,200
This is the second subtitle segment.
```

### 3. JSON File (Structured Data)
```json
{
  "text": "Full transcript text...",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "This is the first segment.",
      "tokens": [...],
      "temperature": 0.0,
      "avg_logprob": -0.25
    }
  ],
  "language": "en"
}
```

## Advanced Examples

### Batch process all WAV files in a directory
```bash
python cli_transcribe.py *.wav --model medium
```

### Transcribe with specific language and save to folder
```bash
python cli_transcribe.py meeting.mp3 --language en --model medium --output-dir ./meetings
```

### Translate multiple foreign files to English
```bash
python cli_transcribe.py german1.wav german2.wav --task translate --model large
```

### High-quality transcription with progress details
```bash
python cli_transcribe.py interview.mp4 --model large --verbose
```

## Command Reference

```bash
python cli_transcribe.py [OPTIONS] AUDIO_FILES...
```

**Positional Arguments:**
- `AUDIO_FILES`: One or more audio files to transcribe

**Options:**
- `--model {tiny,base,small,medium,large}`: Model size (default: small)
- `--language LANG`: Language code (auto-detect if not specified)
- `--task {transcribe,translate}`: Task to perform (default: transcribe)
- `--output-dir DIR`: Output directory for files
- `--verbose`: Show detailed progress
- `--version`: Show version information
- `--help`: Show help message

## Tips & Best Practices

1. **Start with the small model** - Good balance of speed and quality
2. **Specify language** - Manual language specification improves accuracy
3. **Use larger models for important transcripts** - Worth the extra time
4. **Review while listening** - Always verify critical transcripts
5. **GPU recommended** - 10x faster than CPU processing
6. **Batch processing** - More efficient for multiple files

## Troubleshooting

### Out of Memory Error
- Use a smaller model (tiny or base)
- Process fewer files at once
- Close other GPU applications

### Poor Transcription Quality
- Try a larger model (medium or large)
- Specify the language manually
- Check audio quality (clear speech, low noise)

### Slow Processing
- Use GPU acceleration (install CUDA)
- Use smaller model (tiny or base)
- Reduce audio length

## Real-Time Transcription

For real-time transcription with a web interface, use the main server:
```bash
python main.py
```
Then open http://localhost:8000 in your browser.

## Examples Output

```bash
$ python cli_transcribe.py sample.wav --model small

============================================================
Whisper AI CLI Transcription Tool
============================================================
Model: small
Task: transcribe
Files: 1
============================================================

🔄 Loading Whisper 'small' model...
✓ Model loaded successfully

[1/1] Processing: sample.wav
  Language: Auto-detect
  🎙️  Transcribing...
  ✓ Detected language: en
  ✓ Created: sample.txt
  ✓ Created: sample.srt
  ✓ Created: sample.json
  📝 Preview: This is a sample audio transcription demonstrating the Whisper AI...

✅ Completed processing 1 file(s)
```

## License

Uses OpenAI's Whisper AI (MIT License)
