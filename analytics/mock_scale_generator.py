"""
Module: mock_scale_generator.py
Description: Injects high-volume historical telemetry records directly 
             into device_telemetry to stress-test system scale.
"""
import os
import sqlite3
import random
import time

ROOT_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def generate_scale_data(target_rows=200000):
    db_path = os.path.join(ROOT_WORKSPACE, "telemetry_grid.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"[BIG DATA] Commencing generation run targeting {target_rows:,} records...")
    
    device_ids = [f"DEV-{code}" for code in ["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO"]]
    statuses = ["NORMAL", "NORMAL", "NORMAL", "CRITICAL_ANOMALY"]
    
    # 30-day historical epoch window
    base_time = time.time() - (30 * 24 * 60 * 60) 
    
    batch = []
    batch_size = 25000
    
    for i in range(target_rows):
        # Format timestamp to string matching SQLite DATETIME format
        record_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(base_time + (i * 12))) 
        
        dev = random.choice(device_ids)
        drift = round(random.uniform(100.0, 6000.0), 4)
        stat = random.choice(statuses)
        
        batch.append((record_time, dev, drift, stat))
        
        if len(batch) >= batch_size:
            cursor.executemany("""
                INSERT INTO device_telemetry (timestamp, device_id, drift_index, status)
                VALUES (?, ?, ?, ?)
            """, batch)
            conn.commit()
            print(f"[BIG DATA] Ingested cluster progress: {i + 1:,}/{target_rows:,} rows logged...")
            batch = []
            
    if batch:
        cursor.executemany("""
            INSERT INTO device_telemetry (timestamp, device_id, drift_index, status)
            VALUES (?, ?, ?, ?)
        """, batch)
        conn.commit()

    print("[BIG DATA] Scale generation run finished cleanly!")
    conn.close()

if __name__ == "__main__":
    generate_scale_data(200000)