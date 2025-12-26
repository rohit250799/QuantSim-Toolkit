from src.modules.analytics.returns_analyzer import (
    summarize_returns,
    read_all_csv_data, 
    #calculate_daily_portfolio_returns,
    calculate_daily_returns
)
from src.flow_controller import FlowController
from src.custom_errors import EmptyRecordReturnError
from src.analysis_module import AnalysisModule

from typing import List
from pathlib import Path
import pandas as pd
import logging
import argparse

logger = logging.getLogger("cli")

# We can perform analysis on fetch values from the CSV file for analysis. For now, loading
# the CSV file all at once. Later, will create another feature which will use generator to load
# CSV file in chunks if the dataset is large 

def run_analyze(args: argparse.Namespace, flow_controller: FlowController | None) -> None:
    logging.debug('Entered the run analyze function block!')
    input_ticker = args.ticker
    input_benchmark = args.benchmark if args.benchmark else 'NIFTY50_id.csv'

    flow_controller.dispatch_analysis_request(input_ticker, input_benchmark, args.startDate, args.endDate)
    
    return


