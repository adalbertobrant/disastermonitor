# src/config.py
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# --- API Keys & Secrets ---
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
FRED_API_KEY = os.getenv('FRED_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# --- Database ---
DATABASE_NAME = 'disaster_monitor.db'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', DATABASE_NAME) # Store in data/ folder

# --- Scraping ---
HEADLESS_BROWSER = True # Set to False for debugging scraper
SELENIUM_TIMEOUT = 90 # seconds to wait for page elements

SCRAPING_URLS = {
    "earthquake_usgs": "https://earthquake.usgs.gov/earthquakes/map/?extent=-85.22099,-175.78125&extent=85.22099,-20.03906", # More specific map view
    "noaa_hurricanes": "https://www.nhc.noaa.gov/",
    "noaa_weather_alerts": "https://www.weather.gov/alerts", # For US weather alerts
    "marketwatch_news": "https://www.marketwatch.com/latest-news",
    "investing_news": "https://www.investing.com/news/stock-market-news", # More specific news
    # Add more specific URLs, e.g., for Mississippi basin if available
    # "mississippi_flood_status": "https://water.weather.gov/ahps2/index.php?wfo=meg" # Example for a specific region
}

# --- LLM (Google Gemini) ---
GEMINI_MODEL_NAME = "gemini-1.5-flash" # Or other compatible models like gemini-1.5-flash
GEMINI_TEMPERATURE = 0.3 # better for precise high value more "creative"
GEMINI_MAX_OUTPUT_TOKENS = 2048

# --- Agent System ---
AGENT_ROLES = {
    "climatologist": "Expert in atmospheric patterns, flood risks, and extreme weather, focusing on events with potential economic impact, especially in the Mississippi River Basin.",
    "solar_specialist": "Expert in Coronal Mass Ejections (CME), solar flares, and their potential to disrupt communication, power grids, and financial systems.",
    "seismologist": "Expert in earthquake risk, tectonic shifts, and real-time seismic alerts, assessing impact on infrastructure and economic activity.",
    "insurance_analyst": "Models potential insurance claims, risk exposure, and reinsurance market impacts based on predicted disaster scenarios.",
    "disaster_economist": "Evaluates macroeconomic impacts of disasters, predicts market reactions, supply chain disruptions, and likely central bank/government responses. Synthesizes all agent inputs into a final economic recommendation."
}

# --- Logging ---
LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# --- System ---
MONITORING_CYCLE_INTERVAL_SECONDS = 3600 # 1 hour, adjust as needed

# --- Validation ---
def validate_config():
    required_vars = {
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "FRED_API_KEY": FRED_API_KEY,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
    }
    missing = [key for key, value in required_vars.items() if not value]
    if missing:
        msg = f"Missing critical environment variables: {', '.join(missing)}. Please check your .env file."
        logging.critical(msg)
        raise ValueError(msg)
    logging.info("Configuration loaded and validated.")

logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)
logger = logging.getLogger(__name__)

# Ensure data directory exists
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    logger.info(f"Created data directory: {data_dir}")

validate_config()
