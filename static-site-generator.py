#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import errno
from datetime import datetime

def main(template_path, output_dir):
    # Read the template file
    with open(template_path, 'r') as template_file:
        template_content = template_file.read()
    
    print(f"{'-' * 80}\nBegin output\n{'-' * 80}")
    
    # Iterate through content files
    for subdir, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".content"):
                content_file_path = os.path.join(subdir, file)
                
                # Extract date information from the filename
                _, year_str, month_str, _ = content_file_path.split(os.sep)
                day_str = (file.split('.'))[0]
                
                # Create the result string
                with open(content_file_path, 'r') as content_file:
                    result = template_content.replace('<div class="content"></div>', f'<div class="content">{content_file.read()}</div>')
                
                # Print date, hyphens, and result
                print(f"{year_str}-{month_str}-{day_str}\n{'-' * 80}\n{result}\n{'-' * 80}")
                
                # Create or warn about existing HTML file
                html_output_path = os.path.join(output_dir, f"{year_str}/{month_str}/{day_str}.html")
                if not os.path.exists(html_output_path):
                    try:
                        os.makedirs(os.path.dirname(html_output_path))
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            raise
                    with open(html_output_path, 'w') as html_file:
                        html_file.write(result)
                else:
                    print("\033[91mWarning: The file {} already exists.\033[0m".format(html_output_path), file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        script_name = os.path.basename(__file__)
        print(f"Usage: {script_name} template_path output_dir")
        sys.exit(1)
    
    template_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.isfile(template_path):
        print(f"Error: Template file {template_path} not found.")
        sys.exit(1)
    
    if not os.path.isdir(output_dir):
        print(f"Error: Output directory {output_dir} not found.")
        sys.exit(1)
    
    main(template_path, output_dir)
