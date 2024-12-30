#!/bin/bash

# Check if the directory and output file are provided as arguments
if [ $# -lt 2 ]; then
  echo "Usage: $0 <directory_path> <output_file>"
  exit 1
fi

DIRECTORY=$1
OUTPUT_FILE=$2

# Check if the directory exists
if [ ! -d "$DIRECTORY" ]; then
  echo "Error: Directory $DIRECTORY does not exist."
  exit 1
fi

# Initialize the output file
echo "Python files content from directory: $DIRECTORY" > "$OUTPUT_FILE"
echo "==========================================" >> "$OUTPUT_FILE"

# Find and process Python files excluding __init__.py
found_files=false
while IFS= read -r -d '' file; do
  found_files=true
  echo "File: $file" >> "$OUTPUT_FILE"
  echo "--------------------" >> "$OUTPUT_FILE"
  cat "$file" >> "$OUTPUT_FILE"
  echo -e "\n" >> "$OUTPUT_FILE"
done < <(find "$DIRECTORY" -type f -name "*.py" ! -name "__init__.py" -print0)

if [ "$found_files" = false ]; then
  echo "No Python files found in $DIRECTORY or its subdirectories (excluding __init__.py)."
else
  echo "Python file contents have been saved to $OUTPUT_FILE."
fi
