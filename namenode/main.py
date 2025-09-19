# NameNode implementation for simplified HDFS

import os
import time
import uuid
import threading
import argparse
import requests
from typing import Dict, List, Any
from flask import Flask, request, jsonify
from flask_cors import CORS

from common.config import NAMENODE_PORT, METADATA_FILE, REPLICATION_FACTOR
from common.utils import make_api_request
from namenode.metadata import MetadataManager

BLOCK_SIZE = 1 * 1024 * 1024

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
metadata_manager = None


# main.py

@app.route('/api/v1/files', methods=['GET'])
def list_files():
    """
    List all files in the file system with their metadata.
    """
    filenames = metadata_manager.list_files()
    files_with_info = []
    for name in filenames:
        info = metadata_manager.get_file_info(name)
        if info:
            files_with_info.append({
                'name': name,
                'created': info.get('created', 0),
                'modified': info.get('modified', 0),
                'blocks': info.get('blocks', [])
            })

    return jsonify({
        'status': 'success',
        'files': files_with_info
    })


@app.route('/api/v1/files/<filename>', methods=['GET'])
def get_file_info(filename):
    """
    Get information about a specific file.
    """
    file_info = metadata_manager.get_file_info(filename)
    if not file_info:
        return jsonify({
            'status': 'error',
            'message': f"File '{filename}' not found"
        }), 404
    
    # Get block locations for each block
    blocks_with_locations = []
    for block_id in file_info['blocks']:
        locations = metadata_manager.get_block_locations(block_id)
        blocks_with_locations.append({
            'block_id': block_id,
            'locations': [
                {
                    'datanode_id': dn_id,
                    'host': metadata_manager.datanodes[dn_id]['host'],
                    'port': metadata_manager.datanodes[dn_id]['port']
                }
                for dn_id in locations
                if dn_id in metadata_manager.datanodes
            ]
        })
    
    return jsonify({
        'status': 'success',
        'file': {
            'name': filename,
            'blocks': blocks_with_locations,
            'created': file_info['created'],
            'modified': file_info['modified']
        }
    })

    
@app.route('/api/v1/files/<filename>/log_download', methods=['POST'])
def log_download_event(filename):
    """
    Log that a file has been successfully downloaded.
    """
    metadata_manager.increment_downloads()
    return jsonify({'status': 'success', 'message': f'Download of {filename} logged.'})


