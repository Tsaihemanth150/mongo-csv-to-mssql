import os
import pandas as pd
import pyodbc
import logging
from datetime import datetime
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from .env file
db_config = {
    'driver': os.getenv('DB_DRIVER', '{ODBC Driver 17 for SQL Server}'),
    'server': os.getenv('DB_SERVER'),
    'database': os.getenv('DB_NAME'),
    'username': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
}

# Folder containing your MongoDB CSV exports
exports_folder = os.getenv('EXPORTS_FOLDER', r'C:\Users\sai hemanth\Desktop\dev\MongoDB_Exports')

# Set up logging
log_file = 'mongo_to_sql_migration/log/log.txt'
logging.basicConfig(
    filename=log_file,
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Build the connection string
def get_connection_string(config):
    return (
        f"DRIVER={config['driver']};"
        f"SERVER={config['server']};"
        f"DATABASE={config['database']};"
        f"UID={config['username']};"
        f"PWD={config['password']}"
    )

# Connect to SQL Server
def connect_db():
    conn_str = get_connection_string(db_config)
    return pyodbc.connect(conn_str)

# Ensure a control table to track imported files
def ensure_control_table(cursor):
    cursor.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.tables WHERE name = 'ImportedFiles'
        )
        CREATE TABLE ImportedFiles (
            FileName NVARCHAR(255) PRIMARY KEY,
            ImportedDate DATETIME NOT NULL DEFAULT GETDATE()
        );
        """
    )

# Sanitize SQL identifiers
def clean_name(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

# Main import logic
def import_csvs(folder_path):
    conn = connect_db()
    cursor = conn.cursor()
    ensure_control_table(cursor)
    conn.commit()

    for fname in os.listdir(folder_path):
        if not fname.lower().endswith('.csv'):
            continue

        full_path = os.path.join(folder_path, fname)

        # Check if already imported
        cursor.execute("SELECT 1 FROM ImportedFiles WHERE FileName = ?", fname)
        if cursor.fetchone():
            msg = f"Skipping '{fname}': already imported."
            print(msg)
            logging.info(msg)
            continue

        # Sanitize table name
        raw_table_name = os.path.splitext(fname)[0]
        table_name = clean_name(raw_table_name)

        try:
            if os.path.getsize(full_path) == 0:
                raise ValueError("Empty file")

            df = pd.read_csv(full_path, dtype=str, keep_default_na=False)
            if df.empty or df.columns.empty:
                raise ValueError("No columns to parse from file")

            df = df.astype(str)
            original_columns = df.columns.tolist()
            clean_columns = [clean_name(col) for col in original_columns]
            df.columns = clean_columns

            col_defs = ", ".join(f"[{col}] NVARCHAR(MAX)" for col in clean_columns)
            create_sql = f"""
                IF NOT EXISTS (
                    SELECT 1 FROM sys.tables WHERE name = '{table_name}'
                )
                CREATE TABLE [{table_name}] (
                    {col_defs}
                );
            """
            cursor.execute(create_sql)
            conn.commit()

            col_list = ", ".join(f"[{col}]" for col in clean_columns)
            placeholders = ", ".join('?' for _ in clean_columns)
            insert_sql = f"INSERT INTO [{table_name}] ({col_list}) VALUES ({placeholders});"

            cursor.fast_executemany = True
            cursor.executemany(insert_sql, df.values.tolist())
            conn.commit()

            success_msg = f"Imported '{fname}' into table '{table_name}'."
            print(success_msg)
            logging.info(success_msg)

            cursor.execute("INSERT INTO ImportedFiles (FileName) VALUES (?)", fname)
            conn.commit()

        except Exception as e:
            error_msg = f"Failed to import '{fname}': {str(e)}"
            print(error_msg)
            logging.error(error_msg)

    cursor.close()
    conn.close()

if __name__ == '__main__':
    import_csvs(exports_folder)
