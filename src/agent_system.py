# src/agent_system.py
import logging
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import AGENT_ROLES, SCRAPING_URLS, MONITORING_CYCLE_INTERVAL_SECONDS
from src.database import init_db, store_scenario
from src.llm_adapter import GeminiAdapter, generate_agent_prompt
from src.scraper import get_page_content_selenium, extract_text_from_html, fetch_fred_data
from src.utils import send_telegram_alert

logger = logging.getLogger(__name__)

class IntelligentMonitor:
    def __init__(self):
        self.llm_adapter = GeminiAdapter()
        init_db() # Ensure DB is ready

    def _scrape_source(self, site_name: str, url: str) -> tuple[str, str]:
        """Scrapes a single source. Uses Selenium for now.
        Could be extended to choose scraper based on URL or site needs.
        """
        logger.info(f"Scraping {site_name} from {url}...")
        # For now, default to Selenium. Could add logic to use requests for simpler sites.
        # For "Toro Investimentos" or similar complex financial platforms,
        # this would need significant enhancement:
        # - Login handling (securely)
        # - WebDriverWait for specific dynamic elements
        # - Navigating through menus/tabs
        # - Potentially handling CAPTCHAs (very advanced, often needs 3rd party services)
        # - More robust error handling for site-specific issues
        html_content = get_page_content_selenium(url)
        if html_content:
            text_content = extract_text_from_html(html_content)
            return site_name, text_content
        return site_name, f"Failed to retrieve content from {site_name}."

    def gather_initial_context(self) -> str:
        """Gathers initial context from web sources and APIs."""
        logger.info("Gathering initial context...")
        contexts = {}
        
        # Web scraping with ThreadPoolExecutor for parallelism
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self._scrape_source, name, url): name for name, url in SCRAPING_URLS.items()}
            for future in as_completed(future_to_url):
                site_name = future_to_url[future]
                try:
                    _, content = future.result()
                    contexts[site_name] = content
                except Exception as exc:
                    logger.error(f"{site_name} generated an exception during scraping: {exc}", exc_info=True)
                    contexts[site_name] = f"Error scraping {site_name}."

        # FRED Data
        fred_gdp = fetch_fred_data("GDP")
        fred_fedfunds = fetch_fred_data("FEDFUNDS")
        fred_cpi = fetch_fred_data("CPIAUCSL") # Consumer Price Index

        full_context = "Collected Real-Time Data:\n\n"
        for source, text in contexts.items():
            full_context += f"--- {source.upper()} ---\n{text}\n\n"
        
        full_context += f"--- FRED ECONOMIC DATA ---\n"
        full_context += f"{fred_gdp}\n{fred_fedfunds}\n{fred_cpi}\n"
        
        logger.info("Initial context gathering complete.")
        # logger.debug(f"Full context: {full_context[:1000]}...") # Log a snippet
        return full_context

    def run_agent_analysis(self, agent_name: str, agent_role: str, current_context: str, previous_insights_str: str) -> tuple[str, str]:
        """Runs a single agent's analysis."""
        logger.info(f"Running analysis for agent: {agent_name} ({agent_role})")
        prompt = generate_agent_prompt(agent_role, current_context, previous_insights_str)
        
        try:
            analysis = self.llm_adapter.generate_text(prompt)
            logger.info(f"Agent {agent_name} analysis received.")
            # logger.debug(f"Agent {agent_name} analysis: {analysis[:200]}...")
            return agent_name, analysis
        except Exception as e:
            logger.error(f"Error running agent {agent_name}: {e}", exc_info=True)
            return agent_name, f"Error in {agent_name} analysis: {str(e)}"

    def run_monitoring_cycle(self):
        """Executes one full monitoring and analysis cycle."""
        logger.info("Starting new monitoring cycle...")
        
        initial_context = self.gather_initial_context()
        if not initial_context or initial_context.strip() == "Collected Real-Time Data:":
            logger.warning("Initial context is empty or minimal. Cycle might be ineffective.")
            # Potentially send an alert about data gathering issues
            # send_telegram_alert("Warning: Data gathering for monitoring cycle failed or yielded no data.")
            # return

        agent_outputs = {}
        aggregated_insights_for_next_agent = ""

        # Define agent processing order if dependencies exist, or run in parallel if independent enough
        # For now, sequential to allow later agents to build on earlier ones.
        # The 'disaster_economist' should ideally run last to synthesize.
        
        agent_order = list(AGENT_ROLES.keys()) # Default order
        if "disaster_economist" in agent_order: # Ensure economist is last
            agent_order.remove("disaster_economist")
            agent_order.append("disaster_economist")

        for agent_name in agent_order:
            agent_role = AGENT_ROLES[agent_name]
            name, analysis = self.run_agent_analysis(agent_name, agent_role, initial_context, aggregated_insights_for_next_agent)
            agent_outputs[name] = analysis
            
            # Append this agent's key findings for the next agent
            # This is a simple aggregation; could be more sophisticated (e.g., LLM summarizes key points)
            aggregated_insights_for_next_agent += f"\n--- Insights from {name} ---\n{analysis}\n"

        # Synthesize final summary and recommendation (could be a dedicated LLM call)
        # For now, use disaster_economist's output as primary recommendation
        # and a concatenation of all outputs as the summary.

        final_summary_parts = []
        for agent_name, output_text in agent_outputs.items():
            final_summary_parts.append(f"--- {agent_name.upper()} ANALYSIS ---\n{output_text}\n")
        
        final_summary = "\n".join(final_summary_parts)
        
        recommendation = agent_outputs.get("disaster_economist", "No economic recommendation generated.")
        
        if not final_summary.strip() or not recommendation.strip():
            logger.error("Failed to generate a comprehensive summary or recommendation.")
            send_telegram_alert("Critical Error: Monitoring cycle completed but failed to generate summary/recommendation.")
            return

        # Store in DB
        try:
            # Storing raw agent outputs as JSON string for review
            agent_inputs_json = json.dumps(agent_outputs, indent=2)
            store_scenario(final_summary, recommendation, agent_inputs_json)
        except Exception as e:
            logger.error(f"Failed to store scenario in database: {e}", exc_info=True)
            # Decide if this is critical enough to halt or just log

        # Send Telegram Alert
        alert_message = f"🚨 **New Disaster Monitor Scenario** 🚨\n\n**Economic Recommendation:**\n{recommendation[:800]}...\n\n[🔍 Check dashboard for full details](https://seusite.com/dashboard)"
        send_telegram_alert(alert_message)
        
        logger.info("Monitoring cycle complete.")
        # logger.debug(f"Final Summary (snippet): {final_summary[:500]}...")
        # logger.debug(f"Recommendation (snippet): {recommendation[:500]}...")

    def start_continuous_monitoring(self):
        """Starts the monitoring loop."""
        logger.info("Intelligent Disaster Monitor starting continuous monitoring...")
        send_telegram_alert("📈 Intelligent Disaster Monitor activated. Starting monitoring cycles.")
        while True:
            try:
                self.run_monitoring_cycle()
            except Exception as e:
                logger.critical(f"Critical error in monitoring loop: {e}", exc_info=True)
                send_telegram_alert(f"🆘 CRITICAL ERROR in Disaster Monitor: {e}. System may need attention.")
            
            logger.info(f"Next monitoring cycle in {MONITORING_CYCLE_INTERVAL_SECONDS} seconds.")
            time.sleep(MONITORING_CYCLE_INTERVAL_SECONDS)

def main():
    """Entry point for the agent system."""
    try:
        monitor = IntelligentMonitor()
        # For a single run:
        # monitor.run_monitoring_cycle()
        # For continuous monitoring:
        monitor.start_continuous_monitoring()
    except Exception as e:
        logger.critical(f"Failed to initialize or start IntelligentMonitor: {e}", exc_info=True)
        # Attempt to send a startup failure alert if possible
        try:
            send_telegram_alert(f"🆘 CRITICAL STARTUP FAILURE for Disaster Monitor: {e}. System is DOWN.")
        except Exception as alert_e:
            logger.error(f"Failed to send startup failure alert: {alert_e}")

if __name__ == "__main__":
    # This allows running the agent system directly, e.g., in Docker or as a background service
    main()
