#!/usr/bin/env python3
"""
Script to download and clean video transcripts using yt-dlp.
Takes a video URL as a command line argument, downloads the auto-generated subtitles
in VTT format, and automatically cleans them by removing timestamps and metadata,
producing a clean text file with just the transcript content.

Enhanced with advanced processing features:
- Text deduplication and cleaning
- Paragraph segmentation
- Automatic heading generation
- Optional speaker diarization
"""

import sys
import argparse
import subprocess
import os
import re
from urllib.parse import urlparse
import glob

# Import advanced processor if available
try:
    from advanced_processor import AdvancedTranscriptProcessor
    ADVANCED_PROCESSING_AVAILABLE = True
except ImportError:
    ADVANCED_PROCESSING_AVAILABLE = False
    print("ℹ️ Advanced processing not available. Install required packages for enhanced features.")


def clean_vtt_file(vtt_file_path):
    """
    Clean VTT file by removing timestamps, metadata, and formatting,
    keeping only the transcript text. Creates a separate cleaned file,
    leaving the original VTT file completely unchanged.
    
    Args:
        vtt_file_path (str): Path to the original VTT file to read from
        
    Returns:
        str: Path to the newly created cleaned text file
    """
    try:
        with open(vtt_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split content into lines
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip VTT header
            if line.startswith('WEBVTT'):
                continue
                
            # Skip metadata lines (Kind, Language, etc.)
            if line.startswith(('Kind:', 'Language:', 'NOTE')):
                continue
                
            # Skip timestamp lines (format: 00:00:00.000 --> 00:00:00.000)
            if re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}', line):
                continue
                
            # Skip cue settings (position, align, etc.)
            if re.match(r'^.*\s+(position|align|line|size):', line):
                continue
                
            # Skip HTML-like tags and clean the text
            cleaned_line = re.sub(r'<[^>]+>', '', line)  # Remove HTML tags
            cleaned_line = re.sub(r'&[a-zA-Z]+;', '', cleaned_line)  # Remove HTML entities
            cleaned_line = cleaned_line.strip()
            
            # Only add non-empty lines that contain actual text
            if cleaned_line and not re.match(r'^\d+$', cleaned_line):  # Skip cue numbers
                cleaned_lines.append(cleaned_line)
        
        # Join lines with spaces and clean up extra whitespace
        cleaned_text = ' '.join(cleaned_lines)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with single space
        cleaned_text = cleaned_text.strip()
        
        # Create output filename (replace .vtt with .txt)
        base_name = os.path.splitext(vtt_file_path)[0]
        cleaned_file_path = f"{base_name}_cleaned.txt"
        
        # Write cleaned content to new file
        with open(cleaned_file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_text)
        
        return cleaned_file_path
        
    except Exception as e:
        print(f"❌ Error cleaning VTT file: {e}")
        return None


def sanitize_filename(url):
    """
    Create a suitable filename from the video URL.
    
    Args:
        url (str): The video URL
        
    Returns:
        str: A sanitized filename suitable for the transcript
    """
    # Parse the URL to extract meaningful parts
    parsed = urlparse(url)
    
    # For YouTube URLs, try to extract video ID
    if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
        if 'youtu.be' in parsed.netloc:
            # Short URL format: youtu.be/VIDEO_ID
            video_id = parsed.path.lstrip('/')
        else:
            # Long URL format: youtube.com/watch?v=VIDEO_ID
            query_params = dict(param.split('=') for param in parsed.query.split('&') if '=' in param)
            video_id = query_params.get('v', '')
        
        if video_id:
            # Remove any additional parameters from video ID
            video_id = video_id.split('&')[0].split('?')[0]
            return f"transcript_{video_id}"
    
    # For other URLs, create filename from domain and path
    domain = parsed.netloc.replace('www.', '').replace('.', '_')
    path_parts = [part for part in parsed.path.split('/') if part]
    
    if path_parts:
        filename = f"transcript_{domain}_{path_parts[-1]}"
    else:
        filename = f"transcript_{domain}"
    
    # Remove special characters and limit length
    filename = re.sub(r'[^\w\-_]', '_', filename)
    filename = filename[:50]  # Limit to 50 characters
    
    return filename


