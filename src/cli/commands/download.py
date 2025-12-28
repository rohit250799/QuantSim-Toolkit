import logging
from src.flow_controller import FlowController

import argparse

logger = logging.getLogger("cli")


def run_download(args: argparse.Namespace, flow_controller: FlowController) -> None:
    try:
        flow_controller.handle_download_request(args.symbol, args.startDate, args.endDate)
    except (ConnectionRefusedError, ConnectionAbortedError, InterruptedError, TimeoutError) as e:
        logger.info('Download failed due to reason: %s', e)
        raise
    else:
        print('Data downloaded successfully!')
        return