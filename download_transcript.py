#!/usr/bin/env python3
"""
Script to download and clean video transcripts using yt-dlp.
Takes a video URL as a command line argument, downloads the auto-generated subtitles
in VTT format, and automatically cleans them by removing timestamps and metadata,
producing a clean text file with just the transcript content.
"""

import sys
import argparse
import subprocess
import os
import re
from urllib.parse import urlparse
import glob


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


def download_transcript(video_url):
    """
    Download transcript using yt-dlp command.
    
    Args:
        video_url (str): The URL of the video to download transcript from
    """
    try:
        # Get current directory
        current_dir = os.getcwd()
        
        # Create suitable filename
        base_filename = sanitize_filename(video_url)
        output_path = os.path.join(current_dir, base_filename)
        
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
        print(f"Output will be saved to: {output_path}.vtt")
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Transcript downloaded successfully!")
            
            # Find the downloaded VTT file(s)
            vtt_files = glob.glob(f"{output_path}*.vtt")
            
            if vtt_files:
                print(f"� Original VTT file(s) preserved: {', '.join(vtt_files)}")
                
                # Clean each VTT file and save to separate cleaned file
                for vtt_file in vtt_files:
                    print(f"🧹 Processing VTT file: {vtt_file}")
                    cleaned_file = clean_vtt_file(vtt_file)
                    
                    if cleaned_file:
                        print(f"✨ Cleaned transcript saved to separate file: {cleaned_file}")
                        print(f"📋 Original VTT file unchanged: {vtt_file}")
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
        description='Download and clean video transcripts using yt-dlp.',
        epilog='Example: python download_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"\n'
               'This will create both a .vtt file and a cleaned .txt file.'
    )
    parser.add_argument(
        'video_url',
        help='URL of the video to download transcript from'
    )
    
    args = parser.parse_args()
    
    # Validate URL format
    if not (args.video_url.startswith('http://') or args.video_url.startswith('https://')):
        print("❌ Error: Please provide a valid URL starting with http:// or https://", file=sys.stderr)
        sys.exit(1)
    
    download_transcript(args.video_url)


if __name__ == '__main__':
    main()