from db.database import init_db 

def test_database():
    """Testing database while loading in local development environment"""
    config = load_config()
    db_path = config["database"]["path"]

    init_db(db_path)

    execute_query(db_path, """
    CREATE TABLE IF NOT EXISTS symbols (
        id INTEGER PRIMARY KEY,
        ticker TEXT UNIQUE NOT NULL,
        company_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    execute_query(db_path, "INSERT OR IGNORE INTO symbols (ticker, company_name) VALUES (?, ?);", ("AAPL", "Apple Inc."))
    execute_query(db_path, "INSERT OR IGNORE INTO symbols (ticker, company_name) VALUES (?, ?);", ("GOOG", "Alphabet Inc."))

    print("Tables:", list_tables(db_path))
    print("Symbols:", execute_query(db_path, "SELECT * FROM symbols;"))

if __name__ == "__main__":
    test_database()
