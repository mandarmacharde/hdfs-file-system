# Utility functions for the simplified HDFS

import os
import hashlib
import json
import requests
from typing import List, Dict, Any, Tuple


def split_file_into_blocks(file_path: str, block_size: int) -> List[bytes]:
    """
    Split a file into blocks of specified size.
    
    Args:
        file_path: Path to the file to be split
        block_size: Size of each block in bytes
        
    Returns:
        List of byte arrays representing blocks
    """
    blocks = []
    with open(file_path, 'rb') as f:
        while True:
            block_data = f.read(block_size)
            if not block_data:
                break
            blocks.append(block_data)
    return blocks


def reassemble_blocks(blocks: List[bytes], output_file: str) -> None:
    """
    Reassemble blocks into a complete file.
    
    Args:
        blocks: List of byte arrays representing blocks
        output_file: Path to save the reassembled file
    """
    with open(output_file, 'wb') as f:
        for block in blocks:
            f.write(block)


def generate_block_id(data: bytes) -> str:
    """
    Generate a unique ID for a block based on its content.
    
    Args:
        data: Block data as bytes
        
    Returns:
        Unique block ID as string
    """
    return hashlib.md5(data).hexdigest()


def save_block_to_disk(block_data: bytes, block_id: str, data_dir: str) -> str:
    """
    Save a block to disk in the specified directory.
    
    Args:
        block_data: Block data as bytes
        block_id: Unique block ID
        data_dir: Directory to save the block
        
    Returns:
        Path where the block was saved
    """
    os.makedirs(data_dir, exist_ok=True)
    block_path = os.path.join(data_dir, block_id)
    with open(block_path, 'wb') as f:
        f.write(block_data)
    return block_path


def read_block_from_disk(block_id: str, data_dir: str) -> bytes:
    """
    Read a block from disk.
    
    Args:
        block_id: Unique block ID
        data_dir: Directory where the block is stored
        
    Returns:
        Block data as bytes
    """
    block_path = os.path.join(data_dir, block_id)
    with open(block_path, 'rb') as f:
        return f.read()


def make_api_request(url: str, method: str = 'GET', data: Dict = None, files: Dict = None) -> Dict:
    """
    Make an API request to a node.
    
    Args:
        url: API endpoint URL
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Data to send in the request
        files: Files to send in the request
        
    Returns:
        Response as dictionary
    """
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data, files=files)
        elif method == 'PUT':
            response = requests.put(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return {"error": str(e)}


def load_json_file(file_path: str, default: Any = None) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        default: Default value to return if file doesn't exist
        
    Returns:
        Loaded data or default value
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}


def save_json_file(file_path: str, data: Any) -> None:
    """
    Save data to a JSON file.
    
    Args:
        file_path: Path to save the JSON file
        data: Data to save
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)