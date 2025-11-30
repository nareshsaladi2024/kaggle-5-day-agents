"""
Run the Product Catalog Agent as an A2A server.

This script starts the Product Catalog Agent server that will be consumed
by the Customer Support Agent via A2A protocol.

Usage:
    python run_product_catalog_server.py

The server will run on http://localhost:8001 by default.
You can change the port by setting PRODUCT_CATALOG_PORT environment variable.
"""

import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the agent app
from Day5a.ProductCatalogAgent.agent import app

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PRODUCT_CATALOG_PORT", "8001"))
    host = os.getenv("PRODUCT_CATALOG_HOST", "localhost")
    
    print("=" * 60)
    print("Product Catalog Agent - A2A Server")
    print("=" * 60)
    print(f"Starting server on http://{host}:{port}")
    print(f"Agent card: http://{host}:{port}/.well-known/agent-card.json")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

