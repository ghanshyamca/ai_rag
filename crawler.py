"""
Web Crawler Module
Crawls a website and extracts text content from pages
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Set, List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebCrawler:
    """
    Crawls a website and extracts clean text from pages
    """
    
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
        
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid and within the same domain
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        parsed = urlparse(url)
        return (
            parsed.netloc == self.domain and
            parsed.scheme in ['http', 'https'] and
            url not in self.visited_urls
        )
    
    def extract_text(self, soup: BeautifulSoup) -> str:
        """
        Extract clean text from HTML
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Cleaned text content
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """
        Extract all links from a page
        
        Args:
            soup: BeautifulSoup object
            current_url: Current page URL
            
        Returns:
            List of absolute URLs
        """
        links = []
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(current_url, link['href'])
            # Remove fragments
            absolute_url = absolute_url.split('#')[0]
            if self.is_valid_url(absolute_url):
                links.append(absolute_url)
        return links
    
    def crawl_page(self, url: str) -> Dict[str, str]:
        """
        Crawl a single page
        
        Args:
            url: URL to crawl
            
        Returns:
            Dictionary with URL and text content
        """
        try:
            logger.info(f"Crawling: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            text = self.extract_text(soup)
            
            # Get page title
            title = soup.title.string if soup.title else url
            
            return {
                'url': url,
                'title': title,
                'content': text
            }
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
        
        while urls_to_visit and len(self.visited_urls) < self.max_pages:
            url = urls_to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
                
            self.visited_urls.add(url)
            
            # Crawl the page
            page_data = self.crawl_page(url)
            
            if page_data and page_data['content']:
                pages_data.append(page_data)
                
                # Extract new links
                try:
                    response = requests.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, 'lxml')
                    new_links = self.extract_links(soup, url)
                    urls_to_visit.extend(new_links)
                except Exception as e:
                    logger.error(f"Error extracting links from {url}: {str(e)}")
            
            # Be respectful - add delay
            time.sleep(self.delay)
        
        logger.info(f"Crawled {len(pages_data)} pages")
        return pages_data


if __name__ == "__main__":
    # Test the crawler
    from config import TARGET_URL, MAX_PAGES, CRAWL_DELAY
    
    crawler = WebCrawler(TARGET_URL, max_pages=MAX_PAGES, delay=CRAWL_DELAY)
    pages = crawler.crawl()
    
    print(f"\nCrawled {len(pages)} pages")
    if pages:
        print(f"\nFirst page preview:")
        print(f"URL: {pages[0]['url']}")
        print(f"Title: {pages[0]['title']}")
        print(f"Content length: {len(pages[0]['content'])} characters")
        print(f"Content preview: {pages[0]['content'][:200]}...")
