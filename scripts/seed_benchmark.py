import logging
import pandas as pd
from pathlib import Path

from src.data_loader.data_loader import DataLoader
from src.data_validator import DataValidator

logger = logging.getLogger("cli")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "src" / "data"

def load_csv_to_dataframe(csv_file_name: str) -> pd.DataFrame:
    """
    Reads your local Nifty50 CSV, format it to match our internal price_data schema, and "hydrate" 
    the database so the rest of the system treats it like any other ticker.

    Returns: A sanitized dataframe which will be seeded to the price_data table in the db
    """
    file_path = DATA_DIR / csv_file_name
    if not file_path.exists():
        logger.error('File not found at: %s', file_path)
        raise FileNotFoundError(f'Missing source CSV: {file_path}')
    
    try:
        #df = pd.read_csv(file_path, usecols=['date', 'open', 'high', 'low', 'close', 'volume'], parse_dates=['date'])[['date', 'open', 'high', 'low', 'close', 'volume']]
        df = pd.read_csv(file_path, usecols=['date', 'open', 'high', 'low', 'close', 'volume'], parse_dates=['date']) #load necessary cols
        
        #with Gemini (unconfirmed) - standardize index to timestamp
        df.rename(columns={'date': 'timestamp'}, inplace=True)
        df.set_index('timestamp', inplace=True)

        #normalizing time and ensuring UTC localization
        df.index = pd.to_datetime(df.index)
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")

        logger.debug('The head of the dataframe is: %s', df.head)
        logger.debug('\n The dataframe shape: %s', df.shape)
        logger.debug('\n The dataframe columns: %s', df.columns.to_list())

        # Format the index for SQLite storage (YYYY-MM-DD HH:MM:SS)
        # Note: We keep it as a DatetimeIndex for validation, DataLoader handles string conversion
        return df
        
    except FileNotFoundError as e:
        logger.error("Error loading CSV %s: %s", csv_file_name, e)
        raise

    except ValueError as e:
        logger.debug('Error loading columns: %s. Check if the column names exist in the CSV file.', e)
        raise
    
def seed_database(ticker_name: str, csv_filename: str) -> None:
    """
    Inserts the valid benchmark OHLCV data into the price_data table in db 

    Orchestrates:
    1. Loading CSV
    2. Validating data integrity
    3. Inserting into the price_data table in the db
    """
    data_loader = DataLoader()
    data_validator = DataValidator(data_loader)

    if data_loader.ticker_exists(ticker_name):
        logger.info('Ticker %s already exists. Skipping its seeding.', ticker_name)
        return
    
    try:
        # 1. Extraction
        df = load_csv_to_dataframe(csv_filename)
        
        # 2. Validation (Audit)
        # We audit 'close' to ensure the quality score is captured before ingestion
        _, report = data_validator.validate_and_clean(ticker_name, df, ['close'])
        score = data_validator.calculate_quality_score(report)
        
        # 3. Persistence
        data_loader.insert_daily_data(ticker_name, df)
        
        logger.debug(
            "Successfully seeded %s from %s (Quality Score: %.2f)", 
            ticker_name, csv_filename, score
        )

    except Exception as e:
        logger.info("Failed to seed %s: %s", ticker_name, e)
        raise

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