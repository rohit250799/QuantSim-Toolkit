import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List

from src.data_loader.data_loader import DataLoader
from src.data_validator import DataValidator
from db.database import get_prod_conn, get_db_path

logger = logging.getLogger("cli")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "src" / "data"

def load_csv_to_dataframe(csv_file_name: str) -> pd.DataFrame:
    """
    Reads your local Nifty50 CSV, format it to match our internal price_data schema, and "hydrate" 
    the database so the rest of the system treats it like any other ticker. Standardizes CSV data for the DB with strict type safety. 
    Handles:
    1. 'date' vs 'timestamp' column names.
    2. Case sensitivity.
    3. Conversion to Unix Epoch (seconds).

    Returns: A sanitized dataframe which will be seeded to the price_data table in the db
    """
    file_path = DATA_DIR / csv_file_name
    if not file_path.exists():
        logger.error('File not found at: %s', file_path)
        raise FileNotFoundError(f'Missing source CSV: {file_path}')
    
    # 1. Read only the header to detect column names
    headers: List[str] = pd.read_csv(file_path, nrows=0).columns.tolist()
    
    # 2. Map required columns (case-insensitive)
    mapping: Dict[str, str] = {}
    required_targets = ['open', 'close', 'high', 'low', 'volume']

    # Handle the Time column specifically
    time_col = next((h for h in headers if h.lower() in ['date', 'timestamp', 'time', 'datetime']), None)
    if not time_col:
        logger.error(f"Headers found in {csv_file_name}: {headers}")
        raise ValueError(f"No time-based column (date/timestamp) found in {csv_file_name}")
    
    mapping[time_col] = 'timestamp'

    for req in required_targets:
        match = next((h for h in headers if h.lower() == req), None)
        if match:
            mapping[match] = req
        else: 
            #If volume is missing, its defaulted to 0. But OHLC must always exist
            logger.debug("Optional/Missing column '%s' in %s", req, csv_file_name)
        
    try:
        #Load and Parse
        df = pd.read_csv(file_path, usecols=list(mapping.keys()))
        df.rename(columns=mapping, inplace=True)
        
        # Convert to DatetimeIndex (DataLoader requirement)
        # We handle conversion here so the Validator and Loader receive standard types
        if csv_file_name == 'NIFTY50_id.csv':
            df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True, utc=True, format='%d-%b-%Y', errors='coerce')
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
        df = df.dropna(subset=['timestamp']).copy()

        pre_drop_count = len(df)
        df = df.dropna(subset=['timestamp']).copy()
        post_drop_count = len(df)

        if post_drop_count == 0 and pre_drop_count > 0:
            # Diagnostic: show a sample of the raw data that failed to parse
            sample_val = pd.read_csv(file_path, nrows=1)[time_col].iloc[0]
            logger.error(f"Failed to parse dates in {csv_file_name}. Sample value: '{sample_val}'")
            raise ValueError(f"Timestamp parsing failed for all rows in {csv_file_name}")
        df.set_index('timestamp', inplace=True)

        if 'volume' not in df.columns:
            df['volume'] = 0

        df = df.drop_duplicates().sort_index()
        if df.empty:
            raise ValueError(f"{csv_file_name} produced empty dataframe after parsing")

        return df
    
    except Exception as e:
        logger.error('Fail to parse %s due to error: %s', csv_file_name, e)
        raise
    
def seed_database(ticker_name: str, csv_filename: str) -> None:
    """
    Inserts the valid benchmark OHLCV data into the price_data table in db 

    Orchestrates:
    1. Loading CSV
    2. Validating data integrity
    3. Inserting into the price_data table in the db
    """
    # Use the existing project DataLoader
    db_path = get_db_path()
    conn = get_prod_conn(db_path)
    
    try:
        data_loader = DataLoader(conn)
        data_validator = DataValidator(data_loader)
        logger.info('Seed request: %s from %s', ticker_name, csv_filename)
        data_loader.ensure_symbol_exists(ticker=ticker_name)
        df = load_csv_to_dataframe(csv_filename)
        #df.index = pd.to_datetime(df.index).view('int64') // 10**9
        clean_df, report = data_validator.validate_and_clean(ticker_name, df, ['close'])

        data_loader.insert_daily_data(ticker_name, clean_df) #ensuring the loader receives timestamp column

        # VERIFICATION: Double check count immediately
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM price_data WHERE ticker = ?", (ticker_name,))
        count = cursor.fetchone()[0]
        print(f"✅ Successfully seeded {ticker_name}. DB count: {count}")

        score = data_validator.calculate_quality_score(report)
        logger.debug(
            "Successfully seeded %s from %s with length: %d rows. (Quality Score: %.2f)", 
            ticker_name, csv_filename, len(df), score
        )

    except Exception as e:
        logger.info("Failed to seed %s: %s", ticker_name, e)
        raise

    finally:
        conn.close()



    
# seed_database()
# logger.info('Benchmark Data seeded sucessfully')