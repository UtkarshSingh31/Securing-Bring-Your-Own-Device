import pandas as pd
from sklearn.ensemble import IsolationForest # type: ignore
from scipy.stats import zscore # type: ignore
import time
import os
from watchdog.observers import Observer # type: ignore
from watchdog.events import FileSystemEventHandler # type: ignore

# Global variable to store previous data
prev_data = None

def aggregate_data(df):
    """Aggregates the student activity data for anomaly detection."""
    email_mapping = df.groupby('User_Id')['E-mail'].last().reset_index()
    aggregated_data = df.groupby('User_Id').agg(
        Total_Websites=('URL', 'count'),
        Productive_Count=('Category', lambda x: (x == 'Productive').sum()),
        Non_Productive_Count=('Category', lambda x: (x == 'Non-Productive').sum()),
        Session_Duration=('TimeSpent(s)', 'sum'),
        E_mail=("E-mail","first")
    ).reset_index()

    # Calculate switches
    df['Prev_Category'] = df.groupby('User_Id')['Category'].shift(1)
    df['Switches'] = ((df['Category'] != df['Prev_Category']) & (df['Prev_Category'].notna())).astype(int)
    switch_counts = df.groupby('User_Id')['Switches'].sum().reset_index()

    aggregated_data = aggregated_data.merge(switch_counts, on='User_Id', how='left')

    return aggregated_data

def detect_anomalies(aggregated_data):
    """Applies Isolation Forest to detect anomalies in real time."""
    model = IsolationForest(contamination=0.05, random_state=42)
    aggregated_data['Anomaly_Score'] = model.fit_predict(aggregated_data[['Total_Websites', 'Session_Duration', 'Switches']])
    aggregated_data['Anomaly'] = aggregated_data['Anomaly_Score'].apply(lambda x: 1 if x == -1 else 0)
    
    return aggregated_data

def calculate_z_scores(aggregated_data, df):
    """Computes Z-score for anomaly detection and tracks total alerts per user."""
    
    # Compute Z-score for switch count
    aggregated_data['Z_Score'] = zscore(aggregated_data['Switches'])

    # Flag anomalies where Z-score > 3
    aggregated_data['Z_Anomaly'] = (aggregated_data['Z_Score'] > 3).astype(int)

    # Calculate total alerts: Count how many times a user visits non-productive websites
    alerts = df[df['Category'] == 'Non-Productive'].groupby('User_Id').size().reset_index(name='Total_Alerts')

    # Merge alerts with aggregated data
    aggregated_data = aggregated_data.merge(alerts, on='User_Id', how='left')
    
    # Fill missing alerts with 0 (if no non-productive sites were visited)
    aggregated_data['Total_Alerts'].fillna(0, inplace=True)

    return aggregated_data


def process_anomalies(file_path):
    """Reads the updated log file, aggregates data, and detects anomalies."""
    global prev_data

    df = pd.read_csv(file_path)

    # Aggregate latest data
    aggregated_data = aggregate_data(df)
    
    # Detect anomalies using Isolation Forest
    aggregated_data = detect_anomalies(aggregated_data)
    
    # Compute Z-score anomalies
    aggregated_data = calculate_z_scores(aggregated_data, df)  

    # Handle missing values before applying ML models
    aggregated_data.fillna(0, inplace=True)
    os.system("python send_alert.py")
    # Save updated anomalies
    aggregated_data.to_csv('real_time_anomalies.csv', index=False)

    # Check for new anomalies compared to previous data
    if prev_data is not None:
        new_anomalies = aggregated_data[aggregated_data['Anomaly'] == 1]
        new_anomalies = new_anomalies.merge(prev_data, on='User_Id', suffixes=('_new', '_old'), how='left')

        # Handle missing previous anomaly data
        if 'Anomaly_old' in new_anomalies.columns:
            new_anomalies = new_anomalies[new_anomalies['Anomaly_old'] != 1]

        if not new_anomalies.empty:
            with open("anomaly_log.csv", "a") as log_file:
                new_anomalies.to_csv(log_file, index=False, header=False)

    prev_data = aggregated_data.copy()  
    print(" Anomaly detection updated in real_time_anomalies.csv")



class FileWatcher(FileSystemEventHandler):
    """Watches for changes in student_activity.csv and triggers anomaly detection."""
    def on_modified(self, event):
        if event.src_path.endswith("student_activity.csv"):
            print("Detected changes in student_activity.csv, processing anomalies...")
            process_anomalies(event.src_path)


if __name__ == "__main__":
    file_path = "student_activity.csv"

    # Run initial anomaly check
    process_anomalies(file_path)

    # Set up file watcher
    event_handler = FileWatcher()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)  # Keep script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
