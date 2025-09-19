# File operations for HDFS Client

import os
import requests
from typing import List, Dict, Any, Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import BLOCK_SIZE, NAMENODE_API_BASE
from common.utils import split_file_into_blocks, reassemble_blocks, generate_block_id, make_api_request


def upload_file(file_path: str, hdfs_filename: str = None) -> bool:
    """
    Upload a file to HDFS.
    
    Args:
        file_path: Path to the local file
        hdfs_filename: Name to use in HDFS (default: basename of file_path)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Use the basename of the file path if hdfs_filename is not provided
        if not hdfs_filename:
            hdfs_filename = os.path.basename(file_path)
        
        # Split the file into blocks
        print(f"Splitting file into blocks of size {BLOCK_SIZE} bytes...")
        blocks = split_file_into_blocks(file_path, BLOCK_SIZE)
        print(f"File split into {len(blocks)} blocks")
        
        # Allocate DataNodes for blocks
        print(f"Requesting block allocations from NameNode...")
        response = make_api_request(
            f"{NAMENODE_API_BASE}/blocks/allocate",
            method='POST',
            data={
                'num_blocks': len(blocks),
                'filename': hdfs_filename
            }
        )
        
        if 'error' in response:
            print(f"Error allocating blocks: {response['error']}")
            return False
        
        block_allocations = response['block_allocations']
        
        # Upload blocks to DataNodes
        print(f"Uploading blocks to DataNodes...")
        block_ids = []
        for i, block_data in enumerate(blocks):
            block_id = generate_block_id(block_data)
            block_ids.append(block_id)
            
            # Get DataNode allocations for this block
            datanodes = block_allocations[i]
            
            # Upload to each DataNode (replication)
            for datanode in datanodes:
                host = datanode['host']
                port = datanode['port']
                url = f"http://{host}:{port}/api/v1/blocks/{block_id}"
                
                print(f"Uploading block {i+1}/{len(blocks)} to {host}:{port}...")
                files = {'block': block_data}
                try:
                    response = requests.put(url, files=files)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"Error uploading block to {host}:{port}: {e}")
                    # Continue with other replicas
        
        # Register the file with the NameNode
        print(f"Registering file with NameNode...")
        response = make_api_request(
            f"{NAMENODE_API_BASE}/files",
            method='POST',
            data={
                'filename': hdfs_filename,
                'blocks': block_ids
            }
        )
        
        if 'error' in response:
            print(f"Error registering file: {response['error']}")
            return False
        
        print(f"File uploaded successfully as '{hdfs_filename}'")
        return True
    
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False


def download_file(hdfs_filename: str, output_path: str) -> bool:
    """
    Download a file from HDFS.
    
    Args:
        hdfs_filename: Name of the file in HDFS
        output_path: Path to save the downloaded file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get file information from NameNode
        print(f"Getting file information from NameNode...")
        response = make_api_request(
            f"{NAMENODE_API_BASE}/files/{hdfs_filename}",
            method='GET'
        )
        
        if 'error' in response:
            print(f"Error getting file information: {response['error']}")
            return False
        
        file_info = response['file']
        blocks_info = file_info['blocks']
        
        # Download blocks from DataNodes
        print(f"Downloading {len(blocks_info)} blocks...")
        blocks = []
        for i, block_info in enumerate(blocks_info):
            block_id = block_info['block_id']
            locations = block_info['locations']
            
            # Try each location until successful
            success = False
            for location in locations:
                host = location['host']
                port = location['port']
                url = f"http://{host}:{port}/api/v1/blocks/{block_id}"
                
                print(f"Downloading block {i+1}/{len(blocks_info)} from {host}:{port}...")
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    blocks.append(response.content)
                    success = True
                    break
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading block from {host}:{port}: {e}")
            
            if not success:
                print(f"Failed to download block {block_id} from any DataNode")
                return False
        
        # Reassemble blocks into the output file
        print(f"Reassembling blocks into output file...")
        reassemble_blocks(blocks, output_path)
        
        print(f"File downloaded successfully to '{output_path}'")
        return True
    
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False


def list_files() -> List[str]:
    """
    List all files in HDFS.
    
    Returns:
        List of filenames
    """
    try:
        response = make_api_request(
            f"{NAMENODE_API_BASE}/files",
            method='GET'
        )
        
        if 'error' in response:
            print(f"Error listing files: {response['error']}")
            return []
        
        return response['files']
    
    except Exception as e:
        print(f"Error listing files: {e}")
        return []


def delete_file(hdfs_filename: str) -> bool:
    """
    Delete a file from HDFS.
    
    Args:
        hdfs_filename: Name of the file in HDFS
        
    Returns:
        True if successful, False otherwise
    """
    try:
        response = make_api_request(
            f"{NAMENODE_API_BASE}/files/{hdfs_filename}",
            method='DELETE'
        )
        
        if 'error' in response:
            print(f"Error deleting file: {response['error']}")
            return False
        
        print(f"File '{hdfs_filename}' deleted successfully")
        return True
    
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def get_file_info(hdfs_filename: str) -> Dict:
    """
    Get information about a file in HDFS.
    
    Args:
        hdfs_filename: Name of the file in HDFS
        
    Returns:
        File information or empty dict if file doesn't exist
    """
    try:
        response = make_api_request(
            f"{NAMENODE_API_BASE}/files/{hdfs_filename}",
            method='GET'
        )
        
        if 'error' in response:
            print(f"Error getting file information: {response['error']}")
            return {}
        
        return response['file']
    
    except Exception as e:
        print(f"Error getting file information: {e}")
        return {}