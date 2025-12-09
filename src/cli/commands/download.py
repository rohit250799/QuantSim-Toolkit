from src.modules.stock_data_downloader import FinancialDataDownloader

def run_download(args):
    downloader = FinancialDataDownloader()
    result = downloader.download_historical_stock_data(args.symbol, args.exchange)
    print(result)
    return