"""
Service for cleaning text content extracted from Docusaurus websites.
"""
import re


class TextCleanerService:
    """
    Service class for cleaning text content extracted from Docusaurus websites.
    Uses BeautifulSoup to extract text while preserving important structural elements like code blocks.
    """

    def __init__(self):
        """
        Initialize the text cleaner service.
        """
        pass

    def clean_content(self, raw_content: str, source_url: str) -> str:
        """
        Cleans raw HTML content and extracts clean text.

        Args:
            raw_content: Raw HTML content string
            source_url: Source URL for context

        Returns:
            Clean text content with preserved formatting
        """
        if not raw_content:
            return ""

        from bs4 import BeautifulSoup

        # Parse the HTML content
        soup = BeautifulSoup(raw_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Try to find main content area (common in Docusaurus sites)
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'container|content|doc')) or soup

        # Clean up the content
        cleaned_text = self._extract_text_with_formatting(main_content)

        # Normalize whitespace
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)  # Remove excessive newlines
        cleaned_text = cleaned_text.strip()

        return cleaned_text

    def _extract_text_with_formatting(self, soup_element) -> str:
        """
        Extract text from soup element while preserving some formatting.

        Args:
            soup_element: BeautifulSoup element to extract text from

        Returns:
            Text content with some formatting preserved
        """
        if soup_element is None:
            return ""

        from bs4 import BeautifulSoup
        import re

        # Handle different types of elements
        result = []

        for element in soup_element.descendants:
            if element.name == 'code':
                # Preserve code blocks
                result.append(f"`{element.get_text()}`")
            elif element.name == 'pre':
                # Preserve preformatted text (code blocks)
                result.append(f"\n```\n{element.get_text()}\n```\n")
            elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Preserve headings
                result.append(f"\n{element.get_text()}\n")
            elif element.name in ['p', 'div', 'li', 'td']:
                # Regular text blocks
                text = element.get_text().strip()
                if text:
                    result.append(text)
            elif element.name in ['br', 'hr']:
                # Line breaks
                result.append('\n')
            elif element.name is None:  # Text node
                text = element.strip()
                if text:
                    result.append(text)

        # Join the text segments
        text_content = ' '.join(result)

        # Clean up multiple spaces
        text_content = re.sub(r' +', ' ', text_content)

        return text_content