# PullVideoToText - Enhanced with AI Processing

Transform video transcripts into professional, structured documents with advanced AI processing capabilities.

## 🚀 Features

### Core Functionality
- **Video Transcript Download**: Extract transcripts from YouTube and other video platforms
- **Text Cleaning**: Remove timestamps, metadata, and formatting artifacts
- **Advanced AI Processing**: Transform repetitive auto-captions into structured content

### Advanced Processing Features
- **Intelligent Deduplication**: Remove repetitive content using semantic similarity
- **Smart Paragraph Segmentation**: Group related sentences using AI clustering
- **Automatic Heading Generation**: Create descriptive headings for each section
- **Speaker Diarization**: Identify different speakers (when audio available)
- **Professional Output**: Generate well-formatted Markdown documents

## 📁 File Organization

All transcript files are organized in a dedicated `transcription/` folder:

```
your-project/
├── download_transcript.py          # Main download script
├── advanced_processor.py           # AI processing engine
├── requirements.txt                # Dependencies
├── transcription/                  # 📂 All transcript files here
│   ├── transcript_VIDEO_ID.en.vtt
│   ├── transcript_VIDEO_ID.en_cleaned.txt
│   └── transcript_VIDEO_ID.en_cleaned_advanced.md
└── models/                        # AI models cache (auto-created)
```

## 🎯 Quick Start

### Basic Transcript Download
```bash
python download_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Enhanced Processing with AI
```bash
python download_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" --advanced
```

### Process Existing Files
```bash
python advanced_processor.py transcription/existing_transcript.txt
```

## 📋 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/naeemakram/PullVideoToText.git
   cd PullVideoToText
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download language models**
   ```bash
   python -m spacy download en_core_web_sm
   python -m nltk.downloader punkt
   ```

4. **Optional: Enable speaker diarization**
   ```bash
   # Uncomment pyannote-audio in requirements.txt, then:
   pip install pyannote-audio
   ```

## 📖 Usage Examples

### Transform Repetitive Auto-Captions

**Before (Raw Auto-Generated):**
```
Let me guess, you've got 47 browser tabs Let me guess, you've got 47 browser tabs open right now, three different open right now, three different note-taking apps...
```

**After (AI Enhanced):**
```markdown
## The Modern Digital Overwhelm Problem

Let me guess, you've got 47 browser tabs open right now, three different note-taking apps, and a 5-year plan that you've revised every month for the past 5 years.

---

## Intelligence as a Barrier to Success

Here's the thing nobody talks about. Being smart might actually be the reason you're not successful...
```

## 🛠️ Command Options

### download_transcript.py
```bash
python download_transcript.py URL [--advanced] [--audio-file PATH]
```
- `--advanced`: Enable AI processing features
- `--audio-file`: Path to audio file for speaker diarization

### advanced_processor.py
```bash
python advanced_processor.py INPUT_FILE [-o OUTPUT] [-a AUDIO] [--max-sentences N]
```
- `-o`: Custom output file path
- `-a`: Audio file for diarization
- `--max-sentences`: Sentences per paragraph (default: 5)

## 🧠 AI Models Used

- **Sentence Transformers**: Semantic similarity and clustering
- **spaCy**: Natural language processing and entity recognition  
- **BART**: Text summarization for heading generation
- **FLAN-T5**: Neural text generation
- **pyannote-audio**: Speaker diarization (optional)

## 📊 Performance

- **Processing Speed**: 30-60 seconds for typical video transcript
- **Memory Usage**: 2-4 GB during processing
- **Model Size**: ~1-2 GB cached models (downloaded once)
- **Quality**: Significantly improved readability and structure

## 🔧 Advanced Configuration

### Custom Processing
```python
from advanced_processor import AdvancedTranscriptProcessor

processor = AdvancedTranscriptProcessor()
segments = processor.process_text_only(your_text)
```

### Batch Processing
```bash
# Process multiple files
for file in transcription/*.txt; do
    python advanced_processor.py "$file"
done
```

## 📁 Output Formats

- **VTT**: Original subtitle format with timestamps
- **TXT**: Clean text without formatting
- **MD**: Enhanced Markdown with structure and headings

## ⚠️ Requirements

- Python 3.8+
- 2-4 GB RAM for AI processing
- Internet connection for model downloads
- yt-dlp for video transcript extraction

## 📚 Documentation

- `ADVANCED_SETUP.md`: Detailed setup and configuration guide
- `IMPLEMENTATION_SUMMARY.md`: Technical implementation details

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Built with:
- yt-dlp for transcript extraction
- Hugging Face Transformers for AI processing
- spaCy for natural language processing
- pyannote-audio for speaker diarization

---

**Transform your video content into professional documentation with AI! 🚀**