import logging
import argparse

from src.flow_controller import FlowController

logger = logging.getLogger("cli")

def run_validation(args: argparse.Namespace, fc: FlowController) -> None:
    """Runs validation check"""
    logging.debug('Entering the run validation function block')
    ticker = args.tName
    file_path = args.mPath

    fc.handle_validation_test(ticker, file_path)


