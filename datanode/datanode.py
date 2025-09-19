# DataNode implementation for simplified HDFS

import os
import time
import uuid
import threading
import argparse
from typing import Dict, List, Any
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import requests
import io

from common.config import NAMENODE_HOST, NAMENODE_PORT, DATANODE_PORT_BASE, DATANODE_DATA_DIR, HEARTBEAT_INTERVAL
from common.utils import make_api_request
from block_storage import BlockStorage


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
block_storage = None
datanode_id = None
datanode_host = None
datanode_port = None


@app.route('/api/v1/blocks/<block_id>', methods=['GET'])
def get_block(block_id):
    """
    Retrieve a block from storage.
    """
    try:
        block_data = block_storage.retrieve_block(block_id)
        return send_file(
            io.BytesIO(block_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=block_id
        )
    except FileNotFoundError:
        return jsonify({
            'status': 'error',
            'message': f"Block '{block_id}' not found"
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/v1/blocks/<block_id>', methods=['PUT'])
def store_block(block_id):
    """
    Store a block in the DataNode.
    """
    if 'block' not in request.files:
        return jsonify({
            'status': 'error',
            'message': "No block file provided"
        }), 400
    
    block_file = request.files['block']
    block_data = block_file.read()
    
    success = block_storage.store_block(block_id, block_data)
    if not success:
        return jsonify({
            'status': 'error',
            'message': f"Failed to store block '{block_id}'"
        }), 500
    
    # Register the block with the NameNode
    namenode_url = f"http://{NAMENODE_HOST}:{NAMENODE_PORT}/api/v1/blocks/{block_id}"
    try:
        response = requests.post(namenode_url, json={
            'datanode_id': datanode_id
        })
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to register block with NameNode: {e}")
    
    return jsonify({
        'status': 'success',
        'message': f"Block '{block_id}' stored successfully"
    })


@app.route('/api/v1/blocks/<block_id>', methods=['DELETE'])
def delete_block(block_id):
    """
    Delete a block from the DataNode.
    """
    success = block_storage.delete_block(block_id)
    if not success:
        return jsonify({
            'status': 'error',
            'message': f"Failed to delete block '{block_id}'"
        }), 500
    
    return jsonify({
        'status': 'success',
        'message': f"Block '{block_id}' deleted successfully"
    })


@app.route('/api/v1/blocks', methods=['GET'])
def list_blocks():
    """
    List all blocks stored in this DataNode.
    """
    blocks = block_storage.list_blocks()
    return jsonify({
        'status': 'success',
        'blocks': blocks
    })


@app.route('/api/v1/info', methods=['GET'])
def get_info():
    """
    Get information about this DataNode.
    """
    storage_info = block_storage.get_storage_info()
    return jsonify({
        'status': 'success',
        'datanode_id': datanode_id,
        'host': datanode_host,
        'port': datanode_port,
        'storage': storage_info
    })


def send_heartbeat():
    """
    Send a heartbeat to the NameNode.
    """
    namenode_url = f"http://{NAMENODE_HOST}:{NAMENODE_PORT}/api/v1/datanodes/heartbeat"
    try:
        response = requests.post(namenode_url, json={
            'datanode_id': datanode_id
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send heartbeat: {e}")
        return None


def heartbeat_sender():
    """
    Background thread to send periodic heartbeats to the NameNode.
    """
    while True:
        try:
            response = send_heartbeat()
            if response and 'under_replicated_blocks' in response:
                under_replicated = response['under_replicated_blocks']
                if under_replicated:
                    print(f"NameNode reported {len(under_replicated)} under-replicated blocks")
                    # In a real system, we would handle re-replication here
        except Exception as e:
            print(f"Error in heartbeat thread: {e}")
        
        time.sleep(HEARTBEAT_INTERVAL)


def register_with_namenode():
    """
    Register this DataNode with the NameNode.
    """
    namenode_url = f"http://{NAMENODE_HOST}:{NAMENODE_PORT}/api/v1/datanodes/register"
    try:
        response = requests.post(namenode_url, json={
            'datanode_id': datanode_id,
            'host': datanode_host,
            'port': datanode_port
        })
        response.raise_for_status()
        print(f"Registered with NameNode: {response.json()['message']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to register with NameNode: {e}")
        return False


def main():
    """
    Main function to start the DataNode server.
    """
    parser = argparse.ArgumentParser(description='Start an HDFS DataNode')
    parser.add_argument('--port', type=int, default=DATANODE_PORT_BASE,
                        help=f'Port to run the DataNode on (default: {DATANODE_PORT_BASE})')
    parser.add_argument('--host', type=str, default='localhost',
                        help='Hostname or IP address for this DataNode')
    parser.add_argument('--data_dir', type=str, default=DATANODE_DATA_DIR,
                        help=f'Directory to store data blocks (default: {DATANODE_DATA_DIR})')
    parser.add_argument('--id', type=str, default=None,
                        help='Unique ID for this DataNode (default: auto-generated)')
    args = parser.parse_args()
    
    # Initialize global variables
    global block_storage, datanode_id, datanode_host, datanode_port
    
    datanode_id = args.id if args.id else str(uuid.uuid4())
    datanode_host = args.host
    datanode_port = args.port
    
    # Create data directory with DataNode ID to ensure uniqueness
    data_dir = os.path.join(args.data_dir, datanode_id)
    block_storage = BlockStorage(data_dir=data_dir)
    
    # Register with NameNode
    if not register_with_namenode():
        print("Failed to register with NameNode. Exiting.")
        return
    
    # Start heartbeat thread
    heartbeat_thread = threading.Thread(target=heartbeat_sender, daemon=True)
    heartbeat_thread.start()
    
    print(f"Starting DataNode {datanode_id} on {datanode_host}:{datanode_port}")
    app.run(host='0.0.0.0', port=datanode_port)


if __name__ == '__main__':
    main()