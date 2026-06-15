# HDFS File System - Distributed File Storage System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)

A production-ready implementation of a Hadoop Distributed File System (HDFS) with a modern React frontend interface. This system demonstrates core principles of distributed file storage, block management, replication, and metadata handling with Docker support and comprehensive monitoring.

## 🏗️ System Architecture

The system consists of four main components:

### Backend Components

1. **NameNode (Master Node)** - `namenode/`
   - Maintains metadata: File → Block → DataNode mapping
   - Handles client requests for file operations
   - Assigns DataNodes for block storage
   - Tracks DataNode health via heartbeats
   - Provides REST API for frontend communication

2. **DataNodes (Worker Nodes)** - `datanode/`
   - Store actual file blocks as local files
   - Respond to read/write block requests
   - Send periodic heartbeat signals to NameNode
   - Handle block replication

3. **Client Library** - `client/`
   - Provides programmatic interface for file operations
   - Communicates with NameNode for metadata
   - Directly sends/receives blocks to/from DataNodes

### Frontend Component

4. **Web Interface** - `hdfs-frontend/`
   - Modern React-based dashboard
   - Real-time file management
   - System monitoring and statistics
   - Drag-and-drop file upload
   - Interactive file browser

## ✨ Features

### Core Features
- **File Upload/Download**: Complete file operations with block splitting and reassembly
- **Block Replication**: Fault tolerance through data replication across multiple DataNodes
- **Health Monitoring**: Real-time DataNode status tracking via heartbeat mechanism
- **Metadata Management**: Persistent storage of file system metadata
- **Statistics Tracking**: Upload/download counters and system metrics

### Frontend Features
- **Dashboard**: Real-time system statistics and monitoring
- **File Browser**: Interactive file management with upload/download capabilities
- **DataNode Monitoring**: Live status of all DataNodes in the system
- **Responsive Design**: Modern Material-UI interface with dark theme support
- **Real-time Updates**: Live statistics and file system changes

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker & Docker Compose (for containerized deployment)
- Git

### Option 1: Development Setup (Recommended for contributors)

1. **Clone the repository**
   ```bash
   git clone https://github.com/mandarmacharde/hdfs-file-system.git
   cd hdfs-file-system
   ```

2. **Start development environment**
   ```bash
   ./scripts/start-dev.sh
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5050

### Option 2: Docker Deployment (Recommended for production)

1. **Clone and deploy**
   ```bash
   git clone https://github.com/mandarmacharde/hdfs-file-system.git
   cd hdfs-file-system
   ./scripts/deploy.sh
   ```

2. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5050

### Option 3: Manual Setup

1. **Set up Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up frontend**
   ```bash
   cd hdfs-frontend
   npm install
   cd ..
   ```

3. **Start services manually**
   ```bash
   # Terminal 1 - NameNode
   source venv/bin/activate && python3 -m namenode.main
   
   # Terminal 2 - DataNode 1
   source venv/bin/activate && python3 -m datanode.datanode --port 5001 --data_dir ./data/datanode1
   
   # Terminal 3 - DataNode 2
   source venv/bin/activate && python3 -m datanode.datanode --port 5002 --data_dir ./data/datanode2
   
   # Terminal 4 - Frontend
   cd hdfs-frontend && npm run dev
   ```

## 📁 Project Structure

```
hdfs-file-system/
├── 📁 Backend Components
│   ├── namenode/                    # NameNode (Master)
│   │   ├── main.py                 # NameNode server implementation
│   │   ├── metadata.py             # Metadata management
│   │   └── metadata.json           # Persistent metadata storage
│   │
│   ├── datanode/                   # DataNode (Worker)
│   │   ├── datanode.py             # DataNode server implementation
│   │   └── block_storage.py        # Block storage management
│   │
│   ├── client/                     # Client Library
│   │   ├── client.py               # Client interface
│   │   └── file_operations.py      # File splitting and reassembly
│   │
│   └── common/                     # Shared Components
│       ├── config.py               # Configuration settings
│       └── utils.py                # Utility functions
│
├── 📁 Frontend Components
│   └── hdfs-frontend/              # React Web Interface
│       ├── src/
│       │   ├── components/         # React Components
│       │   │   ├── Dashboard/      # System dashboard
│       │   │   ├── DataNodes/      # DataNode monitoring
│       │   │   ├── FileBrowser/    # File management
│       │   │   ├── Layout/         # UI layout components
│       │   │   └── Upload/         # File upload interface
│       │   ├── pages/              # Page components
│       │   ├── services/           # API services
│       │   ├── theme/              # UI theme configuration
│       │   └── utils/              # Frontend utilities
│       ├── Dockerfile              # Frontend container
│       ├── nginx.conf              # Nginx configuration
│       ├── package.json            # Frontend dependencies
│       └── vite.config.ts          # Vite configuration
│
├── 📁 Data Storage
│   └── data/                       # DataNode storage directories
│       ├── datanode1/              # DataNode 1 storage
│       │   └── .gitkeep            # Keep directory in git
│       └── datanode2/              # DataNode 2 storage
│           └── .gitkeep            # Keep directory in git
│
├── 📁 Scripts & Automation
│   └── scripts/                    # Development and deployment scripts
│       ├── start-dev.sh            # Development environment startup
│       ├── stop-dev.sh             # Development environment shutdown
│       ├── deploy.sh               # Production deployment
│       └── test.sh                 # Test runner
│
├── 📁 Docker & Deployment
│   ├── docker-compose.yml          # Multi-container setup
│   ├── Dockerfile.namenode         # NameNode container
│   ├── Dockerfile.datanode         # DataNode container
│   └── .env.example                # Environment template
│
├── 📁 CI/CD & Quality
│   └── .github/
│       └── workflows/
│           └── ci.yml              # GitHub Actions pipeline
│
├── 📁 Documentation
│   ├── README.md                   # This file
│   ├── CONTRIBUTING.md             # Contribution guidelines
│   ├── CHANGELOG.md                # Version history
│   └── LICENSE                     # MIT License
│
├── 📁 Configuration
│   ├── requirements.txt            # Python dependencies
│   ├── .gitignore                  # Git ignore rules
│   └── test_hdfs.py                # System tests
│
└── 📁 Virtual Environment (ignored)
    └── venv/                       # Python virtual environment
