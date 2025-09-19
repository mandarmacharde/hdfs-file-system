#!/usr/bin/env python3

"""
Test script for the simplified HDFS implementation.

This script demonstrates how to use the system by:
1. Starting a NameNode
2. Starting multiple DataNodes
3. Uploading a file
4. Listing files
5. Getting file information
6. Downloading the file
7. Deleting the file

Usage:
    python test_hdfs.py
"""

import os
import time
import subprocess
import tempfile
import shutil
import signal
import sys


def create_test_file(size_mb=10):
    """
    Create a test file of specified size.
    
    Args:
        size_mb: Size of the file in MB
        
    Returns:
        Path to the created file
    """
    fd, path = tempfile.mkstemp(suffix='.txt')
    with os.fdopen(fd, 'wb') as f:
        f.write(os.urandom(size_mb * 1024 * 1024))  # Random data
    return path


def start_namenode():
    """
    Start the NameNode process.
    
    Returns:
        Process object
    """
    print("Starting NameNode...")
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
    process = subprocess.Popen(
        [sys.executable, 'namenode/namenode.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    time.sleep(2)  # Give it time to start
    return process


def start_datanode(port, data_dir):
    """
    Start a DataNode process.
    
    Args:
        port: Port number for the DataNode
        data_dir: Directory to store data
        
    Returns:
        Process object
    """
    print(f"Starting DataNode on port {port}...")
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
    process = subprocess.Popen(
        [sys.executable, 'datanode/datanode.py', '--port', str(port), '--data_dir', data_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    time.sleep(1)  # Give it time to start
    return process


def run_client_command(command, *args):
    """
    Run a client command.
    
    Args:
        command: Client command to run
        args: Additional arguments
        
    Returns:
        Command output
    """
    cmd = [sys.executable, 'client/client.py', command] + list(args)
    print(f"Running: {' '.join(cmd)}")
    process = subprocess.run(cmd, capture_output=True, text=True)
    print(process.stdout)
    if process.stderr:
        print(f"Error: {process.stderr}")
    return process.stdout


def main():
    """
    Main test function.
    """
    # Create temporary directories for DataNodes
    data_dirs = [
        tempfile.mkdtemp(prefix='datanode1_'),
        tempfile.mkdtemp(prefix='datanode2_')
    ]
    
    try:
        # Start NameNode
        namenode_process = start_namenode()
        
        # Start DataNodes
        datanode_processes = [
            start_datanode(5001, data_dirs[0]),
            start_datanode(5002, data_dirs[1])
        ]
        
        # Wait for nodes to initialize
        print("Waiting for nodes to initialize...")
        time.sleep(3)
        
        # Check if NameNode is running
        if namenode_process.poll() is not None:
            print("NameNode failed to start.")
            namenode_err = namenode_process.stderr.read()
            print(namenode_err.decode('utf-8'))
            return
        
        # Create a test file
        test_file = create_test_file(size_mb=1)  # 1MB test file
        print(f"Created test file: {test_file}")
        
        # Upload the file
        print("\n=== Uploading file ===")
        run_client_command('upload', test_file, '--hdfs-path', 'test_file.dat')
        
        # List files
        print("\n=== Listing files ===")
        run_client_command('list')
        
        # Get file info
        print("\n=== Getting file info ===")
        run_client_command('info', 'test_file.dat')
        
        # Download the file
        download_path = os.path.join(tempfile.gettempdir(), 'downloaded_file.dat')
        print("\n=== Downloading file ===")
        run_client_command('download', 'test_file.dat', download_path)
        
        # Verify the download
        if os.path.exists(download_path):
            original_size = os.path.getsize(test_file)
            downloaded_size = os.path.getsize(download_path)
            print(f"Original file size: {original_size} bytes")
            print(f"Downloaded file size: {downloaded_size} bytes")
            print(f"Files match: {original_size == downloaded_size}")
        else:
            print("Download failed: File not found")
        
        # Delete the file
        print("\n=== Deleting file ===")
        run_client_command('delete', 'test_file.dat')
        
        # List files again to confirm deletion
        print("\n=== Listing files after deletion ===")
        run_client_command('list')
        
        print("\nTest completed successfully!")
    
    finally:
        # Clean up
        print("\nCleaning up...")
        
        # Terminate processes
        for process in datanode_processes + [namenode_process]:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Remove temporary files and directories
        for data_dir in data_dirs:
            shutil.rmtree(data_dir, ignore_errors=True)
        
        if 'test_file' in locals() and os.path.exists(test_file):
            os.remove(test_file)
        
        if 'download_path' in locals() and os.path.exists(download_path):
            os.remove(download_path)


if __name__ == '__main__':
    main()