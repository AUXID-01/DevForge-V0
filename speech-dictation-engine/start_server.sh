#!/bin/bash
# Start Integration Server

echo "======================================================================"
echo "GRAMMAR STAGE (PERSON C) - INTEGRATION SERVER"
echo "======================================================================"
echo ""
echo "Starting server on port 8000..."
echo "Your endpoint: http://localhost:8000/process"
echo ""
echo "Person B should POST messages to this endpoint."
echo "Messages will be forwarded to Person D after processing."
echo ""
echo "======================================================================"
echo ""

# Activate venv and start server
source venv/bin/activate
python src/integration_server.py
