#!/bin/bash
# Start Redis in the background
redis-server --requirepass "Admin123" &

# Wait for Redis to be ready
sleep 2

# Run Python script
python /app/sample_setup.py

# Keep container alive
tail -f /dev/null
