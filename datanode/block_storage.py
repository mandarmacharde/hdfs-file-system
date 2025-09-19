# Block storage management for DataNode

import os
import shutil
from typing import Dict, List, Any, Tuple

from common.config import DATANODE_DATA_DIR


class BlockStorage:
    """
    Manages the storage of data blocks on a DataNode.
    """
    
    def __init__(self, data_dir: str = DATANODE_DATA_DIR):
        """
        Initialize the block storage.
        
        Args:
            data_dir: Directory to store blocks
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def store_block(self, block_id: str, data: bytes) -> bool:
        """
        Store a block in the local file system.
        
        Args:
            block_id: ID of the block
            data: Block data as bytes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            block_path = os.path.join(self.data_dir, block_id)
            with open(block_path, 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            print(f"Error storing block {block_id}: {e}")
            return False
    
    def retrieve_block(self, block_id: str) -> bytes:
        """
        Retrieve a block from the local file system.
        
        Args:
            block_id: ID of the block
            
        Returns:
            Block data as bytes
            
        Raises:
            FileNotFoundError: If the block doesn't exist
        """
        block_path = os.path.join(self.data_dir, block_id)
        with open(block_path, 'rb') as f:
            return f.read()
    
    def delete_block(self, block_id: str) -> bool:
        """
        Delete a block from the local file system.
        
        Args:
            block_id: ID of the block
            
        Returns:
            True if successful, False otherwise
        """
        try:
            block_path = os.path.join(self.data_dir, block_id)
            if os.path.exists(block_path):
                os.remove(block_path)
            return True
        except Exception as e:
            print(f"Error deleting block {block_id}: {e}")
            return False
    
    def list_blocks(self) -> List[str]:
        """
        List all blocks stored in this DataNode.
        
        Returns:
            List of block IDs
        """
        try:
            return [f for f in os.listdir(self.data_dir) 
                   if os.path.isfile(os.path.join(self.data_dir, f))]
        except Exception as e:
            print(f"Error listing blocks: {e}")
            return []
    
    def get_block_size(self, block_id: str) -> int:
        """
        Get the size of a block in bytes.
        
        Args:
            block_id: ID of the block
            
        Returns:
            Size of the block in bytes, or 0 if the block doesn't exist
        """
        try:
            block_path = os.path.join(self.data_dir, block_id)
            return os.path.getsize(block_path) if os.path.exists(block_path) else 0
        except Exception as e:
            print(f"Error getting block size for {block_id}: {e}")
            return 0
    
    def get_storage_info(self) -> Dict:
        """
        Get information about the storage usage.
        
        Returns:
            Dictionary with storage information
        """
        try:
            blocks = self.list_blocks()
            total_size = sum(self.get_block_size(block_id) for block_id in blocks)
            
            # Get disk usage information
            disk_usage = shutil.disk_usage(self.data_dir)
            
            return {
                'block_count': len(blocks),
                'total_size': total_size,  # bytes
                'disk_total': disk_usage.total,  # bytes
                'disk_used': disk_usage.used,  # bytes
                'disk_free': disk_usage.free,  # bytes
            }
        except Exception as e:
            print(f"Error getting storage info: {e}")
            return {
                'block_count': 0,
                'total_size': 0,
                'disk_total': 0,
                'disk_used': 0,
                'disk_free': 0,
            }