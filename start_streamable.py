#!/usr/bin/env python3
"""
Custom startup script for streamable HTTP mode with proper host binding
"""
import os
import sys
from mind_map_server import MindMapServer

def main():
    # Force host binding
    os.environ['HOST'] = '0.0.0.0'
    os.environ['UVICORN_HOST'] = '0.0.0.0'
    
    # Create server and run
    server = MindMapServer()
    server.run_streamablehttp(host='0.0.0.0', port=8091)

if __name__ == "__main__":
    main()

