#!/usr/bin/env python3
"""
Script to reset Qdrant collection by deleting it.
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Load environment variables
load_dotenv()

# Get configuration from environment
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = os.getenv("QDRANT_COLLECTION_NAME", "documents")  # Default to 'documents'

if not qdrant_url or not qdrant_api_key:
    print("Error: QDRANT_URL and QDRANT_API_KEY must be set in your .env file")
    exit(1)

print(f"Connecting to Qdrant at: {qdrant_url}")
print(f"Using collection: {collection_name}")

try:
    # Create Qdrant client
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        prefer_grpc=False
    )

    # Check if collection exists
    collections = client.get_collections()
    collection_names = [collection.name for collection in collections.collections]
    
    if collection_name in collection_names:
        print(f"Found collection '{collection_name}', deleting it...")
        
        # Delete the collection
        client.delete_collection(collection_name)
        
        print(f"Collection '{collection_name}' has been deleted successfully!")
    else:
        print(f"Collection '{collection_name}' does not exist.")
        
    # Show remaining collections
    collections = client.get_collections()
    remaining_collections = [collection.name for collection in collections.collections]
    print(f"Remaining collections: {remaining_collections}")

except Exception as e:
    print(f"Error: {str(e)}")