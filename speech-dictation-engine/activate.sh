#!/bin/bash
# Quick activation script
export VIRTUAL_ENV="/home/vedu/Work/speech-dictation-engine/venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
unset PYTHON_HOME

echo "✅ Virtual environment activated!"
echo "Python: $(which python)"
echo "Pip: $(which pip)"
echo ""
echo "Run commands normally now:"
echo "  python your_script.py"
echo "  pip install package"
echo "  uvicorn src.main_streaming:app --reload"
