# Metadata management for NameNode

import os
import time
import threading
from typing import Dict, List, Set, Tuple, Any

from common.utils import load_json_file, save_json_file
from common.config import METADATA_FILE, REPLICATION_FACTOR, DATANODE_TIMEOUT


class MetadataManager:
    """
    Manages file system metadata including file-to-block mapping and block locations.
    """
    
    def __init__(self, metadata_file: str = METADATA_FILE):
        """
        Initialize the metadata manager.
        
        Args:
            metadata_file: Path to the metadata file
        """
        self.metadata_file = metadata_file
        self.lock = threading.RLock()  # Reentrant lock for thread safety
        
        # Load existing metadata or initialize empty structures
        self._load_metadata()
        
        # Start periodic metadata saving
        self._start_periodic_save()
    
    def _load_metadata(self) -> None:
        """
        Load metadata from file or initialize empty structures.
        """
        with self.lock:
            metadata = load_json_file(self.metadata_file, default={})
            
            # File to blocks mapping
            self.files = metadata.get('files', {})
            
            # Block to DataNodes mapping
            self.blocks = metadata.get('blocks', {})
            
            # DataNode status tracking
            self.datanodes = metadata.get('datanodes', {})
            
            # Upload and download counters
            self.total_uploads = metadata.get('total_uploads', 0)
            self.total_downloads = metadata.get('total_downloads', 0)
    
    def _save_metadata(self) -> None:
        """
        Save metadata to file.
        """
        with self.lock:
            metadata = {
                'files': self.files,
                'blocks': self.blocks,
                'datanodes': self.datanodes,
                'total_uploads': self.total_uploads,
                'total_downloads': self.total_downloads
            }
            save_json_file(self.metadata_file, metadata)
    
    def increment_uploads(self) -> None:
        """Increment the total upload count."""
        with self.lock:
            self.total_uploads += 1
            self._save_metadata()

    def increment_downloads(self) -> None:
        """Increment the total download count."""
        with self.lock:
            self.total_downloads += 1
            self._save_metadata()
    
    def _start_periodic_save(self, interval: int = 60) -> None:
        """
        Start a background thread to periodically save metadata.
        
        Args:
            interval: Save interval in seconds
        """
        def save_periodically():
            while True:
                time.sleep(interval)
                self._save_metadata()
        
        thread = threading.Thread(target=save_periodically, daemon=True)
        thread.start()
    
    def register_file(self, filename: str, blocks: List[str]) -> None:
        """
        Register a new file and its blocks in the metadata.
        
        Args:
            filename: Name of the file
            blocks: List of block IDs
        """
        with self.lock:
            self.files[filename] = {
                'blocks': blocks,
                'size': len(blocks),  # Number of blocks
                'created': time.time(),
                'modified': time.time()
            }
            self._save_metadata()
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from the metadata.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file was deleted, False otherwise
        """
        with self.lock:
            if filename not in self.files:
                return False
            
            # Get blocks associated with the file
            blocks = self.files[filename]['blocks']
            
            # Remove file entry
            del self.files[filename]
            
            # Remove block entries if they're not used by other files
            all_blocks = set()
            for file_info in self.files.values():
                all_blocks.update(file_info['blocks'])
            
            for block in blocks:
                if block not in all_blocks:
                    if block in self.blocks:
                        del self.blocks[block]
            
            self._save_metadata()
            return True
    
    def get_file_info(self, filename: str) -> Dict:
        """
        Get information about a file.
        
        Args:
            filename: Name of the file
            
        Returns:
            File information or empty dict if file doesn't exist
        """
        with self.lock:
            return self.files.get(filename, {})
    
    def list_files(self) -> List[str]:
        """
        Get a list of all files in the system.
        
        Returns:
            List of filenames
        """
        with self.lock:
            return list(self.files.keys())

    def get_total_file_count(self) -> int:
        """
        Get the total number of files.
        """
        with self.lock:
            return len(self.files)

    def get_total_block_count(self) -> int:
        """
        Get the total number of blocks.
        """
        with self.lock:
            return len(self.blocks)
    
    def register_block(self, block_id: str, datanode_id: str) -> None:
        """
        Register a block as being stored on a DataNode.
        
        Args:
            block_id: ID of the block
            datanode_id: ID of the DataNode
        """
        with self.lock:
            if block_id not in self.blocks:
                self.blocks[block_id] = []
            
            # Add DataNode to block's location list if not already there
            if datanode_id not in self.blocks[block_id]:
                self.blocks[block_id].append(datanode_id)
            
            self._save_metadata()
    
    def get_block_locations(self, block_id: str) -> List[str]:
        """
        Get the DataNodes where a block is stored.
        
        Args:
            block_id: ID of the block
            
        Returns:
            List of DataNode IDs
        """
        with self.lock:
            return self.blocks.get(block_id, [])
    
    def get_file_blocks(self, filename: str) -> List[str]:
        """
        Get the blocks that make up a file.
        
        Args:
            filename: Name of the file
            
        Returns:
            List of block IDs
        """
        with self.lock:
            file_info = self.files.get(filename, {})
            return file_info.get('blocks', [])
    
    def register_datanode(self, datanode_id: str, host: str, port: int) -> None:
        """
        Register a DataNode with the system.
        
        Args:
            datanode_id: ID of the DataNode
            host: Hostname or IP of the DataNode
            port: Port number of the DataNode
        """
        with self.lock:
            self.datanodes[datanode_id] = {
                'host': host,
                'port': port,
                'last_heartbeat': time.time(),
                'status': 'active'
            }
            self._save_metadata()
    
    def update_datanode_heartbeat(self, datanode_id: str) -> None:
        """
        Update the last heartbeat time for a DataNode.
        
        Args:
            datanode_id: ID of the DataNode
        """
        with self.lock:
            if datanode_id in self.datanodes:
                self.datanodes[datanode_id]['last_heartbeat'] = time.time()
                self.datanodes[datanode_id]['status'] = 'active'
    
    def check_datanode_status(self) -> None:
        """
        Check the status of all DataNodes and mark inactive ones.
        """
        with self.lock:
            current_time = time.time()
            for datanode_id, info in self.datanodes.items():
                if current_time - info['last_heartbeat'] > DATANODE_TIMEOUT:
                    info['status'] = 'inactive'
    
    def get_active_datanodes(self) -> List[Dict]:
        """
        Get a list of active DataNodes.
        
        Returns:
            List of active DataNode information
        """
        with self.lock:
            self.check_datanode_status()
            return [{'datanode_id': dn_id, **info} for dn_id, info in self.datanodes.items() 
                   if info['status'] == 'active']
    
    def select_datanodes_for_block(self, count: int = REPLICATION_FACTOR) -> List[str]:
        """
        Select DataNodes for storing a new block.
        
        Args:
            count: Number of DataNodes to select
            
        Returns:
            List of selected DataNode IDs
        """
        with self.lock:
            active_datanodes = self.get_active_datanodes()
            if len(active_datanodes) < count:
                raise ValueError(f"Not enough active DataNodes. Required: {count}, Available: {len(active_datanodes)}")
            

            return [dn['datanode_id'] for dn in active_datanodes[:count]]
    
    def check_under_replicated_blocks(self) -> Dict[str, int]:
        """
        Check for blocks that are under-replicated.
        
        Returns:
            Dictionary mapping block IDs to their replication count
        """
        with self.lock:
            self.check_datanode_status()
            active_datanode_ids = {dn['datanode_id'] for dn in self.get_active_datanodes()}
            
            under_replicated = {}
            for block_id, datanode_ids in self.blocks.items():
                # Count only active DataNodes that have this block
                active_replicas = sum(1 for dn_id in datanode_ids if dn_id in active_datanode_ids)
                if active_replicas < REPLICATION_FACTOR:
                    under_replicated[block_id] = active_replicas
            
            return under_replicated