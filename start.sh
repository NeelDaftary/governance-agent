#!/bin/bash

# Start the backend server in the background
echo "Starting backend server..."
cd $(dirname "$0") && uvicorn src.api:app --reload &

# Wait for backend to start
sleep 2

# Start the frontend server
echo "Starting frontend server..."
cd frontend && npm run dev

# Kill background processes when script is terminated
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT 