#!/usr/bin/env python
"""
Quick start script for Grammar Engine
Run tests, start server, verify environment
"""

import sys
import subprocess
from pathlib import Path

def check_environment():
    """Verify environment is set up correctly"""
    print("🔍 Checking environment...\n")
    
    dependencies = {
        'language_tool_python': 'language-tool',
        'spacy': 'spaCy',
        'nltk': 'NLTK',
        'textblob': 'TextBlob',
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
    }
    
    all_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name} - {e}")
            all_ok = False
    
    if all_ok:
        print("\n✅ All dependencies installed!")
    else:
        print("\n⚠️ Missing dependencies. Run:")
        print("   pip install -r requirements.txt")
    
    return all_ok

def download_models():
    """Download required models"""
    print("\n📦 Downloading NLP models...\n")
    
    try:
        import spacy
        try:
            spacy.load("en_core_web_sm")
            print("✅ spaCy model (en_core_web_sm) already installed")
        except OSError:
            print("⏳ Downloading spaCy model...")
            subprocess.run(
                ["python", "-m", "spacy", "download", "en_core_web_sm"],
                check=True
            )
            print("✅ spaCy model downloaded")
    except Exception as e:
        print(f"⚠️ spaCy model download: {e}")
    
    try:
        import nltk
        print("⏳ Downloading NLTK resources...")
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('wordnet', quiet=True)
        print("✅ NLTK resources ready")
    except Exception as e:
        print(f"⚠️ NLTK download: {e}")

def start_server():
    """Start FastAPI server"""
    print("\n🚀 Starting FastAPI server...\n")
    print("📝 API Documentation: http://localhost:8000/docs")
    print("📝 ReDoc: http://localhost:8000/redoc")
    print("💾 Press Ctrl+C to stop\n")
    
    # Use venv uvicorn
    venv_uvicorn = Path(__file__).parent / "venv" / "bin" / "uvicorn"
    subprocess.run(
        [str(venv_uvicorn), "src.grammar_unified_pipeline_minilm:app", "--reload", "--port", "8000"]
    )

def run_tests():
    """Run all tests"""
    print("\n🧪 Running tests...\n")
    result = subprocess.run(
        ["pytest", "tests/", "-v", "--tb=short"],
        cwd=Path(__file__).parent
    )
    return result.returncode == 0

def profile_performance():
    """Profile latency and accuracy"""
    print("\n📊 Profiling performance...\n")
    subprocess.run(["python", "tests/profile_performance.py"])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            check_environment()
        
        elif command == "download":
            download_models()
        
        elif command == "start" or command == "serve":
            if check_environment():
                print()
                start_server()
            else:
                print("⚠️ Fix environment issues first")
        
        elif command == "test":
            if check_environment():
                print()
                success = run_tests()
                sys.exit(0 if success else 1)
            else:
                print("⚠️ Fix environment issues first")
        
        elif command == "profile":
            if check_environment():
                print()
                profile_performance()
            else:
                print("⚠️ Fix environment issues first")
        
        elif command == "setup":
            print("Setting up development environment...\n")
            if check_environment():
                download_models()
                print("\n✅ Setup complete!")
                print("\nNext steps:")
                print("  1. Copy grammar_formatter_classical.py to src/")
                print("  2. Copy tone_transformer.py to src/")
                print("  3. Run: python run.py test")
                print("  4. Run: python run.py start")
            else:
                print("\n⚠️ Fix issues above and try again")
        
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  check      - Verify environment setup")
            print("  download   - Download NLP models")
            print("  setup      - Full initial setup")
            print("  start      - Start FastAPI server")
            print("  test       - Run unit tests")
            print("  profile    - Performance profiling")
    
    else:
        # Default: run setup
        print("Speech Dictation Engine - Grammar Module")
        print("=" * 50 + "\n")
        
        command = input("Choose operation:\n1. setup\n2. start\n3. test\n4. check\n\nEnter number (1-4): ").strip()
        
        if command == "1":
            subprocess.run([sys.executable, __file__, "setup"])
        elif command == "2":
            subprocess.run([sys.executable, __file__, "start"])
        elif command == "3":
            subprocess.run([sys.executable, __file__, "test"])
        elif command == "4":
            subprocess.run([sys.executable, __file__, "check"])
        else:
            print("Invalid choice")
