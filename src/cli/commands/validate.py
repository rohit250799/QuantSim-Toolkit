import logging
import argparse

from src.flow_controller import FlowController

logging.basicConfig(filename='logs/main_file_logs.txt', level=logging.DEBUG,
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

def run_validation(args: argparse.Namespace, fc: FlowController) -> None:
    logging.debug('Entering the run validation function block')
    ticker = args.tName
    file_path = args.mPath

    fc.handle_validation_test(ticker, file_path)


