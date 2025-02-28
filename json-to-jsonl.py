#!/usr/bin/env python3
import json
import os
import argparse
from tqdm import tqdm

def convert_json_to_jsonl(input_file, output_file=None):
    """
    Convert a JSON file (containing an array of objects) to JSONL format.
    
    Args:
        input_file (str): Path to the input JSON file
        output_file (str, optional): Path to the output JSONL file. If None, 
                                     will replace .json with .jsonl
    
    Returns:
        str: Path to the output file
    """
    if output_file is None:
        output_file = input_file.replace('.json', '.jsonl')
    
    print(f"Converting {input_file} to {output_file}...")
    
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Verify it's a list/array
    if not isinstance(data, list):
        raise ValueError(f"Input file {input_file} must contain a JSON array")
    
    # Write each object as a separate line in the JSONL file
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in tqdm(data, desc="Converting"):
            json_line = json.dumps(item, ensure_ascii=False)
            f.write(json_line + '\n')
    
    print(f"Conversion complete! Wrote {len(data)} lines to {output_file}")
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Convert JSON files to JSONL format')
    parser.add_argument('input_files', nargs='+', help='Input JSON file paths')
    parser.add_argument('--output-dir', help='Output directory (optional)')
    
    args = parser.parse_args()
    
    for input_file in args.input_files:
        if args.output_dir:
            base_name = os.path.basename(input_file).replace('.json', '.jsonl')
            output_file = os.path.join(args.output_dir, base_name)
            os.makedirs(args.output_dir, exist_ok=True)
        else:
            output_file = None
            
        convert_json_to_jsonl(input_file, output_file)

if __name__ == "__main__":
    main()