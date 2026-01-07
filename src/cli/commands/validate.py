import logging
import argparse

from src.flow_controller import FlowController

logger = logging.getLogger("cli")

def run_validation(args: argparse.Namespace, fc: FlowController) -> None:
    """Runs validation check"""
    logging.debug('Entering the run validation function block')
    ticker = args.tName
    start_date = args.startDate
    end_date = args.endDate

    if start_date >= end_date:
        raise ValueError('Start date must be earlier than end date')
    
    result = fc.handle_validation_test(ticker, start_date, end_date)
    logger.info('The result is: \n%s', result)
    return
