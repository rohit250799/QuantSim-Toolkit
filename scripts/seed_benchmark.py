import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict

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
    headers = pd.read_csv(file_path, nrows=0).columns.tolist()
    
    # 2. Map required columns (case-insensitive)
    mapping: Dict[str, str] = {}
    required_targets = ['open', 'high', 'low', 'close', 'volume']

    # Handle the Time column specifically
    time_col = next((h for h in headers if h.lower() in ['date', 'timestamp']), None)
    if not time_col:
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

        # 3. Type-Safe Unix conversion (Mypy friendly)
        # We ensure it's a Series to avoid DatetimeIndex/Series confusion
        time_series = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')

        # Filter out rows where timestamp couldn't be parsed
        df = df[time_series.notna()].copy()
        time_series = time_series.dropna()

        # Convert to Unix seconds
        df['timestamp'] = (time_series.astype(np.int64) // 10**9).astype(int)
       
        #Final cleaning
        df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')

        logger.debug('The head of the dataframe is: %s', df.head)
        logger.debug('\n The dataframe shape: %s', df.shape)
        logger.debug('\n The dataframe columns: %s', df.columns.to_list())
        logger.debug('Seeder loaded %s: %d rows', csv_file_name, len(df))
        
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

        if data_loader.ticker_exists(ticker_name):
            logger.info('Ticker %s already exists. Skipping its seeding.', ticker_name)
            return

        df = load_csv_to_dataframe(csv_filename)

        data_loader.insert_daily_data(ticker_name, df) #ensuring the loader receives timestamp column
        
        # 3. Validation (Audit)
        # We audit 'close' to ensure the quality score is captured before ingestion
        _, report = data_validator.validate_and_clean(ticker_name, df, ['close'])
        score = data_validator.calculate_quality_score(report)
        logger.debug(
            "Successfully seeded %s from %s with length: %d rows. (Quality Score: %.2f)", 
            ticker_name, csv_filename, len(df), score
        )

    except Exception as e:
        logger.info("Failed to seed %s: %s", ticker_name, e)

    finally:
        conn.close()

def hydrate_environment() -> None:
    """
    Convenience function to hydrate the database for remote environments (Codespaces/CI).
    Add all your 'Golden Sample' tickers here.
    """
    # Hydrate the Benchmark
    seed_database('NIFTY50', 'NIFTY50_id.csv')

    # Hydrate TCS
    seed_database('TCS', 'TCS_id.csv')
    seed_database('ITC', 'ITC_id.csv')    
    seed_database('RELIANCE', 'RELIANCE_id.csv')

    return    

if __name__ == '__main__':
    #If run directly, performing the full environmemt hydration
    hydrate_environment()

    
# seed_database()
# logger.info('Benchmark Data seeded sucessfully')