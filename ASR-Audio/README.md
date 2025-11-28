# 🎙️ ASR-Audio: Complete Whisper AI Transcription System

A comprehensive speech-to-text solution with **both real-time web interface** and **CLI batch processing**, implementing OpenAI's Whisper AI with advanced anti-hallucination features.

## 🌟 Features

### Real-Time Web Transcription
- 🌐 Browser-based audio capture via WebRTC
- ⚡ Live transcription (1.5-second intervals)
- 🎨 Visual audio waveform display
- 🛡️ Anti-hallucination system (lucid threshold)
- 🔄 WebSocket-based streaming
- 🎯 Session tracking and management

### CLI Batch Transcription
- 🎙️ Multi-format support (WAV, MP3, MP4, FLAC, etc.)
- 🌍 96+ language support with auto-detection
- 📦 Batch processing for multiple files
- 🎯 5 model sizes (tiny → large)
- 🔄 Translation to English
- 📝 Three output formats (TXT, SRT, JSON)
- ⚡ GPU acceleration (automatic CUDA)

## 🚀 Quick Start

### Installation
All dependencies are already installed:
```bash
# Already in your environment:
# - Python 3.13.7
# - OpenAI Whisper
# - FastAPI + Uvicorn
# - PyTorch with CUDA
```

### Real-Time Transcription

Start the web server:
```bash
python main.py
```

Open http://localhost:8000 in your browser:
1. Click "Start Recording"
2. Allow microphone access
3. Speak and see transcripts appear every 1.5 seconds

### CLI Transcription

Basic usage:
```bash
# Single file
python cli_transcribe.py audio.wav

# Multiple files
python cli_transcribe.py audio1.wav audio2.mp3 audio3.mp4

# With model selection
python cli_transcribe.py audio.wav --model medium

# Show all options
python cli_transcribe.py --help
```

## 📖 Documentation

| File | Description |
|------|-------------|
| **SUMMARY.md** | Complete project overview |
| **CLI_README.md** | Comprehensive CLI documentation |
| **USAGE_GUIDE.md** | Quick reference guide |
| **examples.sh** | Example commands for all features |

## 🎯 Use Cases

### When to Use Real-Time Server
- Live meetings/interviews
- Real-time captions
- Interactive voice applications
- Testing and development

### When to Use CLI Tool
- Batch processing multiple files
- High-quality offline transcription
- Podcast/video transcription
- Multi-language document creation

## 📝 CLI Quick Examples

### Model Selection
```bash
# Fast (tiny model)
python cli_transcribe.py audio.wav --model tiny

# Balanced (recommended)
python cli_transcribe.py audio.wav --model small

# Best quality
python cli_transcribe.py audio.wav --model large
```

### Language & Translation
```bash
# Specify language
python cli_transcribe.py german.wav --language de

# Translate to English
python cli_transcribe.py german.wav --task translate

# Batch translation
python cli_transcribe.py *.wav --task translate --model medium
```

### Advanced Usage
```bash
# Custom output directory
python cli_transcribe.py audio.wav --output-dir ./transcripts

# Verbose mode
python cli_transcribe.py audio.wav --verbose

# Batch with quality
python cli_transcribe.py recordings/*.wav --model medium --output-dir ./results
```

## 📊 Model Comparison

| Model | Speed | Quality | GPU Memory | Best For |
|-------|-------|---------|------------|----------|
| tiny | Fastest | Low | ~1GB | Quick drafts |
| base | Fast | Decent | ~1GB | General use |
| small | Balanced | Good | ~2GB | **Recommended** |
| medium | Slow | Better | ~5GB | Important work |
| large | Slowest | Best | ~10GB | Critical accuracy |

## 🌍 Language Support

Supports 96+ languages including:
- **en** - English
- **es** - Spanish
- **fr** - French
- **de** - German
- **zh** - Chinese
- **ja** - Japanese
- **ko** - Korean
- **ru** - Russian
- **pt** - Portuguese
- **it** - Italian
- **ar** - Arabic
- **hi** - Hindi

*Full list: `python cli_transcribe.py --help`*

## 📂 Output Files (CLI)

For each audio file, three files are created:

1. **`.txt`** - Plain text transcript
2. **`.srt`** - Subtitle file with timestamps
3. **`.json`** - Structured data with segments

