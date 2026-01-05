import pandas as pd
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Tuple, Dict, List

from src.data_loader.data_loader import DataLoader
from src.quant_enums import ValidationIssueType

logger = logging.getLogger("validation")

class DataValidator:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def validate_and_clean(self, ticker: str, df: pd.DataFrame, price_columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Orchestrates:  all checks but does not modify the underlying data (no deleting outliers).
        
        Logs: issues to the log file

        Returns: original Dataframe with extra columns for changes in price columns listed columns and a report dict 
        showing the number of gaps, outliers and stale data records in dataset
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            raise TypeError(f"Expected DatetimeIndex, got {type(df.index).__name__}. Ensure date column is parsed and set as index.")
        
        if df.index.tz is None:
            df = df.copy()
            df.index = df.index.tz_localize("UTC")
        
        missing = [c for c in price_columns if c not in df.columns]
        if missing:
            raise KeyError(
                f"Missing price columns: {missing}. "
                f"Available columns: {list(df.columns)}"
            )

        df = df.copy()

        for col in price_columns:
            df[f"{col}_returns"] = df[col].pct_change()

        self.data_loader.delete_unresolved_validation_log(ticker)

        logger.debug('The dataframe is: \n%s', df)
        report = {
            'gap_number': self._check_gaps(ticker, df),
            'outlier_number': self._check_outliers(ticker, df, price_columns),
            'stale_data_number': self._check_stale(ticker, df, price_columns)
        }
        return df, report

    def _check_gaps(self, ticker: str, df: pd.DataFrame) -> int:
        """
        Identifies non-sequential timestamps (compares days actually present in the df against the days that the market should have 
        been open). Its assumed, that dataframe is already sorted and indexed by time
        Logs every gap to the log file

        Returns - the number of gaps existing in the file
        """
        data_loader = self.data_loader
        if df.empty:
            logger.debug('Empty dataframe passed to check gaps function. So, skipping the validation check')
            raise pd.errors.EmptyDataError('Empty dataframe was supplied as a parameter')
        start_date = df.index[0]
        end_date = df.index[-1]
        logger.debug('The start and end dates are: %s and %s', start_date, end_date)

        all_business_dates = pd.date_range(start=start_date, end=end_date, freq='B')
        all_unique_dates = pd.DatetimeIndex(df.index).normalize().unique()
        
        missing_days = set(all_business_dates) - set(all_unique_dates)
        logger.debug('The missing days are: %s', missing_days)

        for day in missing_days:
            date_string = day.isoformat()
            data_loader.insert_validation_issue(ticker, date_string, ValidationIssueType.MISSING_DAY.value, "Missing OHLCV data for this trading day")

        return len(missing_days)

    def _check_outliers(self, ticker: str, df: pd.DataFrame, price_columns: List[str]) -> int:
        """
        Calculates daily percentage returns. Flags any return exceeding 5 standard deviations (5SD) of the entire series.

        Returns - the number of outliers existing in the ddtaset
        """
        total_outliers = 0
        outlier_issue = ValidationIssueType.OUTLIER_5SD.value

        for col in price_columns:
            returns_col = f"{col}_returns"

            if returns_col not in df.columns:
                raise KeyError(f"Missing return column: {returns_col}")

            returns = df[returns_col].dropna()
            mean = returns.mean()
            std = returns.std()
            logger.info(
                "[%s] mean=%f std=%f (%s)",
                ticker, mean, std, returns_col
            )

            upper = mean + 5 * std
            lower = mean - 5 * std
            mask = (returns > upper) | (returns < lower)
            triggered_indices = returns.index[mask]

            for ts in triggered_indices:
                self.data_loader.insert_validation_issue(
                    ticker=ticker,
                    date=ts.isoformat(),
                    issue_type=outlier_issue,
                    description=f"5σ outlier detected in {returns_col}",
                )

            total_outliers += len(triggered_indices)
        return total_outliers

    def _check_stale(self, ticker: str, df: pd.DataFrame, price_columns: List[str]) -> int:
        """
        Detects and logs if 5 consecutive closing prices are identical AND volume is 0

        Returns- the number of stale rows in the dataset
        """
        issue_type = ValidationIssueType.STALE_PRICE.value
        stale_count = 0

        for col in price_columns:
            prices = df[col]
            # Identify change points
            price_changed = prices.ne(prices.shift(1))
            # Run identifiers
            run_id = price_changed.cumsum()

            # Length of each run
            run_lengths = prices.groupby(run_id).transform("size")

            # Mask stale runs (>= 5)
            stale_mask = run_lengths >= 5

            if not stale_mask.any():
                continue

            stale_indices = prices.index[stale_mask]

            for ts in stale_indices:
                # Ensure timezone awareness
                if ts.tzinfo is None:
                    ts = ts.tz_localize("UTC")

                unix_epoch = int(ts.timestamp())

                self.data_loader.insert_validation_issue(
                    ticker=ticker,
                    date=unix_epoch,
                    issue_type=issue_type,
                    description=f"Stale price detected in {col} (≥5 identical values)",
                )
                stale_count += 1
        return stale_count
    
    def calculate_quality_score(self, report: Dict[str, float]) -> float:
        """
        Takes the dictionary object about the counts of gaps, outliers and stale rows in the dataset as an input to calculate the Data Integrity Score

        Returns - the Data Integrity score
        """
        data_quality_initial_score: float = 1.0
        score = data_quality_initial_score - (report['gap_number'] * 0.05) - (report['outlier_number'] * 0.1) - (report['stale_data_number'] * 0.02)
        if score < 0:
            raise ArithmeticError('Score cannot be < 0')

        return score
    
