import sqlite3
import os

class StorageManager:
    def __init__(self, db_path: str = "telemetry_grid.db"):
        self.db_path = db_path
        # Establish connection and cursor as instance attributes
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        
    def initialize_schema(self, sql_script_path: str = "02-advanced-sql/migrate.sql"):
        """Reads your migrate.sql file and executes it to prepare the table."""
        if os.path.exists(sql_script_path):
            with open(sql_script_path, "r") as file:
                schema_script = file.read()
            self.cursor.executescript(schema_script)
            self.connection.commit()
            print("[DATABASE] Schema migrated successfully from SQL script.")
        else:
            print(f"[ERROR] Migration script not found at {sql_script_path}")

    def save_telemetry_frame(self, data_frame: dict):
        """Inserts a processed telemetry frame dictionary into the SQLite database."""
        insert_query = """
        INSERT INTO device_telemetry (device_id, drift_index, status) 
        VALUES (?, ?, ?);
        """
        
        extraction_tuple = (
            data_frame["device_id"],
            data_frame["drift_index"],
            data_frame["status"]
        )
        
        self.cursor.execute(insert_query, extraction_tuple)
        self.connection.commit() # Wait, slight correction: self.connection.commit()
        print(f"[DATABASE] Frame for {data_frame['device_id']} successfully persisted.")
        
    def close(self):
        """Clean up and safely close database resources."""
        self.connection.close()

# =====================================================================
# LOCAL VERIFICATION RUN
# =====================================================================
if __name__ == "__main__":
    print("[SYSTEM] Initializing Local Storage Manager Test...")
    
    # Instantiate the manager
    db_manager = StorageManager(db_path="telemetry_grid.db")
    
    # Point it exactly to where your migrate.sql file lives
    db_manager.initialize_schema(sql_script_path="02-advanced-sql/migrate.sql")
    
    # Create a mock processed frame matching our Math Engine output style
    mock_frame = {
        "device_id": "DEV-ALPHA",
        "drift_index": 1709.4496,
        "status": "CRITICAL_ANOMALY"
    }
    
    # Try inserting it!
    db_manager.save_telemetry_frame(mock_frame)
    
    # Safely disconnect
    db_manager.close()