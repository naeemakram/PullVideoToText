#!/usr/bin/env python3
"""
Advanced transcript processor for diarization, paragraph segmentation, and heading generation.
Processes cleaned transcript text to create well-structured documents with:
1. Text deduplication and cleaning
2. Paragraph segmentation based on semantic similarity
3. Automatic heading generation for each paragraph
4. Optional speaker diarization (requires audio file)
"""

import os
import re
import sys
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

# Core processing libraries
import spacy
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# Text analysis
import nltk
from nltk.tokenize import sent_tokenize
from collections import Counter

# Optional audio processing for diarization
try:
    from pyannote.audio import Pipeline
    from pyannote.core import Annotation
    DIARIZATION_AVAILABLE = True
except ImportError:
    DIARIZATION_AVAILABLE = False
    print("⚠️ pyannote.audio not available. Diarization features will be disabled.")

# Rich formatting for output
from rich.console import Console
from rich.progress import Progress
from rich import print as rprint

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessedSegment:
    """Represents a processed text segment with metadata."""
    text: str
    heading: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    speaker: Optional[str] = None
    confidence: Optional[float] = None

class AdvancedTranscriptProcessor:
    """Advanced transcript processor with multiple enhancement features."""
    
    def __init__(self, model_cache_dir: str = "./models"):
        """
        Initialize the processor with required models.
        
        Args:
            model_cache_dir: Directory to cache downloaded models
        """
        self.console = Console()
        self.model_cache_dir = model_cache_dir
        os.makedirs(model_cache_dir, exist_ok=True)
        
        # Initialize models
        self._load_models()
    
    def _load_models(self):
        """Load all required models for processing."""
        self.console.print("🚀 Loading AI models for advanced processing...")
        
        try:
            # Load spaCy model for NLP
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.console.print("❌ spaCy model 'en_core_web_sm' not found. Please install with: python -m spacy download en_core_web_sm")
                sys.exit(1)
            
            # Load sentence transformer for semantic similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=self.model_cache_dir)
            
            # Load summarization model for heading generation
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                tokenizer="facebook/bart-large-cnn",
                device=-1  # Use CPU
            )
            
            # Load text generation model for better headings
            self.heading_generator = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                tokenizer="google/flan-t5-base",
                device=-1
            )
            
            # Initialize diarization pipeline if available
            if DIARIZATION_AVAILABLE:
                try:
                    # Note: This requires authentication with Hugging Face Hub
                    # Users need to accept terms for pyannote models
                    self.diarization_pipeline = Pipeline.from_pretrained(
                        "pyannote/speaker-diarization@2.1",
                        cache_dir=self.model_cache_dir
                    )
                except Exception as e:
                    self.console.print(f"⚠️ Diarization pipeline not available: {e}")
                    self.diarization_pipeline = None
            else:
                self.diarization_pipeline = None
            
            self.console.print("✅ All models loaded successfully!")
            
        except Exception as e:
            self.console.print(f"❌ Error loading models: {e}")
            raise
    
    def clean_repetitive_text(self, text: str) -> str:
        """
        Remove repetitive content common in auto-generated transcripts.
        
        Args:
            text: Raw transcript text
            
        Returns:
            Cleaned text with reduced repetition
        """
        # Split into sentences
        sentences = sent_tokenize(text)
        
        # Remove exact duplicates while preserving order
        seen = set()
        unique_sentences = []
        for sentence in sentences:
            sentence_clean = sentence.strip().lower()
            if sentence_clean and sentence_clean not in seen:
                seen.add(sentence_clean)
                unique_sentences.append(sentence.strip())
        
        # Handle near-duplicates (sentences with high similarity)
        if len(unique_sentences) > 1:
            # Get embeddings for all sentences
            embeddings = self.sentence_model.encode(unique_sentences)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(embeddings)
            
            # Remove sentences that are too similar to previous ones
            filtered_sentences = [unique_sentences[0]]  # Always keep the first sentence
            
            for i in range(1, len(unique_sentences)):
                # Check similarity with all previous sentences
                max_similarity = max(similarity_matrix[i][:i])
                
                # Only keep if similarity is below threshold (0.85 = 85% similar)
                if max_similarity < 0.85:
                    filtered_sentences.append(unique_sentences[i])
            
            return ' '.join(filtered_sentences)
        
        return ' '.join(unique_sentences)
    
    def segment_into_paragraphs(self, text: str, max_sentences_per_paragraph: int = 5) -> List[str]:
        """
        Segment text into coherent paragraphs using semantic similarity.
        
        Args:
            text: Input text to segment
            max_sentences_per_paragraph: Maximum sentences per paragraph
            
        Returns:
            List of paragraph strings
        """
        sentences = sent_tokenize(text)
        
        if len(sentences) <= max_sentences_per_paragraph:
            return [text]
        
        # Get sentence embeddings
        embeddings = self.sentence_model.encode(sentences)
        
        # Calculate number of clusters (paragraphs)
        n_clusters = min(len(sentences) // 2, max(2, len(sentences) // max_sentences_per_paragraph))
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(embeddings)
        
        # Group sentences by cluster while preserving order
        paragraphs = [[] for _ in range(n_clusters)]
        cluster_order = {}
        
        for i, (sentence, cluster_id) in enumerate(zip(sentences, clusters)):
            if cluster_id not in cluster_order:
                cluster_order[cluster_id] = i
            paragraphs[cluster_id].append(sentence)
        
        # Sort paragraphs by the order they first appear
        sorted_paragraphs = sorted(paragraphs, key=lambda p: min(sentences.index(s) for s in p))
        
        # Join sentences within each paragraph
        paragraph_texts = []
        for paragraph_sentences in sorted_paragraphs:
            if paragraph_sentences:  # Only add non-empty paragraphs
                paragraph_text = ' '.join(paragraph_sentences)
                paragraph_texts.append(paragraph_text)
        
        return paragraph_texts
    
    def generate_heading(self, paragraph: str) -> str:
        """
        Generate a descriptive heading for a paragraph.
        
        Args:
            paragraph: Text content of the paragraph
            
        Returns:
            Generated heading
        """
        try:
            # Truncate paragraph if too long for the model
            max_length = 500
            if len(paragraph) > max_length:
                paragraph = paragraph[:max_length] + "..."
            
            # Try different approaches for heading generation
            
            # Method 1: Extract key phrases using spaCy
            doc = self.nlp(paragraph)
            key_phrases = []
            
            # Extract noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text) > 3 and chunk.text.lower() not in ['you', 'your', 'they', 'their', 'this', 'that']:
                    key_phrases.append(chunk.text.title())
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'EVENT', 'PRODUCT']:
                    key_phrases.append(ent.text.title())
            
            # Method 2: Use text generation model
            prompt = f"Generate a short, descriptive heading (3-6 words) for this text: {paragraph[:200]}..."
            
            try:
                result = self.heading_generator(
                    prompt,
                    max_length=30,
                    num_return_sequences=1,
                    temperature=0.7
                )
                generated_heading = result[0]['generated_text'].strip()
                
                # Clean up the generated heading
                generated_heading = re.sub(r'^(Heading:|Title:|Summary:)\s*', '', generated_heading, flags=re.IGNORECASE)
                generated_heading = generated_heading.strip('"\'')
                
                if generated_heading and len(generated_heading.split()) <= 8:
                    return generated_heading.title()
            except Exception as e:
                logger.warning(f"Text generation failed: {e}")
            
            # Method 3: Fallback to extractive approach
            if key_phrases:
                # Use most frequent key phrases
                phrase_counts = Counter(key_phrases)
                most_common_phrase = phrase_counts.most_common(1)[0][0]
                return most_common_phrase
            
            # Method 4: Extract first meaningful sentence fragment
            first_sentence = sent_tokenize(paragraph)[0]
            words = first_sentence.split()
            
            # Find key words (nouns, adjectives, verbs)
            key_words = []
            doc = self.nlp(first_sentence)
            for token in doc:
                if token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB'] and len(token.text) > 2:
                    key_words.append(token.text.lower())
            
            if key_words:
                # Take first few key words
                heading_words = key_words[:4]
                return ' '.join(heading_words).title()
            
            # Final fallback
            return "Content Section"
            
        except Exception as e:
            logger.error(f"Error generating heading: {e}")
            return "Content Section"
    
    def process_with_audio_diarization(self, audio_file_path: str, transcript_text: str) -> List[ProcessedSegment]:
        """
        Process transcript with speaker diarization using audio file.
        
        Args:
            audio_file_path: Path to the audio file
            transcript_text: Cleaned transcript text
            
        Returns:
            List of processed segments with speaker information
        """
        if not self.diarization_pipeline:
            self.console.print("⚠️ Diarization not available. Processing without speaker information.")
            return self.process_text_only(transcript_text)
        
        try:
            # Run diarization on audio
            self.console.print("🎤 Running speaker diarization...")
            diarization = self.diarization_pipeline(audio_file_path)
            
            # Process segments with speaker information
            segments = []
            sentences = sent_tokenize(transcript_text)
            
            # Estimate timing for sentences (rough approximation)
            total_duration = max(segment.end for segment in diarization.itersegments())
            time_per_sentence = total_duration / len(sentences)
            
            current_time = 0
            for i, sentence in enumerate(sentences):
                sentence_start = current_time
                sentence_end = current_time + time_per_sentence
                
                # Find overlapping speaker segment
                speaker = "Unknown"
                for segment, _, speaker_label in diarization.itertracks(yield_label=True):
                    if segment.start <= sentence_start <= segment.end:
                        speaker = speaker_label
                        break
                
                segments.append(ProcessedSegment(
                    text=sentence,
                    heading=self.generate_heading(sentence),
                    start_time=sentence_start,
                    end_time=sentence_end,
                    speaker=speaker
                ))
                
                current_time += time_per_sentence
            
            return segments
            
        except Exception as e:
            self.console.print(f"❌ Diarization failed: {e}")
            return self.process_text_only(transcript_text)
    
    def process_text_only(self, transcript_text: str) -> List[ProcessedSegment]:
        """
        Process transcript without audio diarization.
        
        Args:
            transcript_text: Cleaned transcript text
            
        Returns:
            List of processed segments
        """
        # Clean repetitive text
        cleaned_text = self.clean_repetitive_text(transcript_text)
        
        # Segment into paragraphs
        paragraphs = self.segment_into_paragraphs(cleaned_text)
        
        # Generate segments with headings
        segments = []
        for paragraph in paragraphs:
            heading = self.generate_heading(paragraph)
            segments.append(ProcessedSegment(
                text=paragraph,
                heading=heading
            ))
        
        return segments
    
    def save_processed_transcript(self, segments: List[ProcessedSegment], output_path: str):
        """
        Save processed transcript to file with formatting.
        
        Args:
            segments: List of processed segments
            output_path: Path to save the output file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Advanced Processed Transcript\n\n")
                f.write(f"*Processed with Advanced Transcript Processor*\n\n")
                f.write("---\n\n")
                
                for i, segment in enumerate(segments, 1):
                    # Write heading
                    f.write(f"## {segment.heading}\n\n")
                    
                    # Write metadata if available
                    if segment.speaker or segment.start_time is not None:
                        metadata_parts = []
                        if segment.speaker:
                            metadata_parts.append(f"**Speaker:** {segment.speaker}")
                        if segment.start_time is not None:
                            metadata_parts.append(f"**Time:** {segment.start_time:.1f}s - {segment.end_time:.1f}s")
                        
                        if metadata_parts:
                            f.write(f"*{' | '.join(metadata_parts)}*\n\n")
                    
                    # Write content
                    f.write(f"{segment.text}\n\n")
                    
                    # Add separator between sections
                    if i < len(segments):
                        f.write("---\n\n")
            
            self.console.print(f"✅ Advanced processed transcript saved: {output_path}")
            
        except Exception as e:
            self.console.print(f"❌ Error saving processed transcript: {e}")
            raise

def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Advanced transcript processor with diarization, paragraph segmentation, and heading generation."
    )
    parser.add_argument("input_file", help="Input transcript file (cleaned text)")
    parser.add_argument("-o", "--output", help="Output file path (default: saves to transcription folder with '_advanced' suffix)")
    parser.add_argument("-a", "--audio", help="Audio file path for diarization (optional)")
    parser.add_argument("--max-sentences", type=int, default=5, help="Maximum sentences per paragraph")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"❌ Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Create transcription folder if it doesn't exist
        current_dir = os.path.dirname(os.path.abspath(args.input_file))
        transcription_dir = os.path.join(current_dir, 'transcription')
        os.makedirs(transcription_dir, exist_ok=True)
        
        # Generate output filename in transcription folder
        input_basename = os.path.basename(args.input_file)
        base_path = os.path.splitext(input_basename)[0]
        output_path = os.path.join(transcription_dir, f"{base_path}_advanced.md")
    
    # Initialize processor
    processor = AdvancedTranscriptProcessor()
    
    # Read input file
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        sys.exit(1)
    
    # Process transcript
    if args.audio and os.path.exists(args.audio):
        segments = processor.process_with_audio_diarization(args.audio, transcript_text)
    else:
        if args.audio:
            print(f"⚠️ Audio file not found: {args.audio}. Processing without diarization.")
        segments = processor.process_text_only(transcript_text)
    
    # Save results
    processor.save_processed_transcript(segments, output_path)
    
    print(f"🎉 Advanced processing complete!")
    print(f"📊 Generated {len(segments)} segments with headings")
    print(f"📁 Output saved to: {output_path}")
    if any(s.speaker for s in segments):
        speakers = set(s.speaker for s in segments if s.speaker)
        print(f"🎤 Detected {len(speakers)} speakers: {', '.join(speakers)}")

if __name__ == "__main__":
    main()