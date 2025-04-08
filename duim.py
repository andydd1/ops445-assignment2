#!/usr/bin/env python3
"""
DU Improved - Disk Usage Improved
Author: [Your Name]
"""

import subprocess
import argparse
import sys
import os

def call_du_sub(target_dir):
    try:
        process = subprocess.Popen(
            ['du', '-d', '1', target_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        output, _ = process.communicate()
        return [line.strip() for line in output.splitlines()]
    except subprocess.SubprocessError as e:
        print(f"Error running du command: {e}", file=sys.stderr)
        sys.exit(1)

def percent_to_graph(percent, total_chars):
    if not 0 <= percent <= 100:
        raise ValueError("Percent must be between 0 and 100")
    filled = round(percent / 100 * total_chars)
    return '=' * filled + ' ' * (total_chars - filled)

def create_dir_dict(du_output):
    dir_dict = {}
    for line in du_output:
        try:
            size, dir_path = line.split(maxsplit=1)
            dir_dict[dir_path] = int(size)
        except ValueError:
            continue
    return dir_dict

def bytes_to_human(size):
    for unit in ['', 'K', 'M', 'G', 'T']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}P"

def colorize_graph(graph, percent):
    if percent > 80:
        color = '\033[91m'
    elif percent > 50:
        color = '\033[93m'
    else:
        color = '\033[92m'
    return f"{color}{graph}\033[0m"

def parse_command_args():
    parser = argparse.ArgumentParser(
        description='DU Improved -- See Disk Usage Report with bar charts',
        epilog='Copyright 2023'
    )
    parser.add_argument(
        '-H', '--human-readable',
        action='store_true',
        help='print sizes in human readable format (e.g. 1K 23M 2G)'
    )
    parser.add_argument(
        '-l', '--length',
        type=int,
        default=20,
        help='Specify the length of the graph. Default is 20.'
    )
    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=0,
        help='Minimum percentage to display (default: 0)'
    )
    parser.add_argument(
        'target',
        nargs='?',
        default='.',
        help='The directory to scan'
    )
    return parser.parse_args()

def print_report(dir_dict, total_size, args):
    sorted_dirs = sorted(
        dir_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    print(f"\nDisk Usage Report for: {os.path.abspath(args.target)}\n")
    print(f"{'%':>6}  {'Size':>8}  {'Graph'}  Directory")
    print("-" * (args.length + 30))
    
    for dir_path, size in sorted_dirs:
        percent = (size / total_size) * 100
        if percent < args.threshold:
            continue
            
        graph = percent_to_graph(percent, args.length)
        colored_graph = colorize_graph(graph, percent)
        
        size_str = (
            bytes_to_human(size) 
            if args.human_readable 
            else str(size)
        )
        
        print(
            f"{percent:6.1f}%  "
            f"{size_str:>8}  "
            f"[{colored_graph}]  "
            f"{dir_path}"
        )

if __name__ == '__main__':
    try:
        args = parse_command_args()
        
        if not os.path.isdir(args.target):
            print(f"Error: {args.target} is not a valid directory", file=sys.stderr)
            sys.exit(1)
            
        du_output = call_du_sub(args.target)
        dir_dict = create_dir_dict(du_output)
        total_size = sum(size for path, size in dir_dict.items() 
                        if path != args.target.rstrip('/'))
        print_report(dir_dict, total_size, args)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
