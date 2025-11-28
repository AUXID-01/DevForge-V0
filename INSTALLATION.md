# Installation Guide

## Platform-Specific Notes

### Windows Installation

On Windows, some NVIDIA CUDA packages are not available. The requirements files have been updated to exclude these platform-specific packages.

**Important:** PyTorch will automatically install the correct dependencies based on your platform.

### Installation Steps

1. **Install unified pipeline dependencies:**
   ```bash
   cd unified_pipeline
   pip install -r requirements.txt
   ```

2. **Install component dependencies:**

   For **ASR-Audio**:
   ```bash
   cd ../ASR-Audio
   pip install -r requirements.txt
   ```

   For **speech-dictation-engine** (Grammar):
   ```bash
   cd ../speech-dictation-engine
   pip install -r requirements.txt
   ```
   
   **Note:** If you encounter errors with PyTorch on Windows, install CPU version:
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

   For **toneAndOrchestration**:
   ```bash
   cd ../toneAndOrchestration
   pip install -r requirements.txt
   ```

   For **DEvf** (Disfluency):
   ```bash
   cd ../DEvf
   # Check if requirements.txt exists, or install manually:
   pip install spacy nltk
   ```

3. **Install spaCy model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Troubleshooting

### Error: nvidia-cufile-cu12 not found
- **Solution:** This package is Linux-only. It has been removed from requirements.txt. PyTorch will handle CUDA dependencies automatically.

### Error: triton not found
- **Solution:** Triton is Linux-only and optional. It has been commented out in requirements.txt.

### PyTorch Installation Issues
- **Windows CPU:** `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- **Windows CUDA:** `pip install torch --index-url https://download.pytorch.org/whl/cu121`
- **Linux:** PyTorch will install CUDA dependencies automatically if CUDA is available

### Python Version
- Recommended: Python 3.10 or 3.11
- Python 3.13 may have compatibility issues with some packages

## Quick Install (All Components)

```bash
# From project root
pip install -r unified_pipeline/requirements.txt
pip install -r ASR-Audio/requirements.txt
pip install -r speech-dictation-engine/requirements.txt
pip install -r toneAndOrchestration/requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm
```

