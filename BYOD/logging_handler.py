import csv
import threading
import pickle
import os
import time
from datetime import datetime, timedelta
from utils import extract_meta_data,extract_text_from_url

LOG_FILE = "student_activity.csv"
ALERT_THRESHOLD = 300  # 5 minutes 
SWITCH_THRESHOLD = 120 # 2 minutes

# Load Model
MODEL_FILENAME = "svm_stem(3,3).sav"
loaded_model = pickle.load(open(MODEL_FILENAME, "rb"))

log_lock = threading.Lock()  

def classify_url(url):
    
    meta_data = extract_meta_data(url)

    if meta_data:
        text_for_classification = meta_data
    else:
        text_for_classification = extract_text_from_url(url)

    if not text_for_classification.strip():  # If still empty
        return "Unknown"

    prediction = loaded_model.predict([text_for_classification])[0]
    return "Productive" if prediction==1 else "Non-Productive"

def initialize_log_file():
    """Create the log file with headers if it doesn't exist."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "User_Id",
                "Timestamp(Start)", 
                "URL", 
                "Category", 
                "TimeSpent(s)", 
                "Alert", 
                "TimeStamp(End)",
                "ExcessTime(s)",
                "E-mail"
            ])

def log_visit(user_id,url, time_spent,email):
    """Logs URL visit and raises alerts dynamically based on ML classification."""
    
    if not os.path.exists(LOG_FILE):
        initialize_log_file()
        
    category = classify_url(url)  
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=time_spent)
    
    is_alert = category == "Non-Productive" and time_spent > ALERT_THRESHOLD
    alert_status = "YES" if is_alert else "NO"
    excess_time = time_spent - ALERT_THRESHOLD if is_alert else "N/A"
    email=email
    
    log_lock.acquire()
    try:
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow([
                user_id,
                start_time,              # Timestamp
                url,                     # URL visited
                category,                # Productivity category
                time_spent,              # Time spent in seconds
                alert_status,            # Alert status (YES/NO)
                end_time,
                excess_time,              # Excess time if alerted
                email
            ])
            

            if is_alert:
                alert_message = f"ALERT: {url} ({category}) exceeded time limit of {ALERT_THRESHOLD} seconds by {excess_time} seconds!"
                print(alert_message)
    finally:
        log_lock.release()

initialize_log_file()

if __name__=="__main__":
    url="https://www.youtube.com/wwe"
    log_visit(103,url,450)
    time.sleep(2)