Example:
```bash
python cli_transcribe.py interview.wav

# Creates:
# - interview.txt
# - interview.srt
# - interview.json
```

## 🛠️ Technical Details

### Real-Time Server
- **Framework**: FastAPI with WebSocket
- **Model**: Whisper base.en (English-optimized)
- **Audio**: 16kHz mono, float32
- **Latency**: 1.5 seconds
- **Anti-Hallucination**: Lucid threshold (0.3)

### CLI Tool
- **Models**: All 5 sizes + English-optimized
- **Languages**: 96+ supported
- **Translation**: To English only (current)
- **GPU**: Automatic CUDA acceleration

## 🎓 Implementation Status

### ✅ From Video Tutorial
- Python installation
- PyTorch setup
- FFmpeg integration
- Whisper AI installation
- Model selection (5 models)
- Language detection & specification
- Translation to English
- Output formats (TXT, SRT, JSON)
- Batch processing
- CLI interface

### 🌟 Enhanced Features
- Real-time web interface
- Anti-hallucination system
- English-optimized models (.en)
- Progress previews
- Better error handling
- Audio visualization
- Queue-based architecture
- Session management

## 💡 Best Practices

1. **Start with `small` model** - Good balance
2. **Specify language** - Better accuracy
3. **Use `.en` models for English** - Higher quality
4. **GPU recommended** - 10-20x faster
5. **Review transcripts** - Always verify important ones
6. **Batch when possible** - More efficient

## 🐛 Troubleshooting

### Server Issues
✅ **Tokenizer Error** - Fixed
✅ **WebSocket Disconnects** - Fixed
✅ **Transcripts Not Showing** - Fixed (1.5s interval)

### CLI Issues
- **Out of Memory**: Use smaller model
- **Poor Quality**: Use larger model
- **Slow**: Enable GPU acceleration

## 📚 Example Commands

Run examples script:
```bash
bash examples.sh
```

Or see all examples:
```bash
python cli_transcribe.py --help
```

## 🎯 Real-World Examples

### Transcribe Podcast
```bash
python cli_transcribe.py podcast.mp3 --model medium --output-dir ./podcasts
```

### Multi-Language Meeting
```bash
python cli_transcribe.py \
  intro_en.wav --language en \
  presentation_es.wav --language es \
  qa_de.wav --language de \
  --model medium
```

### Translate Interview
```bash
python cli_transcribe.py japanese_interview.mp4 \
  --task translate \
  --model large \
  --verbose
```

### Batch Process
```bash
python cli_transcribe.py recordings/*.wav \
  --model small \
  --output-dir ./transcripts
```

## 🏗️ Project Structure

```
ASR-Audio/
├── main.py                    # Real-time web server
├── cli_transcribe.py          # CLI transcription tool
├── requirements.txt           # Dependencies
│
├── Documentation/
│   ├── SUMMARY.md             # Project overview
│   ├── CLI_README.md          # CLI guide
│   ├── USAGE_GUIDE.md         # Quick reference
│   └── examples.sh            # Example commands
│
├── asr/                       # Core ASR modules
│   ├── whisper_engine.py      # Whisper with anti-hallucination
│   ├── asr_queue_handler.py   # Queue processing
│   ├── endpoint_queue.py      # WebSocket endpoints
│   └── audio_capture.py       # Audio buffer
│
├── shared/                    # Shared utilities
│   ├── pipeline_message.py    # Message schema
│   └── types.py               # Type definitions
│
└── static/                    # Web client
    └── index.html             # Browser UI
```

## 🎉 Summary

This project provides:
- ✅ **Full CLI tool** matching video tutorial
- ✅ **Enhanced features** beyond tutorial
- ✅ **Real-time web server** for live transcription
- ✅ **Anti-hallucination** for better accuracy
- ✅ **Comprehensive docs** for all features

Both interfaces are fully functional and production-ready!

## 🚀 Get Started Now

### Real-Time:
```bash
python main.py
# Open http://localhost:8000
```

### CLI:
```bash
python cli_transcribe.py audio.wav
```

### Help:
```bash
python cli_transcribe.py --help
bash examples.sh
```

---

**Made with ❤️ using OpenAI Whisper AI**
