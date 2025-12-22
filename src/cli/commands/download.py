import logging
from src.flow_controller import FlowController

import argparse

logger = logging.getLogger("cli")


def run_download(args: argparse.Namespace, flow_controller: FlowController) -> None:
    flow_controller.handle_download_request(args.symbol, args.startDate, args.endDate)
    return