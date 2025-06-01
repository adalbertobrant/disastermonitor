# src/scraper.py
import logging
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager # Option 1: Manage driver automatically
from src.config import HEADLESS_BROWSER, SELENIUM_TIMEOUT, FRED_API_KEY

logger = logging.getLogger(__name__)

# Option 2: Specify chromedriver path if not using webdriver-manager
# This is often better for Docker environments where you install it explicitly.
# CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver" # Example path, adjust if needed

def get_selenium_driver():
    """Initializes and returns a Selenium WebDriver."""
    options = Options()
    if HEADLESS_BROWSER:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox') # Crucial for running in Docker/Linux as root
    options.add_argument('--disable-dev-shm-usage') # Overcomes limited resource problems
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36") # Common user agent

    try:
        # Option 1: Use webdriver-manager (uncomment import above)
        # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Option 2: Use a pre-installed chromedriver (more common for Docker)
        # Ensure CHROMEDRIVER_PATH is correct or chromedriver is in PATH
        driver = webdriver.Chrome(options=options) # Assumes chromedriver is in PATH
        # If not in PATH, specify executable_path with Service:
        # driver = webdriver.Chrome(service=Service(executable_path=CHROMEDRIVER_PATH), options=options)
        
        driver.set_page_load_timeout(SELENIUM_TIMEOUT)
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Selenium WebDriver: {e}. Check chromedriver installation/path.", exc_info=True)
        # If using webdriver-manager, it might be a download issue.
        # If using fixed path, ensure it's correct and executable.
        raise

def get_page_content_selenium(url: str) -> str:
    """Fetches page content using Selenium for JS-heavy sites."""
    driver = None
    try:
        driver = get_selenium_driver()
        driver.get(url)
        # Wait for dynamic content to load. This is a generic wait.
        # For specific sites like Toro, more sophisticated waits for specific elements are needed.
        time.sleep(5) # Adjust as needed, or implement WebDriverWait
        page_source = driver.page_source
        logger.info(f"Successfully fetched content from {url} using Selenium.")
        return page_source
    except Exception as e:
        logger.error(f"Error fetching page {url} with Selenium: {e}", exc_info=True)
        return ""
    finally:
        if driver:
            driver.quit()

def get_page_content_requests(url: str) -> str:
    """Fetches page content using requests for static sites."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=SELENIUM_TIMEOUT)
        response.raise_for_status() # Raise an exception for HTTP errors
        logger.info(f"Successfully fetched content from {url} using requests.")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching page {url} with requests: {e}", exc_info=True)
        return ""

def extract_text_from_html(html_content: str, max_length: int = 1500) -> str:
    """Extracts clean text from HTML content."""
    if not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text[:max_length]
    except Exception as e:
        logger.warning(f"Could not parse HTML: {e}")
        return html_content[:max_length] # return raw snippet if parsing fails


def fetch_fred_data(series_id: str = "FEDFUNDS") -> str:
    """Fetches data from FRED API for a given series."""
    if not FRED_API_KEY:
        logger.warning("FRED_API_KEY not set. Skipping FRED data.")
        return "FRED data not available (API key missing)."
    try:
        # Example: Get latest observation for Federal Funds Rate
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=5"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        observations = data.get("observations", [])
        if observations:
            # Format for better readability by LLM
            formatted_obs = [f"{obs['date']}: {obs['value']}" for obs in observations]
            return f"Recent {series_id} observations: {'; '.join(formatted_obs)}"
        logger.info(f"Fetched FRED data for {series_id}")
        return f"No recent observations found for {series_id}."
    except requests.RequestException as e:
        logger.error(f"Error fetching FRED data for {series_id}: {e}", exc_info=True)
        return f"Error fetching FRED data for {series_id}."
    except Exception as e:
        logger.error(f"Unexpected error processing FRED data for {series_id}: {e}", exc_info=True)
        return f"Error processing FRED data for {series_id}."
