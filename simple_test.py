#!/usr/bin/env python3
"""
Simple test script for the advanced transcript processing features.
This demonstrates the functionality without requiring all heavy AI models.
"""

import os
import re
from collections import Counter

def simple_clean_repetitive_text(text):
    """Simple version of text deduplication without AI models."""
    sentences = text.split('. ')
    
    # Remove exact duplicates
    seen = set()
    unique_sentences = []
    for sentence in sentences:
        sentence_clean = sentence.strip().lower()
        if sentence_clean and sentence_clean not in seen and len(sentence_clean) > 10:
            seen.add(sentence_clean)
            unique_sentences.append(sentence.strip())
    
    return '. '.join(unique_sentences)

def simple_paragraph_segmentation(text, sentences_per_paragraph=4):
    """Simple paragraph segmentation by sentence count."""
    sentences = text.split('. ')
    paragraphs = []
    
    for i in range(0, len(sentences), sentences_per_paragraph):
        paragraph = '. '.join(sentences[i:i + sentences_per_paragraph])
        if paragraph.strip():
            paragraphs.append(paragraph.strip())
    
    return paragraphs

def simple_heading_generation(paragraph):
    """Simple heading generation using keyword extraction."""
    words = re.findall(r'\b[A-Z][a-z]+\b', paragraph)  # Find capitalized words
    
    # Remove common words
    common_words = {'The', 'And', 'But', 'You', 'Your', 'This', 'That', 'They', 'Here', 'There'}
    keywords = [word for word in words if word not in common_words]
    
    if keywords:
        # Take most frequent keywords, limit to 4 words
        word_counts = Counter(keywords)
        top_words = [word for word, count in word_counts.most_common(4)]
        return ' '.join(top_words[:3])
    
    # Fallback to first few words
    first_words = paragraph.split()[:4]
    return ' '.join([word.capitalize() for word in first_words if word.isalpha()])

def process_transcript_simple(input_file, output_file=None):
    """Process transcript with simple methods."""
    print(f"🚀 Starting simple advanced processing of: {input_file}")
    
    # Read input
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    print(f"📄 Read {len(text)} characters")
    
    # Clean repetitive text
    print("🧹 Cleaning repetitive content...")
    cleaned_text = simple_clean_repetitive_text(text)
    print(f"✨ Reduced from {len(text)} to {len(cleaned_text)} characters")
    
    # Segment into paragraphs
    print("📝 Segmenting into paragraphs...")
    paragraphs = simple_paragraph_segmentation(cleaned_text)
    print(f"📊 Created {len(paragraphs)} paragraphs")
    
    # Generate headings
    print("🏷️ Generating headings...")
    segments = []
    for i, paragraph in enumerate(paragraphs, 1):
        heading = simple_heading_generation(paragraph)
        segments.append({
            'heading': heading or f"Section {i}",
            'text': paragraph
        })
    
    # Determine output file and create transcription folder
    if not output_file:
        # Create transcription folder
        current_dir = os.path.dirname(os.path.abspath(input_file))
        transcription_dir = os.path.join(current_dir, 'transcription')
        os.makedirs(transcription_dir, exist_ok=True)
        
        # Generate output filename in transcription folder
        input_basename = os.path.basename(input_file)
        base_name = os.path.splitext(input_basename)[0]
        output_file = os.path.join(transcription_dir, f"{base_name}_simple_advanced.md")
    
    # Save results
    print(f"💾 Saving to transcription folder: {os.path.basename(output_file)}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Simple Advanced Processed Transcript\n\n")
            f.write("*Processed with Simple Advanced Processor (No AI models required)*\n\n")
            f.write("---\n\n")
            
            for i, segment in enumerate(segments, 1):
                f.write(f"## {segment['heading']}\n\n")
                f.write(f"{segment['text']}\n\n")
                if i < len(segments):
                    f.write("---\n\n")
        
        print(f"✅ Processing complete!")
        print(f"📁 Output saved: {output_file}")
        print(f"📊 Generated {len(segments)} sections with headings")
        
        # Show preview
        print("\n🔍 Preview of first section:")
        print(f"**Heading:** {segments[0]['heading']}")
        print(f"**Text:** {segments[0]['text'][:150]}...")
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python simple_test.py <input_transcript_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    process_transcript_simple(input_file)