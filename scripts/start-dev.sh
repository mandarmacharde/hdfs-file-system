#!/bin/bash

# Development startup script for HDFS system
set -e

echo "🚀 Starting HDFS Development Environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
cd hdfs-frontend
npm install
cd ..

# Create data directories if they don't exist
echo "📁 Creating data directories..."
mkdir -p data/datanode1 data/datanode2

# Start services in background
echo "🎯 Starting NameNode..."
source venv/bin/activate && python3 -m namenode.main &
NAMENODE_PID=$!

# Wait for NameNode to start
sleep 3

echo "🎯 Starting DataNode 1..."
source venv/bin/activate && python3 -m datanode.datanode --port 5001 --data_dir ./data/datanode1 &
DATANODE1_PID=$!

echo "🎯 Starting DataNode 2..."
source venv/bin/activate && python3 -m datanode.datanode --port 5002 --data_dir ./data/datanode2 &
DATANODE2_PID=$!

# Wait for DataNodes to start
sleep 3

echo "🎯 Starting Frontend..."
cd hdfs-frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ All services started!"
echo ""
echo "🌐 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   NameNode API: http://localhost:5050"
echo "   DataNode 1: http://localhost:5001"
echo "   DataNode 2: http://localhost:5002"
echo ""
echo "📊 Process IDs:"
echo "   NameNode: $NAMENODE_PID"
echo "   DataNode 1: $DATANODE1_PID"
echo "   DataNode 2: $DATANODE2_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "🛑 To stop all services, run: ./scripts/stop-dev.sh"
echo "   Or press Ctrl+C and run: kill $NAMENODE_PID $DATANODE1_PID $DATANODE2_PID $FRONTEND_PID"

# Save PIDs for cleanup
echo "$NAMENODE_PID $DATANODE1_PID $DATANODE2_PID $FRONTEND_PID" > .dev_pids

# Wait for user interrupt
trap 'echo "🛑 Stopping services..."; kill $NAMENODE_PID $DATANODE1_PID $DATANODE2_PID $FRONTEND_PID 2>/dev/null; rm -f .dev_pids; exit 0' INT

wait
