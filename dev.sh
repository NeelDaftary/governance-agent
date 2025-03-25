#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Function to check if a port is in use
check_port() {
    if lsof -i :$1 > /dev/null; then
        echo "Error: Port $1 is already in use"
        exit 1
    fi
}

# Check if ports are available
check_port 8000
check_port 3000

# Store the backend PID
BACKEND_PID=""

# Cleanup function
cleanup() {
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Cleaning up backend process..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
}

# Set up cleanup trap
trap cleanup EXIT

echo "Starting FastAPI backend..."
cd "$SCRIPT_DIR"
PYTHONPATH="$SCRIPT_DIR" /Library/Frameworks/Python.framework/Versions/3.11/bin/uvicorn src.api:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..10}; do
    if curl -s http://localhost:8000/docs > /dev/null; then
        echo "Backend started successfully!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "Error: Backend failed to start"
        kill $BACKEND_PID
        exit 1
    fi
    sleep 1
done

# Start the Next.js frontend
echo "Starting Next.js frontend..."
cd frontend && npm run dev 