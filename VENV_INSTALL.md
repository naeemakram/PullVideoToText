# Virtual Environment Installation Guide

## 🎯 Installing for Your Current Virtual Environment

Since you're already in a virtual environment (as shown by the activated venv), here's how to install all dependencies:

### Step 1: Install Core Requirements
```powershell
# You're already in the virtual environment, so just run:
pip install -r requirements.txt
```

### Step 2: Install Language Models
```powershell
# Download spaCy English model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt')"
```

### Step 3: Verify Installation
```powershell
# Test basic functionality
python -c "import spacy, nltk, sentence_transformers, transformers; print('✅ All packages installed successfully')"
```

### Step 4: Optional - Enable Speaker Diarization
If you want speaker diarization features:
```powershell
# Install audio processing libraries
pip install pyannote-audio==3.1.1 torchaudio>=0.9.0
```

## 🚀 Quick Test

After installation, test with:
```powershell
# Test with existing transcript
python simple_test.py transcription/transcript_B257Ppi129k.en_cleaned.txt

# Or download a new one (basic)
python download_transcript.py "https://www.youtube.com/watch?v=QuCBCCs4weI"
```

## 🔧 Troubleshooting

### If pip install fails:
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Then try again
pip install -r requirements.txt
```

### If you get import errors:
```powershell
# Check what's installed
pip list

# Install missing packages individually
pip install sentence-transformers
pip install transformers
pip install torch
pip install scikit-learn
```

### If spaCy model download fails:
```powershell
# Alternative download method
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0.tar.gz
```

## 📋 What Gets Installed

**Core AI Libraries:**
- `sentence-transformers` - For semantic similarity
- `transformers` - For text generation and summarization  
- `torch` - PyTorch for AI models
- `scikit-learn` - For clustering algorithms
- `spacy` - For natural language processing

**Text Processing:**
- `nltk` - Natural language toolkit
- `rich` - Beautiful terminal output
- `webvtt-py` - VTT file processing

**Optional Audio:**
- `pyannote-audio` - Speaker diarization
- `torchaudio` - Audio processing

## 💾 Disk Space Requirements

- **Base installation**: ~2-3 GB
- **With audio processing**: ~4-5 GB
- **AI models cache**: ~1-2 GB (downloaded on first use)

Total: ~5-8 GB depending on features enabled

## ⚡ Installation Commands (All-in-One)

Run these commands in order in your activated virtual environment:

```powershell
# 1. Install all Python packages
pip install -r requirements.txt

# 2. Download language models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt')"

# 3. Test installation
python -c "
try:
    import spacy, nltk, sentence_transformers, transformers
    print('✅ All packages installed successfully!')
    print('🚀 Ready to process transcripts with AI!')
except ImportError as e:
    print(f'❌ Missing package: {e}')
"

# 4. Optional: Enable audio processing
# pip install pyannote-audio==3.1.1 torchaudio>=0.9.0
```

## 🎯 Verify Your Environment

Check your virtual environment status:
```powershell
# Should show your venv path
where python

# Should show packages are installed in venv
pip list | findstr sentence-transformers
```

---

**Your virtual environment will be completely self-contained with all AI processing capabilities! 🚀**