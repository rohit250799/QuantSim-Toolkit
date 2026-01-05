from src.flow_controller import FlowController

from typing import List, Dict, Any
import logging
import argparse

logger = logging.getLogger("cli")

# We can perform analysis on fetch values from the CSV file for analysis. For now, loading
# the CSV file all at once. Later, will create another feature which will use generator to load
# CSV file in chunks if the dataset is large 

def run_analyze(args: argparse.Namespace, flow_controller: FlowController | None) -> Dict[str, Any]:
    """
    Runs the Analyze command for the project
    Returns - the analysis report 
    """
    logging.debug('Entered the run analyze function block!')
    if not flow_controller:
        raise RuntimeError('Flow Conytroller is not properly initialized. Complete Initialization first ')
    
    input_ticker = args.ticker
    input_benchmark = args.benchmark if args.benchmark else 'NIFTY50_id.csv'

    analysis_report = flow_controller.dispatch_analysis_request(input_ticker, input_benchmark, args.startDate, args.endDate)
    logger.debug('The analysis report is: %s', analysis_report)
    
    return analysis_report


