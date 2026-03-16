import logging
from bs4 import BeautifulSoup
import httpx
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class WebsiteCrawler:
    """
    2. ADVANCED WEBSITE CRAWLER
    """
    def __init__(self):
        # Only crawl these specific pages to limit depth
        self.target_paths = ["/", "/contact", "/contact-us", "/about", "/about-us", "/team"]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

    def _normalize_url(self, base: str, path: str) -> str:
        url = urljoin(base, path)
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    async def fetch_page(self, url: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                if response.status_code == 200:
                    return response.text
        except httpx.RequestError as e:
            logger.debug(f"Request failed for {url}: {e}")
        return ""

    async def crawl_website(self, base_url: str) -> dict:
        """
        Crawls homepage, contact, about, and team pages.
        Returns aggregated raw text to be passed to regex/extractors.
        """
        if not base_url.startswith("http"):
            base_url = "https://" + base_url
            
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        
        crawled_urls = set()
        aggregated_text = []
        found_links = []
        
        # Initial queue with target paths
        urls_to_crawl = [self._normalize_url(base_url, p) for p in self.target_paths]
        
        for url in urls_to_crawl:
            if url in crawled_urls:
                continue
                
            crawled_urls.add(url)
            html = await self.fetch_page(url)
            if not html:
                continue
                
            soup = BeautifulSoup(html, 'html.parser')
            # Kill scripts and styles for cleaner text extraction
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text(separator=' ')
            aggregated_text.append(text)
            
            # Look for social media links
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if any(social in href for social in ["linkedin.com", "facebook.com", "twitter.com", "instagram.com"]):
                    found_links.append(href)
                    
        return {
            "raw_text": " ".join(aggregated_text),
            "social_links": list(set(found_links))
        }

