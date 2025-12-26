"""
Command-line interface for the RAG Retrieval Validation system.
"""
import argparse
import sys
from typing import List, Any


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="RAG Retrieval Validation CLI")
    parser.add_argument(
        "command",
        choices=["connect", "retrieve", "validate", "test", "run"],
        help="Command to execute: connect, retrieve, validate, test, or run (full pipeline)"
    )
    parser.add_argument("--query", type=str, help="Query text for retrieval/validation")
    parser.add_argument("--top-k", type=int, default=5, help="Number of top results to retrieve (default: 5)")
    parser.add_argument("--collection", type=str, help="Qdrant collection name")
    parser.add_argument("--expected-sources", nargs="*", help="Expected source URLs for validation")
    parser.add_argument("--config", type=str, help="Path to config file")
    
    args = parser.parse_args()
    
    try:
        if args.command == "run":
            # Full pipeline execution
            if not args.query:
                print("Error: --query is required for the 'run' command", file=sys.stderr)
                sys.exit(1)
            run_full_pipeline(args.query, args.top_k, args.collection, args.expected_sources)
        elif args.command == "connect":
            test_connection(args.collection)
        elif args.command == "retrieve":
            if not args.query:
                print("Error: --query is required for the 'retrieve' command", file=sys.stderr)
                sys.exit(1)
            perform_retrieval(args.query, args.top_k, args.collection)
        elif args.command == "validate":
            if not args.query or not args.expected_sources:
                print("Error: --query and --expected-sources are required for the 'validate' command", file=sys.stderr)
                sys.exit(1)
            perform_validation(args.query, args.expected_sources, args.top_k, args.collection)
        elif args.command == "test":
            run_tests()
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error executing command '{args.command}': {str(e)}", file=sys.stderr)
        sys.exit(1)


def run_full_pipeline(query: str, top_k: int, collection: str = None, expected_sources: List[str] = None):
    """Run the complete retrieval and validation pipeline."""
    print(f"Starting full pipeline for query: '{query}'")
    print(f"Top-K: {top_k}")
    if collection:
        print(f"Collection: {collection}")
    if expected_sources:
        print(f"Expected sources: {expected_sources}")
    
    # Import and run the main retrieve.py functionality
    from retrieve import main as retrieve_main
    import sys
    
    # Prepare command line arguments to simulate calling retrieve.py
    retrieve_args = [sys.argv[0], "--query", query, "--top-k", str(top_k)]
    if collection:
        retrieve_args.extend(["--collection", collection])
    if expected_sources:
        retrieve_args.extend(["--expected-sources"] + expected_sources)
    
    # Temporarily replace sys.argv to run the retrieve functionality
    original_argv = sys.argv
    sys.argv = retrieve_args
    
    try:
        from retrieve import main as retrieve_main
        result = retrieve_main()
        sys.exit(result)
    finally:
        sys.argv = original_argv


def test_connection(collection: str = None):
    """Test connection to Qdrant."""
    print(f"Testing connection to Qdrant")
    if collection:
        print(f"Collection: {collection}")
    
    from backend.src.services.qdrant_connection_service import QdrantConnectionService
    from backend.src.lib.config_loader import get_config
    
    try:
        config = get_config()
        collection_name = collection or config.get('QDRANT_COLLECTION_NAME', 'documents')
        
        connection_service = QdrantConnectionService()
        result = connection_service.connect(
            url=config['QDRANT_URL'],
            api_key=config['QDRANT_API_KEY'],
            collection_name=collection_name
        )
        
        if result:
            print("✓ Successfully connected to Qdrant")
        else:
            print("✗ Failed to connect to Qdrant")
    except Exception as e:
        print(f"✗ Connection test failed: {str(e)}")


def perform_retrieval(query: str, top_k: int, collection: str = None):
    """Perform retrieval based on query."""
    print(f"Performing retrieval for query: '{query}'")
    print(f"Top-K: {top_k}")
    if collection:
        print(f"Collection: {collection}")
    
    # This would implement the retrieval functionality
    print("Retrieval functionality would be implemented here")


def perform_validation(query: str, expected_sources: List[str], top_k: int, collection: str = None):
    """Perform validation against expected sources."""
    print(f"Performing validation for query: '{query}'")
    print(f"Expected sources: {expected_sources}")
    print(f"Top-K: {top_k}")
    if collection:
        print(f"Collection: {collection}")
    
    # This would implement the validation functionality
    print("Validation functionality would be implemented here")


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    
    import subprocess
    import os
    
    # Run pytest on the test directories
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                           cwd=os.getcwd(),
                           capture_output=True, 
                           text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    print(f"Tests completed with exit code: {result.returncode}")


if __name__ == "__main__":
    main()