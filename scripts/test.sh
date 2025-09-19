#!/bin/bash

# Test script for HDFS system
set -e

echo "🧪 Running HDFS System Tests..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./scripts/start-dev.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run Python tests
echo "🐍 Running Python tests..."
if [ -f "test_hdfs.py" ]; then
    python test_hdfs.py
    echo "✅ Python tests completed"
else
    echo "⚠️  No Python test file found"
fi

# Run frontend tests
echo "⚛️  Running frontend tests..."
cd hdfs-frontend

if [ -f "package.json" ]; then
    # Check if test script exists
    if npm run | grep -q "test"; then
        npm test
        echo "✅ Frontend tests completed"
    else
        echo "⚠️  No frontend test script found"
    fi
    
    # Run linting
    if npm run | grep -q "lint"; then
        echo "🔍 Running frontend linting..."
        npm run lint
        echo "✅ Frontend linting completed"
    fi
else
    echo "⚠️  No frontend package.json found"
fi

cd ..

echo ""
echo "🎉 All tests completed!"
