# Client interface for simplified HDFS

import os
import sys
import argparse
from typing import List, Dict, Any

from file_operations import upload_file, download_file, list_files, delete_file, get_file_info


def main():
    """
    Main function for the HDFS client.
    """
    parser = argparse.ArgumentParser(description='HDFS Client')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a file to HDFS')
    upload_parser.add_argument('local_path', help='Path to the local file')
    upload_parser.add_argument('--hdfs-path', help='Name to use in HDFS (default: basename of local_path)')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download a file from HDFS')
    download_parser.add_argument('hdfs_path', help='Name of the file in HDFS')
    download_parser.add_argument('local_path', help='Path to save the downloaded file')
    
    # List command
    subparsers.add_parser('list', help='List all files in HDFS')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a file from HDFS')
    delete_parser.add_argument('hdfs_path', help='Name of the file in HDFS')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get information about a file in HDFS')
    info_parser.add_argument('hdfs_path', help='Name of the file in HDFS')
    
    args = parser.parse_args()
    
    if args.command == 'upload':
        success = upload_file(args.local_path, args.hdfs_path)
        sys.exit(0 if success else 1)
    
    elif args.command == 'download':
        success = download_file(args.hdfs_path, args.local_path)
        sys.exit(0 if success else 1)
    
    elif args.command == 'list':
        files = list_files()
        if files:
            print("Files in HDFS:")
            for file in files:
                print(f"  {file}")
        else:
            print("No files found in HDFS")
    
    elif args.command == 'delete':
        success = delete_file(args.hdfs_path)
        sys.exit(0 if success else 1)
    
    elif args.command == 'info':
        file_info = get_file_info(args.hdfs_path)
        if file_info:
            print(f"File: {args.hdfs_path}")
            print(f"Blocks: {len(file_info['blocks'])}")
            print(f"Created: {file_info['created']}")
            print(f"Modified: {file_info['modified']}")
            print("Block Locations:")
            for i, block in enumerate(file_info['blocks']):
                print(f"  Block {i+1}: {block['block_id']}")
                for location in block['locations']:
                    print(f"    {location['host']}:{location['port']}")
        else:
            print(f"File '{args.hdfs_path}' not found")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()