```

## 🔧 Configuration

### Backend Configuration
- **Block Size**: 1MB (configurable in `common/config.py`)
- **Replication Factor**: 2 (configurable in `common/config.py`)
- **NameNode Port**: 5050 (default)
- **DataNode Ports**: 5001, 5002 (configurable)
- **Heartbeat Interval**: 10 seconds
- **DataNode Timeout**: 30 seconds

### Frontend Configuration
- **Development Server**: http://localhost:5173
- **API Base URL**: http://localhost:5050/api/v1
- **Theme**: Material-UI with dark mode support
- **Build Tool**: Vite

## 🛠️ API Endpoints

### NameNode API (Port 5050)

#### File Operations
- `GET /api/v1/files` - List all files
- `GET /api/v1/files/{filename}` - Get file information
- `POST /api/v1/files/upload` - Upload a file
- `DELETE /api/v1/files/{filename}` - Delete a file
- `POST /api/v1/files/{filename}/log_download` - Log download event

#### System Information
- `GET /api/v1/stats` - Get system statistics
- `GET /api/v1/datanodes` - List active DataNodes
- `GET /api/v1/storage` - Get storage information

#### DataNode Management
- `POST /api/v1/datanodes/register` - Register a DataNode
- `POST /api/v1/datanodes/heartbeat` - DataNode heartbeat

### DataNode API (Ports 5001, 5002)
- `PUT /api/v1/blocks/{block_id}` - Store a block
- `GET /api/v1/blocks/{block_id}` - Retrieve a block
- `GET /api/v1/info` - Get DataNode information

## 🎯 Usage Examples

### Using the Web Interface
1. Open http://localhost:5173 in your browser
2. Navigate to the Dashboard to view system statistics
3. Use the Upload page to upload files via drag-and-drop
4. Browse files in the Files page
5. Monitor DataNode status in the DataNodes page

### Using the Client Library
```python
from client.client import HDFSClient

# Initialize client
client = HDFSClient()

# Upload a file
client.upload_file("myfile.txt")

# Download a file
client.download_file("myfile.txt")

# List files
files = client.list_files()
```

### Using the API directly
```bash
# Upload a file
curl -X POST -F "file=@myfile.txt" http://localhost:5050/api/v1/files/upload

# Get system stats
curl http://localhost:5050/api/v1/stats

# List files
curl http://localhost:5050/api/v1/files
```

## 🔍 Monitoring and Statistics

The system provides comprehensive monitoring through:

### Dashboard Metrics
- **Total Files**: Number of files in the system
- **Active DataNodes**: Number of healthy DataNodes
- **Total Uploads**: Cumulative upload count
- **Total Downloads**: Cumulative download count

### Real-time Monitoring
- DataNode heartbeat status
- Block replication status
- Storage utilization
- File system health

## 🧪 Testing

### Quick Test
```bash
# Run all tests
./scripts/test.sh
```

### Individual Testing
```bash
# Backend tests
source venv/bin/activate && python test_hdfs.py

# Frontend tests
cd hdfs-frontend
npm run lint        # Run ESLint
npm run build       # Build for production
npm run preview     # Preview production build
```

### Docker Testing
```bash
# Test Docker setup
docker-compose config
docker-compose build
docker-compose up -d
./scripts/test.sh
docker-compose down
```

## 🚀 Development

### Backend Development
- **Framework**: Flask with CORS support
- **Communication**: HTTP REST APIs
- **Metadata Storage**: JSON file persistence
- **Threading**: Background tasks for monitoring

### Frontend Development
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI)
- **Build Tool**: Vite
- **State Management**: React hooks
- **Styling**: Emotion + Styled Components
- **Animations**: Framer Motion

## ⚠️ Limitations

This is a simplified prototype for educational purposes with the following limitations:

- **Security**: No authentication or authorization
- **Scalability**: Limited to small-scale deployments
- **Fault Tolerance**: Basic replication without advanced recovery
- **Performance**: Not optimized for high-throughput scenarios
- **Persistence**: Simple JSON-based metadata storage

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Start for Contributors
1. Fork the repository
2. Clone your fork: `git clone https://github.com/mandarmacharde/hdfs-file-system.git`
3. Start development: `./scripts/start-dev.sh`
4. Make your changes
5. Run tests: `./scripts/test.sh`
6. Submit a pull request

### Development Workflow
- Use conventional commit messages
- Follow the code style guidelines
- Add tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Additional Resources

- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [API Documentation](docs/api.md) (coming soon)
- [Deployment Guide](docs/deployment.md) (coming soon)

## 🔗 Related Technologies

- **Hadoop HDFS**: The inspiration for this implementation
- **Apache Kafka**: For distributed messaging
- **Apache Spark**: For distributed processing
- **Docker**: For containerization
- **Kubernetes**: For orchestration

---

**Note**: This system is designed for learning and demonstration purposes. For production use, consider using established distributed file systems like Hadoop HDFS, Ceph, or GlusterFS.
