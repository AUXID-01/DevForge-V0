#!/bin/bash
# Bash script to install all dependencies for unified pipeline

echo "Installing Unified Pipeline Dependencies..."

# Install unified pipeline requirements
echo -e "\n[1/4] Installing unified_pipeline requirements..."
pip install -r requirements.txt

# Install spaCy model
echo -e "\n[2/4] Installing spaCy English model..."
python -m spacy download en_core_web_sm

# Download NLTK data
echo -e "\n[3/4] Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"

# Install component dependencies
echo -e "\n[4/4] Installing component dependencies..."

# ASR-Audio
if [ -f "../ASR-Audio/requirements.txt" ]; then
    echo "  Installing ASR-Audio dependencies..."
    pip install -r ../ASR-Audio/requirements.txt
fi

# Speech-dictation-engine
if [ -f "../speech-dictation-engine/requirements.txt" ]; then
    echo "  Installing speech-dictation-engine dependencies..."
    pip install -r ../speech-dictation-engine/requirements.txt
fi

# ToneAndOrchestration
if [ -f "../toneAndOrchestration/requirements.txt" ]; then
    echo "  Installing toneAndOrchestration dependencies..."
    pip install -r ../toneAndOrchestration/requirements.txt
fi

echo -e "\n✅ All dependencies installed!"
echo -e "\nNote: If you need PyTorch CPU version, run:"
echo "  pip install torch --index-url https://download.pytorch.org/whl/cpu"

