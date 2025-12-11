import argparse
import sys
import logging

from src.cli.parser import build_parser
from src.cli.commands.analyze import run_analyze
from src.cli.commands.download import run_download
from src.cli.commands.simulate import run_simulate

logging.basicConfig(filename='logs/main_file_logs.txt', level=logging.DEBUG,
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

def main() -> None:
    print('Quantsim-Toolkit - running main pipeline...\n')
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "analyze": run_analyze,
        "download": run_download,
        "simulate": run_simulate
    }

    handler = dispatch.get(args.command)
    if handler is None:
        raise ValueError(f'Unknown command: {args.command}')
    handler(args)



if __name__ == '__main__':
    main()

