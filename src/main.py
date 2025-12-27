import logging
import argparse
from pathlib import Path    
from typing import Any

from src.cli.parser import build_parser
from src.cli.commands.analyze import run_analyze
from src.cli.commands.download import run_download
from src.cli.commands.simulate import run_simulate
from src.cli.commands.validate import run_validation
from src.data_loader.data_loader import DataLoader
from src.circuit_breaker import CircuitBreaker
from src.data_validator import DataValidator
from src.flow_controller import FlowController
from src.analysis_module import AnalysisModule
from src.logging_config import configure_logging
from db.database import get_prod_conn, PROD_DB_PATH


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

logging.basicConfig(
    filename=LOG_DIR / "app.log",
    level=logging.DEBUG,
    format=LOG_FORMAT
)

def main() -> None:
    """Main function for the project - serves as the main entry point of execution"""
    configure_logging()
    logger = logging.getLogger("app")
    logger.info("Starting Application...\n")

    print('Quantsim-Toolkit - running main pipeline...\n')
    conn = get_prod_conn(PROD_DB_PATH)
    data_loader = DataLoader(conn)
    circuit_breaker = CircuitBreaker(data_loader)
    data_validator = DataValidator(data_loader)
    data_analyzer = AnalysisModule(data_loader)
    flow_controller: FlowController = FlowController(data_loader, circuit_breaker, data_validator, data_analyzer)

    parser = build_parser()
    args: argparse.Namespace = parser.parse_args()

    dispatch = {
        "analyze": run_analyze,
        "download": run_download,
        "simulate": run_simulate,
        "validate":  run_validation
    }

    handler: Any | None = dispatch.get(args.command)
    if handler is None:
        raise ValueError(f'Unknown command: {args.command}')
    handler(args, flow_controller)



if __name__ == '__main__':
    main()