def download_transcript(video_url, enable_advanced=False, audio_file_path=None):
    """
    Download transcript using yt-dlp command.
    
    Args:
        video_url (str): The URL of the video to download transcript from
        enable_advanced (bool): Whether to apply advanced processing
        audio_file_path (str): Optional path to audio file for diarization
    """
    try:
        # Get current directory and create transcription folder
        current_dir = os.getcwd()
        transcription_dir = os.path.join(current_dir, 'transcription')
        os.makedirs(transcription_dir, exist_ok=True)
        
        # Create suitable filename
        base_filename = sanitize_filename(video_url)
        output_path = os.path.join(transcription_dir, base_filename)
        
        # Construct the yt-dlp command
        cmd = [
            'yt-dlp_x86',
            '--write-auto-sub',
            '--skip-download',
            '--sub-format', 'vtt',
            '--output', f'{output_path}.%(ext)s',
            video_url
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        print(f"Output will be saved to transcription folder: {output_path}.vtt")
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Transcript downloaded successfully!")
            
            # Find the downloaded VTT file(s)
            vtt_files = glob.glob(f"{output_path}*.vtt")
            
            if vtt_files:
                print(f"📄 Original VTT file(s) in transcription folder: {', '.join(os.path.basename(f) for f in vtt_files)}")
                
                # Clean each VTT file and save to separate cleaned file
                for vtt_file in vtt_files:
                    print(f"🧹 Processing VTT file: {os.path.basename(vtt_file)}")
                    cleaned_file = clean_vtt_file(vtt_file)
                    
                    if cleaned_file:
                        print(f"✨ Cleaned transcript saved: {os.path.basename(cleaned_file)}")
                        print(f"📋 Original VTT file unchanged: {os.path.basename(vtt_file)}")
                        
                        # Apply advanced processing if requested
                        if enable_advanced and ADVANCED_PROCESSING_AVAILABLE:
                            try:
                                print("🚀 Starting advanced processing...")
                                processor = AdvancedTranscriptProcessor()
                                
                                # Read cleaned text
                                with open(cleaned_file, 'r', encoding='utf-8') as f:
                                    transcript_text = f.read()
                                
                                # Process with or without audio
                                if audio_file_path and os.path.exists(audio_file_path):
                                    print(f"🎤 Processing with audio diarization: {audio_file_path}")
                                    segments = processor.process_with_audio_diarization(audio_file_path, transcript_text)
                                else:
                                    print("📝 Processing text without diarization")
                                    segments = processor.process_text_only(transcript_text)
                                
                                # Save advanced processed version
                                base_name = os.path.splitext(cleaned_file)[0]
                                advanced_file = f"{base_name}_advanced.md"
                                processor.save_processed_transcript(segments, advanced_file)
                                
                                print(f"🎉 Advanced processing complete!")
                                print(f"📊 Generated {len(segments)} segments with headings")
                                print(f"📁 Advanced transcript: {os.path.basename(advanced_file)}")
                                print(f"📂 All files saved to: transcription/ folder")
                                
                                # Check for speakers
                                speakers = set(s.speaker for s in segments if s.speaker)
                                if speakers:
                                    print(f"🎤 Detected {len(speakers)} speakers: {', '.join(speakers)}")
                                
                            except Exception as e:
                                print(f"❌ Advanced processing failed: {e}")
                                print("📋 Basic cleaned transcript is still available.")
                        
                        elif enable_advanced:
                            print("⚠️ Advanced processing requested but not available. Install required packages.")
                    else:
                        print(f"❌ Failed to create cleaned version of: {vtt_file}")
            else:
                print(f"⚠️  No VTT files found matching pattern: {output_path}*.vtt")
            
            if result.stdout:
                print("\nyt-dlp Output:")
                print(result.stdout)
        else:
            print("❌ Error occurred while downloading transcript:")
            print(f"Exit code: {result.returncode}")
            if result.stderr:
                print("Error details:")
                print(result.stderr)
            if result.stdout:
                print("Output:")
                print(result.stdout)
            sys.exit(1)
            
    except FileNotFoundError:
        print("❌ Error: yt-dlp command not found.", file=sys.stderr)
        print("Please make sure yt-dlp is installed and available in your PATH.", file=sys.stderr)
        print("Install with: pip install yt-dlp", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to handle command line arguments and download transcript."""
    parser = argparse.ArgumentParser(
        description='Download and clean video transcripts using yt-dlp with optional advanced processing.',
        epilog='Example: python download_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --advanced\n'
               'This will create both a .vtt file, a cleaned .txt file, and an advanced .md file.'
    )
    parser.add_argument(
        'video_url',
        help='URL of the video to download transcript from'
    )
    parser.add_argument(
        '--advanced', 
        action='store_true', 
        help='Enable advanced processing (paragraph segmentation, heading generation)'
    )
    parser.add_argument(
        '--audio-file',
        help='Path to audio file for speaker diarization (requires advanced processing)'
    )
    
    args = parser.parse_args()
    
    # Validate URL format
    if not (args.video_url.startswith('http://') or args.video_url.startswith('https://')):
        print("❌ Error: Please provide a valid URL starting with http:// or https://", file=sys.stderr)
        sys.exit(1)
    
    # Check advanced processing requirements
    if args.advanced and not ADVANCED_PROCESSING_AVAILABLE:
        print("❌ Error: Advanced processing requested but required packages not available.")
        print("Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    if args.audio_file and not args.advanced:
        print("⚠️ Audio file specified but advanced processing not enabled. Use --advanced flag.")
    
    download_transcript(args.video_url, args.advanced, args.audio_file)


if __name__ == '__main__':
    main()