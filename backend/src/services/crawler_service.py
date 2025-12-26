"""
Service for crawling Docusaurus websites and extracting content.
"""
from typing import List
from backend.src.models.crawled_page import CrawledPage
from backend.src.lib.exceptions import CrawlerError
import xml.etree.ElementTree as ET


class CrawlerService:
    """
    Service class for crawling Docusaurus websites and extracting content.
    """

    def __init__(self):
        """
        Initialize the crawler service.
        """
        pass

    def crawl_urls(self, urls: List[str]) -> List[CrawledPage]:
        """
        Crawls a list of URLs and returns the crawled page data.

        Args:
            urls: List of URLs to crawl

        Returns:
            List of CrawledPage objects with content and metadata

        Raises:
            CrawlerError: If crawling fails for any URL
        """
        # First, check if any of the URLs have sitemaps and extract additional URLs
        all_urls = set()
        for url in urls:
            all_urls.add(url)
            sitemap_urls = self._extract_urls_from_sitemap(url)
            all_urls.update(sitemap_urls)

        crawled_pages = []
        for url in all_urls:
            try:
                crawled_page = self._crawl_single_url(url)
                crawled_pages.append(crawled_page)
            except Exception as e:
                # Create a crawled page with error information
                from datetime import datetime
                crawled_page = CrawledPage(
                    id=f"crawl_error_{hash(url)}",
                    url=url,
                    raw_content="",
                    clean_content="",
                    title="",
                    status_code=0,
                    created_at=datetime.now(),
                    crawled_at=datetime.now(),
                    error_message=str(e),
                    metadata={}
                )
                crawled_pages.append(crawled_page)

        return crawled_pages

    def _extract_urls_from_sitemap(self, base_url: str) -> List[str]:
        """
        Extract all URLs from the sitemap.xml of the given base URL.

        Args:
            base_url: The base URL to check for sitemap.xml

        Returns:
            List of URLs found in the sitemap
        """
        import requests
        from urllib.parse import urljoin, urlparse

        # Construct sitemap URL
        parsed_url = urlparse(base_url)
        sitemap_url = f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml"

        try:
            response = requests.get(sitemap_url, timeout=30)
            if response.status_code == 200:
                # Parse the sitemap XML
                root = ET.fromstring(response.content)

                # Handle both regular sitemap and sitemap index formats
                urls = []

                # Check if it's a sitemap index (contains other sitemaps)
                if root.tag.endswith('sitemapindex'):
                    # Extract URLs from nested sitemaps
                    for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap/{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        nested_sitemap_url = sitemap.text.strip()
                        nested_urls = self._extract_urls_from_sitemap(nested_sitemap_url)
                        urls.extend(nested_urls)
                else:
                    # Regular sitemap with URLs
                    for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        urls.append(url.text.strip())

                return urls
            else:
                print(f"No sitemap found at {sitemap_url}, status code: {response.status_code}")
                return []
        except ET.ParseError:
            print(f"Could not parse sitemap at {sitemap_url}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching sitemap from {sitemap_url}: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error processing sitemap from {sitemap_url}: {str(e)}")
            return []

    def _crawl_single_url(self, url: str) -> CrawledPage:
        """
        Crawl a single URL and return a CrawledPage object.

        Args:
            url: URL to crawl

        Returns:
            CrawledPage object with content and metadata
        """
        import requests
        from bs4 import BeautifulSoup
        import re
        from urllib.parse import urljoin, urlparse
        from datetime import datetime

        try:
            response = requests.get(url, timeout=30)
            status_code = response.status_code

            if status_code != 200:
                raise CrawlerError(f"HTTP {status_code} error when crawling {url}")

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ""

            # Clean up the soup to extract just the main content
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Try to find main content area (common in Docusaurus sites)
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'container|content|doc')) or soup

            # Extract clean text content
            clean_content = main_content.get_text(separator=' ', strip=True)

            # Create a unique ID based on the URL
            page_id = f"page_{hash(url)}"

            # Create and return CrawledPage object
            return CrawledPage(
                id=page_id,
                url=url,
                raw_content=response.text,
                clean_content=clean_content,
                title=title,
                status_code=status_code,
                created_at=datetime.now(),
                crawled_at=datetime.now(),
                metadata={}
            )

        except requests.exceptions.RequestException as e:
            raise CrawlerError(f"Network error when crawling {url}: {str(e)}")
        except Exception as e:
            raise CrawlerError(f"Unexpected error when crawling {url}: {str(e)}")