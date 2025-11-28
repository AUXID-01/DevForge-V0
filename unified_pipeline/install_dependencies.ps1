# PowerShell script to install all dependencies for unified pipeline

Write-Host "Installing Unified Pipeline Dependencies..." -ForegroundColor Green

# Install unified pipeline requirements
Write-Host "`n[1/4] Installing unified_pipeline requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install spaCy model
Write-Host "`n[2/4] Installing spaCy English model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm

# Download NLTK data
Write-Host "`n[3/4] Downloading NLTK data..." -ForegroundColor Yellow
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"

# Install component dependencies
Write-Host "`n[4/4] Installing component dependencies..." -ForegroundColor Yellow

# ASR-Audio
if (Test-Path "..\ASR-Audio\requirements.txt") {
    Write-Host "  Installing ASR-Audio dependencies..." -ForegroundColor Cyan
    pip install -r ..\ASR-Audio\requirements.txt
}

# Speech-dictation-engine
if (Test-Path "..\speech-dictation-engine\requirements.txt") {
    Write-Host "  Installing speech-dictation-engine dependencies..." -ForegroundColor Cyan
    pip install -r ..\speech-dictation-engine\requirements.txt
}

# ToneAndOrchestration
if (Test-Path "..\toneAndOrchestration\requirements.txt") {
    Write-Host "  Installing toneAndOrchestration dependencies..." -ForegroundColor Cyan
    pip install -r ..\toneAndOrchestration\requirements.txt
}

Write-Host "`n✅ All dependencies installed!" -ForegroundColor Green
Write-Host "`nNote: If you need PyTorch CPU version on Windows, run:" -ForegroundColor Yellow
Write-Host "  pip install torch --index-url https://download.pytorch.org/whl/cpu" -ForegroundColor Yellow

