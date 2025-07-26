# 📦 MongoDB CSV to SQL Server Importer

This Python script automates the import of multiple `.csv` files (exported from MongoDB) into a SQL Server database. It ensures safe, idempotent data loading by tracking which files have already been imported.

---

## 🎯 Purpose

- ✅ Transform MongoDB collection CSV exports into SQL Server tables.
- ✅ Automatically create SQL tables based on CSV headers.
- ✅ Skip already-imported files using a control table.
- ✅ Log all actions and errors to `log.txt`.

---

## 🛠️ Features

- 📁 Bulk CSV import from a specified folder
- 🧠 Intelligent table and column name sanitization
- 🔄 Idempotent imports (prevents re-importing)
- 🗃️ Auto SQL table creation with `NVARCHAR(MAX)` columns
- 🧾 Logging with timestamps in `log.txt`

---

## 📂 Project Structure

```
mongo_to_sql_migration/
├── main.py              # Main import logic
├── .env                 # Database config
├── requirements.txt     # Python dependencies
├── log.txt              # Import logs
└── MongoDB_Exports/     # Folder containing .csv exports
```

---

## 🔧 .env Configuration

Create a `.env` file in the root folder with the following:

```env
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=YourDatabaseName
DB_USER=your_username
DB_PASSWORD=your_password
EXPORTS_FOLDER=C:\Users\sai hemanth\Desktop\dev\MongoDB_Exports
```

---

## 🚀 Usage

1. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the script**  
   ```bash
   python main.py
   ```

3. **Check logs**  
   Open `log.txt` to view import status or errors.

---

## 📦 Requirements

- Python 3.7+
- SQL Server (local or remote)
- ODBC Driver 17 for SQL Server
- Python packages:
  - `pandas`
  - `pyodbc`
  - `python-dotenv`

Install with:

```bash
pip install -r requirements.txt
```

---

## ✅ Safety & Idempotency

- A table `ImportedFiles` keeps track of which CSVs were successfully imported.
- You can safely rerun the script — it will **skip** files already processed.

---

## 🧼 Notes

- Table and column names are sanitized to remove unsupported characters.
- All values are inserted as `NVARCHAR(MAX)` to avoid type mismatch issues.
- Empty or malformed files are automatically skipped and logged.

---

## 📜 License

MIT License – use freely with attribution.

---

> 💬 _Need improvements like datetime casting, array support, or schema inference? PRs welcome or feel free to fork and extend!_
