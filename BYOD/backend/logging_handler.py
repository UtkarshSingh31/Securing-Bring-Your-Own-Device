
import logging
from datetime import datetime

# Configure logging format
logging.basicConfig(filename="usage_logs.log", level=logging.INFO, format="%(asctime)s - %(message)s")

THRESHOLD = 300

website_time_tracker = {}

def log_visit(url, category, time_spent):
    """Logs website visit and checks if it exceeds the threshold."""
    
    log_message = f"Visited {url} - Category: {category} - Time Spent: {time_spent} seconds"
    logging.info(log_message)
    print(log_message)  # Also print to console

    if category == "Non-Productive":
        website_time_tracker[url] = website_time_tracker.get(url, 0) + time_spent
        if website_time_tracker[url] >= THRESHOLD:
            alert_message = f"ALERT: {url} exceeded {THRESHOLD} seconds! (Immediate Alert)"
            logging.warning(alert_message)
            print(alert_message)  # Also print alert

