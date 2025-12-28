import argparse

def build_parser() -> argparse.ArgumentParser:
    """Returns an Argument parser to parse the arguments accepted from the command line"""
    parser = argparse.ArgumentParser(
        prog="Quantsim Toolkit",
        description="A Python-based quantitative simulation and analysis toolkit integrating probability simulations, stock return analysis, portfolio risk calculations, and Monte Carlo methods."
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    #Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze historical price data")
    analyze_parser.add_argument("-ticker", '--ticker_element', help='The target symbol to perform analysis on', required=True, dest='ticker')
    analyze_parser.add_argument("-texchange", '--ticker_exchange', help='The exchange where the ticker is being traded', default="BSE", dest='tExchange')
    analyze_parser.add_argument("-benchmark", '--benchmrk_element', help='The benchmark element which the analysis is being performed against', default='NIFTY50', dest='benchmark')
    analyze_parser.add_argument("-bexchange", '--benchmark_exchange', help = 'The the exchange from where this benchmark data is collected', default="NSE", dest='bExchange')
    analyze_parser.add_argument("-start", '--start_date', help = 'The start date for data collection and analysis', default='2025-09-01', dest='startDate')
    analyze_parser.add_argument("-end", '--end_date', help = 'The end date for data collection and analysis', default='2025-09-21', dest='endDate')


    #Download
    parser_downloader = subparsers.add_parser('download', help='Download required data in CSV format')
    parser_downloader.add_argument('-symbol', '--stockSymbol', help='symbol of the stock', dest='symbol')
    parser_downloader.add_argument('-exchange', '--stock_exchange', help='Stock exchange where the stock is traded', default='BSE', dest='exchange')
    parser_downloader.add_argument('-sdate', '--startdate', help='specifies the starting date for filtering data', dest='startDate')
    parser_downloader.add_argument('-edate', '--enddate', help='specifies the ending date for filtering data', dest='endDate')

    #simulate
    parser_simulation = subparsers.add_parser('simulation', help='Probability simulation to simulate dice rolls, coin tosses etc')
    parser_simulation.add_argument('-type', '--objectType', help='Type of object to use for simulation', dest='objectType', choices=[
        'dice', 'coin', 'custom'
        ], default='dice')
    parser_simulation.add_argument('-multi', '--multipleDice', help='Specifies if multiple dice are used for the simulation', action='store_true', dest='multiDice')
    parser_simulation.add_argument('-dice', '--dicenumber', default=2, type=int, dest='diceNumber', help='number of dice to be used in the sim')
    parser_simulation.add_argument('-sides', '--diceTotalSides', default=6, type=int, dest='diceTotalSides', help='Total sides of each dice')
    parser_simulation.add_argument('-tries', '-totalTries', default=10, type=int, dest='totalTries', help='The number of tries in the simulation')

    #validate
    parser_validator = subparsers.add_parser('validate', help='Helps validate data to be used')
    parser_validator.add_argument('-tname', '--tickerName', help='Name of the ticker whose data you want to vaidate', dest='tName')
    parser_validator.add_argument('-mpath', '--mockPath', help='Path of the file', default='src/data', dest='mPath')

    return parser
