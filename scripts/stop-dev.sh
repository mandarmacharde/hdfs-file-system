#!/bin/bash

# Development stop script for HDFS system

echo "🛑 Stopping HDFS Development Environment..."

# Read PIDs from file
if [ -f ".dev_pids" ]; then
    PIDS=$(cat .dev_pids)
    echo "🔍 Found running processes: $PIDS"
    
    # Kill processes
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then
            echo "🔄 Stopping process $pid..."
            kill $pid
        fi
    done
    
    # Clean up PID file
    rm -f .dev_pids
    echo "✅ All services stopped!"
else
    echo "⚠️  No PID file found. Attempting to stop by process name..."
    
    # Kill by process name
    pkill -f "namenode.main" 2>/dev/null || true
    pkill -f "datanode.datanode" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    
    echo "✅ Attempted to stop all services!"
fi

echo "🧹 Cleanup complete!"
