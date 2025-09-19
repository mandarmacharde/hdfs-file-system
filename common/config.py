# Configuration settings for the simplified HDFS

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# NameNode configuration
NAMENODE_HOST = os.getenv('NAMENODE_HOST', 'localhost')
NAMENODE_PORT = int(os.getenv('NAMENODE_PORT', 5000))

# DataNode configuration
DATANODE_PORT_BASE = int(os.getenv('DATANODE_PORT_BASE', 5001))

# File system configuration
BLOCK_SIZE = int(os.getenv('BLOCK_SIZE', 64 * 1024 * 1024))  # 64MB default
REPLICATION_FACTOR = int(os.getenv('REPLICATION_FACTOR', 2))

# Storage paths
DATANODE_DATA_DIR = os.getenv('DATANODE_DATA_DIR', 'data')
METADATA_FILE = os.getenv('METADATA_FILE', 'namenode/metadata.json')

# Heartbeat configuration
HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', 1))  # seconds
DATANODE_TIMEOUT = int(os.getenv('DATANODE_TIMEOUT', 2))  # seconds

# API endpoints
API_VERSION = 'v1'
NAMENODE_API_BASE = f'http://{NAMENODE_HOST}:{NAMENODE_PORT}/api/{API_VERSION}'

# DataNode endpoints
def get_datanode_api_base(host, port):
    return f'http://{host}:{port}/api/{API_VERSION}'