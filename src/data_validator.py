import pandas as pd
import logging
import numpy as np
from datetime import datetime, timezone

from src.data_loader.data_loader import DataLoader
from src.quant_enums import ValidationIssueType

logging.basicConfig(filename='logs/circuit_breaker_logs.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

class DataValidator:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def validate_and_clean(self, ticker: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Orchestrates:  all checks but does not modify the underlying data (no deleting outliers).
        
        Logs: issues to the log file

        Returns: original Dataframe
        """
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        df = df.set_index('timestamp').sort_index(ascending=True)
        df['daily_returns'] = df['close'].pct_change()
        self.data_loader.delete_unresolved_validation_log(ticker)
        self._check_gaps(ticker, df)
        self._check_outliers(ticker, df)
        self._check_stale(ticker, df)

        return df

    def _check_gaps(self, ticker: str, df: pd.DataFrame):
        """
        Identifies non-sequential timestamps (compares days actually present in the df against the days that the market should have 
        been open). Its assumed, that dataframe is already sorted and indexed by time
        Logs every gap to the log file
        """
        data_loader = self.data_loader
        start_date = df.index[0]
        end_date = df.index[-1]
        logging.debug('The start and end dates are: %s and %s', start_date, end_date)

        all_business_dates = pd.date_range(start=start_date, end=end_date, freq='B')
        all_unique_dates = df.index.normalize().unique()
        # expected_trading_days = all_dates[all_dates.weekday < 5]
        # trading_days_set: set = set(expected_trading_days)

        missing_days = set(all_business_dates) - set(all_unique_dates)
        logging.debug('The missing days are: %s', missing_days)

        for day in missing_days:
            unix_int_day = int(day.timestamp())
            data_loader.insert_validation_issue(ticker, unix_int_day, ValidationIssueType.MISSING_DAY.value, "Missing OHLCV data for this trading day")

        return

    def _check_outliers(self, ticker: str, df: pd.DataFrame):
        """
        Calculates daily percentage returns. Flags any return exceeding 5 standard deviations (5SD) of the entire series.
        """
        mean_daily_return = df['daily_returns'].mean()
        logging.info('The mean daily return is: %f', mean_daily_return)

        daily_returns_standard_deviation = df['daily_returns'].std()
        logging.info('The standard deviation in closing prices is: %f', daily_returns_standard_deviation)

        five_standard_deviation = 5 * daily_returns_standard_deviation
        upper_bound_in_five_standard_deviation = mean_daily_return + five_standard_deviation
        lower_bound_in_five_standard_deviation = mean_daily_return - five_standard_deviation

        signal_mask = (df['daily_returns'] >  upper_bound_in_five_standard_deviation) & (df['daily_returns'] < lower_bound_in_five_standard_deviation)
        triggered_timestamps = df.index[signal_mask]
        #logging.debug('The triggered timestamps are: %s and the data type is: %s', triggered_timestamps, type(triggered_timestamps))
        triggered_indices = df.index[signal_mask]
        #logging.debug('The triggered indices are: %s', triggered_indices)

        outlier_issue = ValidationIssueType.OUTLIER_5SD.value
        for timestamp_idx in triggered_indices:
            logging.debug('The timestamp_idx is: %s and the datatype is: %s', timestamp_idx, type(timestamp_idx))
            unix_date = int(timestamp_idx.timestamp())

            self.data_loader.insert_validation_issue(ticker=ticker, date=unix_date, issue_type=outlier_issue, description='Outlier issue: Return exceeds 5 standard deviation(5SD)')

        return

    def _check_stale(self, ticker: str, df: pd.DataFrame):
        """
        Detects and logs if 5 consecutive closing prices are identical AND volume is 0
        """
        is_volume_zero = (df['volume'] == 0)
        #checking for identical consecutive closing prices (for 5 days)
        consecutive_price_count = df.groupby(df['close'] != df['close'].shift(1).cumsum())['close'].transform('size')
        is_price_consecutive_five = (consecutive_price_count >= 5)

        #combining both above conditions
        is_stale = is_volume_zero & is_price_consecutive_five

        #identifying rows meeting the above criteria
        stale_rows = df[is_stale]
        issue_type = ValidationIssueType.STALE_PRICE.value
        if not stale_rows.empty:
            for ts in stale_rows.index:
                ts = ts.tz_localize("UTC") if ts.tzinfo is None else ts
                unix_date = int(ts.timestamp())
                self.data_loader.insert_validation_issue(ticker, unix_date, issue_type, "Stale data has been detected")

        return
