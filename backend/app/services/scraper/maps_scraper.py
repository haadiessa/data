from playwright.async_api import async_playwright
import asyncio
import logging

logger = logging.getLogger(__name__)

class GoogleMapsScraper:
    """
    1. BUSINESS DISCOVERY MODULE (Google Maps Scraper)
    Extracts Data from Google Maps using Playwright for dynamic JS rendering.
    """
    def __init__(self):
        self.base_url = "https://www.google.com/maps/search/"

    async def _extract_business_data(self, page) -> list:
        """
        Parses the search results pane in Google Maps to extract listings.
        Note: Exact selectors often change, so these are resilient logic approximations.
        """
        results = []
        # Wait for either results or a single business pane to load
        try:
            await page.wait_for_selector('a[href*="/maps/place/"]', timeout=5000)
        except Exception:
            logger.warning("No map results found or timeout reached.")
            return results

        # Get all business listing links in the side panel
        links = await page.locator('a[href*="/maps/place/"]').all()
        
        parsed_urls = set()
        
        for link in links:
            href = await link.get_attribute('href')
            if href in parsed_urls:
                continue
            parsed_urls.add(href)
            
            # Extract name from the aria-label of the link
            name = await link.get_attribute('aria-label')
            
            # We would typically click each listing or parse the immediate container 
            # for address, phone, website, and rating.
            # For this MVP implementation level, we'll return the name and maps link
            # which can then be further enriched.
            
            if name:
                results.append({
                    "name": name,
                    "maps_link": href,
                    "category": "Unknown", # Needs deeper clicking
                    "address": "Unknown",  # Needs deeper clicking
                })
        
        return results

    async def discover_businesses(self, niche: str, location: str, max_results: int = 10) -> list:
        """
        Main entry point for business discovery via Maps.
        """
        query = f"{niche} in {location}"
        search_url = f"{self.base_url}{query.replace(' ', '+')}"
        
        logger.info(f"Scraping Maps for: {query}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                await page.goto(search_url, wait_until="networkidle")
                
                # Deal with cookie consent if in EU (often needed)
                try:
                    accept_button = page.locator("button:has-text('Accept all')")
                    if await accept_button.is_visible():
                        await accept_button.click()
                except Exception:
                    pass
                
                # Scroll the results pane to load more (Pagination logic)
                # In a full implementation, we'd scroll the specific `div.m6QErb` container
                
                businesses = await self._extract_business_data(page)
                
                # Limit to requested amount
                return businesses[:max_results]
                
            finally:
                await browser.close()