@app.route('/api/v1/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """
    Delete a file from the file system.
    """
    success = metadata_manager.delete_file(filename)
    if not success:
        return jsonify({
            'status': 'error',
            'message': f"File '{filename}' not found"
        }), 404
    
    return jsonify({
        'status': 'success',
        'message': f"File '{filename}' deleted successfully"
    })

@app.route('/api/v1/files/upload', methods=['POST'])
def upload_file():
    """
    Handle a file upload, orchestrating the block storage on DataNodes.
    """
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400

    file = request.files['file']
    filename = file.filename
    file_data = file.read()

    if filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    # Check if file already exists
    if metadata_manager.get_file_info(filename):
        return jsonify({'status': 'error', 'message': f"File '{filename}' already exists"}), 409

    block_ids = []
    try:
        # 1. Split the file into blocks
        for i in range(0, len(file_data), BLOCK_SIZE):
            block_content = file_data[i:i + BLOCK_SIZE]
            block_id = str(uuid.uuid4())
            block_ids.append(block_id)

            # 2. Ask NameNode for DataNodes to store this block
            datanodes = metadata_manager.select_datanodes_for_block()
            if not datanodes:
                raise IOError("Could not allocate DataNodes for block.")

            # 3. Command each DataNode to store the block
            for dn_id in datanodes:
                datanode = metadata_manager.datanodes[dn_id]
                datanode_url = f"http://{datanode['host']}:{datanode['port']}/api/v1/blocks/{block_id}"
                
                files = {'block': (block_id, block_content, 'application/octet-stream')}
                response = requests.put(datanode_url, files=files)
                response.raise_for_status() # Raises an exception for 4xx/5xx errors

        # 4. Register the file and its blocks with the NameNode's metadata
        metadata_manager.register_file(filename, block_ids)
        metadata_manager.increment_uploads()

        return jsonify({
            'status': 'success',
            'message': f"File '{filename}' uploaded successfully",
            'filename': filename,
            'blocks': block_ids
        })

    except Exception as e:
        # In a real system, you'd want to implement cleanup logic here
        # to delete partially uploaded blocks.
        print(f"Error during file upload for {filename}: {e}")
        return jsonify({'status': 'error', 'message': 'File upload failed'}), 500


@app.route('/api/v1/blocks/allocate', methods=['POST'])
def allocate_blocks():
    """
    Allocate DataNodes for storing blocks.
    """
    data = request.json
    if not data or 'num_blocks' not in data:
        return jsonify({
            'status': 'error',
            'message': "Missing required parameter: num_blocks"
        }), 400
    
    num_blocks = data['num_blocks']
    filename = data.get('filename', '')
    
    try:
        # Allocate DataNodes for each block
        block_allocations = []
        for _ in range(num_blocks):
            datanodes = metadata_manager.select_datanodes_for_block()
            block_allocations.append([
                {
                    'datanode_id': dn_id,
                    'host': metadata_manager.datanodes[dn_id]['host'],
                    'port': metadata_manager.datanodes[dn_id]['port']
                }
                for dn_id in datanodes
            ])
        
        return jsonify({
            'status': 'success',
            'block_allocations': block_allocations
        })
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 503  # Service Unavailable


@app.route('/api/v1/files', methods=['POST'])
def register_file():
    """
    Register a new file in the file system.
    """
    data = request.json
    if not data or 'filename' not in data or 'blocks' not in data:
        return jsonify({
            'status': 'error',
            'message': "Missing required parameters: filename, blocks"
        }), 400
    
    filename = data['filename']
    blocks = data['blocks']
    
    # Check if file already exists
    if metadata_manager.get_file_info(filename):
        return jsonify({
            'status': 'error',
            'message': f"File '{filename}' already exists"
        }), 409  # Conflict
    
    # Register the file
    metadata_manager.register_file(filename, blocks)
    
    return jsonify({
        'status': 'success',
        'message': f"File '{filename}' registered successfully"
    })


@app.route('/api/v1/blocks/<block_id>', methods=['POST'])
def register_block(block_id):
    """
    Register a block as being stored on a DataNode.
    """
    data = request.json
    if not data or 'datanode_id' not in data:
        return jsonify({
            'status': 'error',
            'message': "Missing required parameter: datanode_id"
        }), 400
    
    datanode_id = data['datanode_id']
    metadata_manager.register_block(block_id, datanode_id)
    
    return jsonify({
        'status': 'success',
        'message': f"Block '{block_id}' registered on DataNode '{datanode_id}'"
    })


@app.route('/api/v1/datanodes', methods=['GET'])
def list_datanodes():
    """
    List all active DataNodes.
    """
    datanodes = metadata_manager.get_active_datanodes()
    return jsonify({
        'status': 'success',
        'datanodes': datanodes
    })


@app.route('/api/v1/storage', methods=['GET'])
def get_storage_info():
    """
    Get aggregated storage information from all active DataNodes.
    """
    total_used = 0
    total_capacity = 0

    active_datanodes = metadata_manager.get_active_datanodes()
    for datanode in active_datanodes:
        try:
            # Contact each datanode to get its specific storage info
            dn_url = f"http://{datanode['host']}:{datanode['port']}/api/v1/info"
            response = requests.get(dn_url, timeout=2)
            response.raise_for_status()
            info = response.json()
            
            total_used += info['storage']['disk_used']
            total_capacity += info['storage']['disk_total']
        except requests.exceptions.RequestException as e:
            print(f"Could not contact DataNode {datanode['datanode_id']} for storage info: {e}")

    return jsonify({
        'status': 'success',
        'storage': {
            'total_used_bytes': total_used,
            'total_capacity_bytes': total_capacity,
        }
    })


@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """
    Get basic statistics about the file system.
    """
    try:
        stats = {
            'total_files': metadata_manager.get_total_file_count(),
            'total_blocks': metadata_manager.get_total_block_count(),
            'active_datanodes': len(metadata_manager.get_active_datanodes()),
            'total_uploads': metadata_manager.total_uploads,
            'total_downloads': metadata_manager.total_downloads
        }
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/v1/datanodes/register', methods=['POST'])
def register_datanode():
    """
    Register a new DataNode with the NameNode.
    """
    data = request.json
    if not data or 'datanode_id' not in data or 'host' not in data or 'port' not in data:
        return jsonify({
            'status': 'error',
            'message': "Missing required parameters: datanode_id, host, port"
        }), 400
    
    datanode_id = data['datanode_id']
    host = data['host']
    port = data['port']
    
    metadata_manager.register_datanode(datanode_id, host, port)
    
    return jsonify({
        'status': 'success',
        'message': f"DataNode '{datanode_id}' registered successfully"
    })


@app.route('/api/v1/datanodes/heartbeat', methods=['POST'])
def datanode_heartbeat():
    """
    Handle heartbeat from a DataNode.
    """
    data = request.json
    if not data or 'datanode_id' not in data:
        return jsonify({
            'status': 'error',
            'message': "Missing required parameter: datanode_id"
        }), 400
    
    datanode_id = data['datanode_id']
    metadata_manager.update_datanode_heartbeat(datanode_id)
    
    # Check for under-replicated blocks
    under_replicated = metadata_manager.check_under_replicated_blocks()
    
    return jsonify({
        'status': 'success',
        'message': f"Heartbeat received from DataNode '{datanode_id}'",
        'under_replicated_blocks': under_replicated
    })


def start_replication_monitor(interval=60):
    """
    Start a background thread to monitor block replication.
    
    Args:
        interval: Check interval in seconds
    """
    def monitor_replication():
        while True:
            time.sleep(interval)
            try:
                under_replicated = metadata_manager.check_under_replicated_blocks()
                if under_replicated:
                    print(f"Found {len(under_replicated)} under-replicated blocks")
                    # In a real system, we would initiate re-replication here
            except Exception as e:
                print(f"Error in replication monitor: {e}")
    
    thread = threading.Thread(target=monitor_replication, daemon=True)
    thread.start()


def main():
    """
    Main function to start the NameNode server.
    """
    parser = argparse.ArgumentParser(description='Start the HDFS NameNode')
    parser.add_argument('--port', type=int, default=NAMENODE_PORT,
                        help=f'Port to run the NameNode on (default: {NAMENODE_PORT})')
    parser.add_argument('--metadata', type=str, default=METADATA_FILE,
                        help=f'Path to metadata file (default: {METADATA_FILE})')
    args = parser.parse_args()
    
    global metadata_manager
    metadata_manager = MetadataManager(metadata_file=args.metadata)
    
    # Start replication monitor
    start_replication_monitor()
    
    print(f"Starting NameNode on port {args.port}")
    app.run(host='0.0.0.0', port=args.port)


if __name__ == '__main__':
    main()