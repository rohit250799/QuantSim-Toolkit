import logging
import pandas as pd

from src.data_loader.data_loader import DataLoader
from src.data_validator import DataValidator

logger = logging.getLogger("cli")


def load_benchmark_csv(file_path: str = 'src/data/') -> pd.DataFrame:
    """
    Reads your local Nifty50 CSV, format it to match our internal price_data schema, and "hydrate" 
    the database so the rest of the system treats it like any other ticker.

    Returns: A sanitized dataframe which will be seeded to the price_data table in the db
    """
    try:
        nifty_df = pd.read_csv('src/data/NIFTY50_id.csv', usecols=['date', 'open', 'high', 'low', 'close', 'volume'], parse_dates=['date'])[['date', 'open', 'high', 'low', 'close', 'volume']]
        print(nifty_df)
        logger.info('The head of the dataframe is: %s', nifty_df.head)
        logger.info('\n The dataframe shape: %s', nifty_df.shape)
        logger.info('\n The dataframe columns: %s', nifty_df.columns.to_list())

    except FileNotFoundError as e:
        logger.debug('File not found in the given location. Error: %s', e)
        raise

    except ValueError as e:
        logger.debug('Error loading columns: %s. Check if the column names exist in the CSV file.', e)
        raise
    
    else: 
        #CSV file found and its data has been loaded as a DataFrame
        nifty_df['date'] = pd.to_datetime(nifty_df['date'], format='%d-%b-%Y')
        nifty_df.set_index('date', inplace=True)
        nifty_df.index.name = 'timestamp'
        nifty_df.index = nifty_df.index.normalize()
        nifty_df.index = nifty_df.index.strftime("%Y-%m-%d %H:%M:%S")
        nifty_df.index = pd.to_datetime(nifty_df.index)
        print(f'The parsed index dataframe with date is: \n{nifty_df}')

        logger.info('The dataframe with updated index in load_benchmark is: \n%s', nifty_df)
        data_loader = DataLoader()
        data_validator = DataValidator(data_loader)

        validated_nifty_df = data_validator.validate_and_clean(ticker='Nifty50', df=nifty_df)
        logger.debug('The validated dataframe is: \n%s', validated_nifty_df)
        print(f'The validated and clean dataframe is: \n{validated_nifty_df}')
        return validated_nifty_df
    
def seed_database(ticker_name: str = 'NIFTY50_id.csv', csv_path: str = 'src/data') -> None:
    """
    Inserts the valid benchmark OHLCV data into the price_data table in db 
    """
    data_loader = DataLoader()
    try:
        clean_dataframe = load_benchmark_csv()
    except (FileNotFoundError, ValueError) as e:
        logger.info('Error occured: %s', e)
        raise
    else:
        data_loader.insert_daily_data(ticker_name, clean_dataframe)
        logger.info('Successfully inserted the Nifty dataframe into price data table in db')

        return

# seed_database()
# logger.info('Benchmark Data seeded sucessfully')