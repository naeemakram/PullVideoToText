# Advanced Transcript Processing Setup Guide

This guide explains how to set up and use the advanced transcript processing features for the PullVideoToText project.

## Features

The advanced processing system provides:

1. **Text Deduplication**: Removes repetitive content common in auto-generated captions
2. **Semantic Paragraph Segmentation**: Groups sentences into coherent paragraphs using AI
3. **Automatic Heading Generation**: Creates descriptive headings for each paragraph
4. **Speaker Diarization** (optional): Identifies different speakers when audio file is available
5. **Rich Markdown Output**: Well-structured document with sections and metadata

## Installation

### Step 1: Install Basic Requirements

```bash
pip install -r requirements.txt
```

### Step 2: Download Required Language Models

```bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# Download NLTK data
python -m nltk.downloader punkt
```

### Step 3: Optional - Enable Speaker Diarization

If you want speaker diarization features, uncomment the pyannote-audio lines in `requirements.txt` and install:

```bash
pip install pyannote-audio==3.1.1 torchaudio>=0.9.0
```

**Note**: Speaker diarization requires:
- Accepting Hugging Face terms for pyannote models
- An audio file (not just transcript text)
- Additional computational resources

## Usage

### Basic Usage (Original Functionality)

```bash
python download_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This creates:
- `transcript_VIDEO_ID.en.vtt` - Original VTT file
- `transcript_VIDEO_ID.en_cleaned.txt` - Cleaned text transcript

### Advanced Processing

```bash
python download_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" --advanced
```

This creates all the above files PLUS:
- `transcript_VIDEO_ID.en_cleaned_advanced.md` - Enhanced markdown with paragraphs and headings

### Advanced Processing with Speaker Diarization

```bash
python download_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" --advanced --audio-file "path/to/audio.wav"
```

This includes speaker identification in the output.

### Processing Existing Transcripts

You can also process existing cleaned transcript files directly:

```bash
python advanced_processor.py transcript_file_cleaned.txt
```

Options:
- `-o output.md` - Specify output file
- `-a audio.wav` - Add speaker diarization
- `--max-sentences 5` - Control paragraph size

## Example Output

### Before (Original Cleaned Text)
```
Let me guess, you've got 47 browser tabs Let me guess, you've got 47 browser tabs open right now, three different open right now, three different note-taking apps...
```

### After (Advanced Processing)
```markdown
# Advanced Processed Transcript

## The Modern Digital Overwhelm Problem

Let me guess, you've got 47 browser tabs open right now, three different note-taking apps, and a 5-year plan that you've revised every month for the past 5 years. Sound familiar?

---

## Intelligence as a Barrier to Success  

Here's the thing nobody talks about. Being smart might actually be the reason you're not successful. I know that sounds insane. You've been told your whole life that intelligence is your greatest asset.

---
```

## Advanced Features Explained

### 1. Text Deduplication
- Removes exact duplicate sentences
- Uses semantic similarity to catch near-duplicates
- Preserves original meaning while reducing repetition

### 2. Paragraph Segmentation
- Uses sentence embeddings to group related content
- Applies K-means clustering for coherent paragraphs
- Maintains chronological flow of the original transcript

### 3. Heading Generation
- Multiple AI approaches for best results:
  - Key phrase extraction using spaCy
  - Neural text generation with FLAN-T5
  - Named entity recognition
  - Extractive summarization fallbacks

### 4. Speaker Diarization (Optional)
- Requires original audio file
- Uses pyannote.audio for speaker identification  
- Provides timing information for each segment
- Labels speakers as "Speaker_0", "Speaker_1", etc.

## Troubleshooting

### Common Issues

**ImportError for advanced_processor**
- Run: `pip install -r requirements.txt`
- Ensure all models are downloaded

**spaCy model not found**
- Run: `python -m spacy download en_core_web_sm`

**Out of memory errors**
- Reduce `max_sentences_per_paragraph` parameter
- Process shorter transcript files
- Use CPU-only mode (default)

**Diarization not working**
- Ensure pyannote-audio is installed
- Accept Hugging Face Hub terms for pyannote models
- Provide valid audio file path

### Performance Notes

- First run downloads AI models (~1-2 GB)
- Processing time: 30-60 seconds for typical video transcript
- Memory usage: 2-4 GB during processing
- Models are cached after first download

## File Structure

After processing, you'll have:

```
transcript_VIDEO_ID.en.vtt              # Original VTT with timestamps
transcript_VIDEO_ID.en_cleaned.txt      # Basic cleaned text  
transcript_VIDEO_ID.en_cleaned_advanced.md  # Enhanced markdown
models/                                 # Cached AI models
```

## Customization

The `AdvancedTranscriptProcessor` class can be customized:

```python
from advanced_processor import AdvancedTranscriptProcessor

processor = AdvancedTranscriptProcessor(model_cache_dir="./custom_models")
segments = processor.process_text_only(transcript_text)

# Adjust paragraph size
paragraphs = processor.segment_into_paragraphs(text, max_sentences_per_paragraph=3)

# Generate custom headings
heading = processor.generate_heading("Your paragraph text here")
```

## API Reference

See docstrings in `advanced_processor.py` for detailed API documentation of all classes and methods.