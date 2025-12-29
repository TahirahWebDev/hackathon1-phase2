"""
Service for chunking content into appropriately sized segments.
"""
import re
from typing import List
from backend.src.models.document_chunk import DocumentChunk


class ChunkerService:
    """
    Service class for splitting content into appropriately sized chunks.
    Implements a recursive character text splitter that maintains semantic boundaries.
    """

    def __init__(self, chunk_size: int = 512, overlap: int = 20):
        """
        Initialize the chunker service.

        Args:
            chunk_size: Target size of chunks in tokens (default: 512)
            overlap: Overlap between chunks in tokens (default: 20)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_content(self, content: str, source_url: str, chunk_size: int = None, overlap: int = None) -> List[DocumentChunk]:
        """
        Splits content into appropriately sized chunks.

        Args:
            content: Content to be chunked
            source_url: Source URL for the content
            chunk_size: Target size of chunks in tokens (optional, uses default if not provided)
            overlap: Overlap between chunks in tokens (optional, uses default if not provided)

        Returns:
            List of DocumentChunk objects
        """
        # Use instance defaults if not provided
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.overlap

        # For this implementation, we'll use a simple approach based on character count
        # A more sophisticated approach would use token counting
        chunks = []

        # Split content into chunks based on the specified size
        start_idx = 0
        content_length = len(content)

        while start_idx < content_length:
            # Determine the end index for this chunk
            end_idx = start_idx + chunk_size

            # If this is not the last chunk, try to break at a sentence or paragraph boundary
            if end_idx < content_length:
                # Look for a good breaking point near the end of the chunk
                search_start = end_idx - overlap
                break_points = [
                    content.rfind('.', search_start, end_idx),
                    content.rfind('!', search_start, end_idx),
                    content.rfind('?', search_start, end_idx),
                    content.rfind('\n\n', search_start, end_idx),  # Paragraph break
                    content.rfind(' ', search_start, end_idx),     # Word boundary
                ]

                # Find the best breaking point (the one closest to the target without going over)
                valid_breaks = [bp for bp in break_points if bp > start_idx]
                if valid_breaks:
                    end_idx = max(valid_breaks) + 1  # +1 to include the punctuation/whitespace

            # Extract the chunk
            chunk_text = content[start_idx:end_idx]

            # Create a DocumentChunk
            from datetime import datetime
            chunk = DocumentChunk(
                id=f"chunk_{start_idx}_{end_idx}_{abs(hash(source_url)) % 10000}",
                content=chunk_text,
                source_url=source_url,
                created_at=datetime.now()
            )

            chunks.append(chunk)

            # Move to the next chunk, accounting for overlap
            start_idx = end_idx - overlap

            # If the next chunk would be empty, break
            if start_idx >= content_length:
                break

        return chunks