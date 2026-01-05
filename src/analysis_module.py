import pandas as pd
import logging

from typing import Dict
from src.data_loader.data_loader import DataLoader
from src.modules.analytics.returns_analyzer import (
    calculate_log_returns,
    calculate_cummulative_returns,
    calculate_annualized_volatility,
    calculate_beta,
    calculate_log_return_alpha,
    calculate_sharp_ratio, 
    calculate_correlation_coefficient
)
#from src.data_validator import DataValidator
logger = logging.getLogger("analytics")

class AnalysisModule:

    def __init__(self, data_loader: DataLoader) -> None:
        self.data_loader = data_loader
        return

    def compute_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Perform all the mathematical computations needed for the analysis

        Returns - A dict object containing all the compute metrics from log returns to beta
        """
        logger.debug('Successfully entered the compute_metrics function')
        df = df.dropna()
        ticker_annualized_volatility, benchmark_annualized_volatility = calculate_annualized_volatility(df, 'ticker_close_returns', 'benchmark_close_returns')

        compute_metrics_dict = {
            'log_returns': calculate_log_returns(df),
            'cummulative_returns': calculate_cummulative_returns(df),
            'ticker_annualized_volatility': ticker_annualized_volatility,
            'benchmark_annualized_volatility': benchmark_annualized_volatility,
            'beta': calculate_beta(df),
            'log_returns_alpha': calculate_log_return_alpha(df),
            'sharpe_ratio': calculate_sharp_ratio(df),
            'correlation_coefficient': calculate_correlation_coefficient(df),
            'sample_size': len(df)
        }
        
        logger.info('\n The compute metrics dict is: \n %s', compute_metrics_dict)
        return compute_metrics_dict 