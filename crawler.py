"""
Web Crawler Module
Crawls a website and extracts clean text content from pages
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Set, List, Dict, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebCrawler:
    """
    Crawls a website and extracts clean text from pages
    """
    
    # HTML elements to remove (noise)
    NOISE_TAGS = [
        'script', 'style', 'nav', 'footer', 'header', 'aside',
        'form', 'button', 'iframe', 'noscript', 'svg', 'path',
        'meta', 'link'
    ]
    
    # Common class/id patterns for noise elements
    NOISE_PATTERNS = [
        r'nav', r'footer', r'header', r'sidebar', r'menu',
        r'cookie', r'banner', r'advertisement', r'ad-',
        r'social', r'share', r'breadcrumb', r'pagination',
        r'comment', r'related', r'popup', r'modal'
    ]
    
    def __init__(self, base_url: str, max_pages: int = 50, delay: float = 1.0):
        """
        Initialize the crawler
        
        Args:
            base_url: The starting URL to crawl
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.domain = urlparse(base_url).netloc
        self.pages_crawled = 0
        
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid and within the same domain
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        parsed = urlparse(url)
        
        # Skip common non-content URLs
        skip_extensions = ['.pdf', '.zip', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        return (
            parsed.netloc == self.domain and
            parsed.scheme in ['http', 'https'] and
            url not in self.visited_urls and
            not url.endswith('#')
        )
    
    def is_noise_element(self, element) -> bool:
        """
        Check if an element is likely noise based on class/id
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            True if element is noise, False otherwise
        """
        # Check element's class and id attributes
        classes = element.get('class', [])
        element_id = element.get('id', '')
        
        # Convert to strings for pattern matching
        class_str = ' '.join(classes) if isinstance(classes, list) else str(classes)
        
        # Check against noise patterns
        for pattern in self.NOISE_PATTERNS:
            if re.search(pattern, class_str, re.IGNORECASE):
                return True
            if re.search(pattern, element_id, re.IGNORECASE):
                return True
        
        return False
    
    def remove_noise_elements(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Remove noise elements from the soup
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Cleaned BeautifulSoup object
        """
        # Remove tags by name
        for tag in self.NOISE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements by class/id patterns
        for element in soup.find_all():
            if self.is_noise_element(element):
                element.decompose()
        
        # Remove hidden elements
        for element in soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden', re.IGNORECASE)):
            element.decompose()
        
        # Remove elements with aria-hidden="true"
        for element in soup.find_all(attrs={"aria-hidden": "true"}):
            element.decompose()
        
        return soup
    
    def extract_text(self, soup: BeautifulSoup) -> str:
        """
        Extract clean visible text from HTML
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Cleaned text content
        """
        # Remove noise elements
        soup = self.remove_noise_elements(soup)
        
        # Try to find main content area first
        main_content = None
        for selector in ['main', 'article', '[role="main"]', '.content', '#content', '.main']:
            main_content = soup.select_one(selector)
            if main_content:
                logger.debug(f"Found main content with selector: {selector}")
                break
        
        # Use main content if found, otherwise use body
        content_element = main_content if main_content else soup.find('body')
        if not content_element:
            content_element = soup
        
        # Get text
        text = content_element.get_text(separator=' ', strip=True)
        
        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """
        Extract page title
        
        Args:
            soup: BeautifulSoup object
            url: Page URL (fallback)
            
        Returns:
            Page title
        """
        # Try different title sources
        title = None
        
        # Try <title> tag
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        
        # Try h1 tag
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text().strip()
        
        # Try og:title meta tag
        if not title:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title = og_title['content'].strip()
        
        # Fallback to URL
        if not title:
            title = url
        
        # Clean title
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """
        Extract all valid links from a page
        
        Args:
            soup: BeautifulSoup object
            current_url: Current page URL
            
        Returns:
            List of absolute URLs
        """
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip javascript links and anchors
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue
            
            # Make URL absolute
            absolute_url = urljoin(current_url, href)
            
            # Remove fragments
            absolute_url = absolute_url.split('#')[0]
            
            # Remove trailing slashes for consistency
            absolute_url = absolute_url.rstrip('/')
            
            if self.is_valid_url(absolute_url):
                links.append(absolute_url)
        
        return list(set(links))  # Remove duplicates
    
    def crawl_page(self, url: str) -> Optional[Dict[str, str]]:
        """
        Crawl a single page and extract clean content
        
        Args:
            url: URL to crawl
            
        Returns:
            Dictionary with URL, title, and cleaned text content, or None on error
        """
        try:
            logger.info(f"Crawling [{self.pages_crawled + 1}/{self.max_pages}]: {url}")
            
            # Set user agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type.lower():
                logger.warning(f"Skipping non-HTML content: {url}")
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract clean text
            text = self.extract_text(soup)
            
            # Get page title
            title = self.extract_title(soup, url)
            
            # Log preview of cleaned text
            logger.info(f"  Title: {title}")
            logger.info(f"  Extracted {len(text)} characters of clean text")
            logger.debug(f"  Preview: {text[:150]}...")
            
            self.pages_crawled += 1
            
            return {
                'url': url,
                'title': title,
                'content': text,
                'content_length': len(text)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return None
    
    def crawl(self) -> List[Dict[str, str]]:
        """
        Crawl the website starting from base_url
        
        Returns:
            List of dictionaries containing page data
        """
        pages_data = []
        urls_to_visit = [self.base_url]
        
        logger.info(f"Starting crawl from {self.base_url}")
        logger.info(f"Max pages: {self.max_pages}, Delay: {self.delay}s")
        
        while urls_to_visit and len(self.visited_urls) < self.max_pages:
            url = urls_to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            # Crawl the page
            page_data = self.crawl_page(url)
            
            if page_data and page_data['content']:
                # Only store pages with meaningful content
                if len(page_data['content']) > 100:
                    pages_data.append(page_data)
                    
                    # Extract new links for further crawling
                    try:
                        response = requests.get(url, timeout=10, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        soup = BeautifulSoup(response.content, 'lxml')
                        new_links = self.extract_links(soup, url)
                        
                        # Add new links to queue
                        for link in new_links:
                            if link not in self.visited_urls and link not in urls_to_visit:
                                urls_to_visit.append(link)
                        
                        logger.debug(f"  Found {len(new_links)} new links")
                    except Exception as e:
                        logger.error(f"Error extracting links from {url}: {str(e)}")
                else:
                    logger.warning(f"Skipping page with insufficient content: {url}")
            
            # Be respectful - add delay between requests
            if urls_to_visit:  # Don't delay after the last page
                time.sleep(self.delay)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Crawling complete!")
        logger.info(f"Pages crawled: {len(pages_data)}")
        logger.info(f"URLs visited: {len(self.visited_urls)}")
        logger.info(f"{'='*60}\n")
        
        return pages_data


def test_crawler():
    """Test function to demonstrate crawler with detailed logging"""
    from config import TARGET_URL, MAX_PAGES, CRAWL_DELAY
    
    # Enable debug logging for testing
    logging.getLogger().setLevel(logging.INFO)
    
    print(f"\n{'='*60}")
    print("TESTING WEB CRAWLER")
    print(f"{'='*60}\n")
    
    crawler = WebCrawler(TARGET_URL, max_pages=min(5, MAX_PAGES), delay=CRAWL_DELAY)
    pages = crawler.crawl()
    
    print(f"\n{'='*60}")
    print("CRAWL RESULTS")
    print(f"{'='*60}\n")
    print(f"Total pages crawled: {len(pages)}\n")
    
    if pages:
        for i, page in enumerate(pages, 1):
            print(f"\n--- Page {i} ---")
            print(f"URL: {page['url']}")
            print(f"Title: {page['title']}")
            print(f"Content length: {page['content_length']} characters")
            print(f"\nContent preview (first 300 chars):")
            print("-" * 60)
            print(page['content'][:300])
            print("-" * 60)
            
            # Show more details for first page
            if i == 1:
                print(f"\nFull cleaned text for first page:")
                print("=" * 60)
                print(page['content'][:1000])
                if len(page['content']) > 1000:
                    print(f"\n... ({len(page['content']) - 1000} more characters)")
                print("=" * 60)


if __name__ == "__main__":
    test_crawler()
