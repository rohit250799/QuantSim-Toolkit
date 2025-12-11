from src.modules.stock_data_downloader import FinancialDataDownloader

import argparse

def run_download(args: argparse.Namespace) -> None:
    downloader = FinancialDataDownloader()
    result = downloader.download_historical_stock_data(args.symbol, args.exchange)
    print(result)
    return