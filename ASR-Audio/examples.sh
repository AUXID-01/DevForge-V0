#!/bin/bash

# Whisper AI CLI - Example Usage Script
# This script demonstrates all the features of the CLI tool

echo "=========================================="
echo "Whisper AI CLI - Example Usage"
echo "=========================================="
echo ""

# Setup
PYTHON="/home/vedu/Work/ASR-Audio/.venv/bin/python"
CLI="cli_transcribe.py"

echo "📋 Available Commands:"
echo ""

# 1. Show help
echo "1. Show help and all options:"
echo "   $PYTHON $CLI --help"
echo ""

# 2. Basic transcription
echo "2. Transcribe single audio file:"
echo "   $PYTHON $CLI audio.wav"
echo ""

# 3. Multiple files
echo "3. Transcribe multiple files at once:"
echo "   $PYTHON $CLI audio1.wav audio2.mp3 audio3.mp4"
echo ""

# 4. Model selection
echo "4. Use different models:"
echo "   $PYTHON $CLI audio.wav --model tiny      # Fastest"
echo "   $PYTHON $CLI audio.wav --model base      # Fast"
echo "   $PYTHON $CLI audio.wav --model small     # Balanced (default)"
echo "   $PYTHON $CLI audio.wav --model medium    # Better quality"
echo "   $PYTHON $CLI audio.wav --model large     # Best quality"
echo ""

# 5. English-optimized
echo "5. English-optimized models (better for English):"
echo "   $PYTHON $CLI audio.wav --model base.en"
echo "   $PYTHON $CLI audio.wav --model small.en"
echo "   $PYTHON $CLI audio.wav --model medium.en"
echo ""

# 6. Language specification
echo "6. Specify language manually:"
echo "   $PYTHON $CLI german.wav --language de    # German"
echo "   $PYTHON $CLI spanish.wav --language es   # Spanish"
echo "   $PYTHON $CLI french.wav --language fr    # French"
echo "   $PYTHON $CLI japanese.wav --language ja  # Japanese"
echo ""

# 7. Translation
echo "7. Translate to English:"
echo "   $PYTHON $CLI german.wav --task translate"
echo "   $PYTHON $CLI french.mp3 --task translate --model medium"
echo ""

# 8. Output directory
echo "8. Save to specific directory:"
echo "   $PYTHON $CLI audio.wav --output-dir ./transcripts"
echo "   $PYTHON $CLI *.wav --output-dir ./batch_results"
echo ""

# 9. Verbose mode
echo "9. Show detailed progress:"
echo "   $PYTHON $CLI audio.wav --verbose"
echo "   $PYTHON $CLI audio.wav --model large --verbose"
echo ""

# 10. Batch processing
echo "10. Batch process multiple files:"
echo "    $PYTHON $CLI recordings/*.wav --model small"
echo "    $PYTHON $CLI podcast_*.mp3 --model medium --output-dir ./podcasts"
echo ""

# 11. Real-world examples
echo "11. Real-world usage examples:"
echo ""
echo "    a) Transcribe interview with high quality:"
echo "       $PYTHON $CLI interview.mp4 --model large --verbose"
echo ""
echo "    b) Translate foreign language meeting:"
echo "       $PYTHON $CLI meeting_german.wav --task translate --model medium"
echo ""
echo "    c) Batch process all recordings:"
echo "       $PYTHON $CLI recordings/*.wav --model small --output-dir ./transcripts"
echo ""
echo "    d) Multi-language conference transcription:"
echo "       $PYTHON $CLI session1_en.wav --language en \\"
echo "                        session2_es.wav --language es \\"
echo "                        session3_fr.wav --language fr \\"
echo "                        --model medium --output-dir ./conference"
echo ""

# 12. Output files
echo "12. Output files created for each audio file:"
echo "    - filename.txt   (plain text transcript)"
echo "    - filename.srt   (subtitle file with timestamps)"
echo "    - filename.json  (structured data with segments)"
echo ""

# 13. Model sizes
echo "13. Model size comparison:"
echo "    +--------+----------+---------+-----------+------------------+"
echo "    | Model  | Speed    | Quality | GPU Memory| Use Case         |"
echo "    +--------+----------+---------+-----------+------------------+"
echo "    | tiny   | Fastest  | Low     | ~1GB      | Quick drafts     |"
echo "    | base   | Fast     | Decent  | ~1GB      | General use      |"
echo "    | small  | Balanced | Good    | ~2GB      | Recommended      |"
echo "    | medium | Slow     | Better  | ~5GB      | Important work   |"
echo "    | large  | Slowest  | Best    | ~10GB     | Critical accuracy|"
echo "    +--------+----------+---------+-----------+------------------+"
echo ""

# 14. Common language codes
echo "14. Common language codes:"
echo "    en=English, es=Spanish, fr=French, de=German, zh=Chinese,"
echo "    ja=Japanese, ko=Korean, ru=Russian, pt=Portuguese, it=Italian,"
echo "    ar=Arabic, hi=Hindi, tr=Turkish, pl=Polish, nl=Dutch"
echo ""
echo "    Full list: python $CLI --help"
echo ""

echo "=========================================="
echo "✅ For complete documentation, see:"
echo "   - CLI_README.md (comprehensive guide)"
echo "   - USAGE_GUIDE.md (quick reference)"
echo "   - SUMMARY.md (project overview)"
echo "=========================================="
echo ""

echo "🚀 Quick Start:"
echo "   1. python $CLI --help           # Show all options"
echo "   2. python $CLI audio.wav         # Basic transcription"
echo "   3. python $CLI audio.wav --model medium  # Better quality"
echo ""

echo "🌐 Real-Time Server:"
echo "   python main.py                   # Start web server"
echo "   Open: http://localhost:8000      # Browser interface"
echo ""
