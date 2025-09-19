#!/usr/bin/env python3
"""
Script to format sentences by adding newlines after periods.
Takes a filename as a command line argument and processes the file
to ensure each sentence ends with a newline.
"""

import sys
import argparse
import re


def format_sentences(text):
    """
    Find all periods in the text and add newlines after them
    if they're not already followed by an end-of-line character.
    Also remove single space characters at the beginning of new lines.
    Remove duplicate consecutive sentences.
    
    Args:
        text (str): The input text to process
        
    Returns:
        str: The formatted text with newlines after periods, cleaned line starts, and no duplicate sentences
    """
    # Use regex to find periods not followed by whitespace that includes newline
    # This pattern looks for a period followed by any character that's not a newline
    formatted_text = re.sub(r'\.(?!\s*$)(?!\s*\n)', '.\n', text)
    
    # Remove single space character at the beginning of new lines
    # This pattern matches newline followed by exactly one space and then non-space content
    formatted_text = re.sub(r'\n ', '\n', formatted_text)
    
    # Remove duplicate consecutive sentences
    # Split the text into lines (each line should be a sentence after formatting)
    lines = formatted_text.split('\n')
    result_lines = []
    
    for line in lines:
        # Clean the line (remove leading/trailing whitespace)
        cleaned_line = line.strip()
        
        # If this line is empty, always keep it (preserves paragraph breaks)
        if not cleaned_line:
            result_lines.append(line)
            continue
        
        # Check if this sentence is the same as the previous non-empty sentence
        if result_lines:
            # Find the last non-empty line
            last_non_empty = None
            for prev_line in reversed(result_lines):
                if prev_line.strip():
                    last_non_empty = prev_line.strip()
                    break
            
            # If current line is same as last non-empty line, skip it
            if last_non_empty and cleaned_line == last_non_empty:
                continue
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def process_file(filename):
    """
    Process a file to format sentences.
    
    Args:
        filename (str): Path to the file to process
    """
    try:
        # Read the file
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Format the content
        formatted_content = format_sentences(content)
        
        # Write back to the file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(formatted_content)
        
        print(f"Successfully processed file: {filename}")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading/writing file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to handle command line arguments and process the file."""
    parser = argparse.ArgumentParser(
        description='Format sentences by adding newlines after periods.'
    )
    parser.add_argument(
        'filename',
        help='Name of the file to process'
    )
    
    args = parser.parse_args()
    
    process_file(args.filename)


if __name__ == '__main__':
    main()