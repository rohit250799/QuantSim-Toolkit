import pandas as pd
import logging

from src.data_loader.data_loader import DataLoader
from src.modules.analytics.returns_analyzer import (
    calculate_log_returns,
    calculate_cummulative_returns,
    calculate_annualized_volatility,
    calculate_beta,
    calculate_alpha,
    calculate_sharp_ratio, 
    calculate_correlation_coefficient
)
logger = logging.getLogger("analytics")

class AnalysisModule:

    def __init__(self, data_loader: DataLoader) -> None:
        self.data_loader = data_loader
        return

    def compute_metrics(self, df: pd.DataFrame) -> None:
        """
        Perform all the mathematical computations needed for the analysis
        """
        logger.debug('Successfully entered the compute_metrics function')
        df = df.dropna()

        compute_metrics_dict = {
            'log_returns': calculate_log_returns(df),
            'cummulative_returns': calculate_cummulative_returns(df),
            'annualized_volatility': calculate_annualized_volatility(df),
            'beta': calculate_beta(df),
            'alpha': calculate_alpha(df),
            'sharpe_ratio': calculate_sharp_ratio(df),
            'correlation_coefficient': calculate_correlation_coefficient(df),
            'sample_size': len(df)
        }
        
        logger.info('\n The compute metrics dict is: \n %s', compute_metrics_dict)
        return 