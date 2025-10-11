import argparse
import sys
import logging

from modules.probability import simulate_probability_of_single_dice, display_distribution_table

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s -  %(levelname)s -  %(message)s')

parser = argparse.ArgumentParser(prog='Quantsim Toolkit', description='A Python-based ' \
'quantitative simulation and analysis toolkit that integrates probability simulations, ' \
'stock return analysis, portfolio risk calculations, and Monte Carlo methods.')

subparsers = parser.add_subparsers(dest='myCommand', required=True)

parser_simulation = subparsers.add_parser('simulation', help='Probability simulation to simulate dice rolls, coin tosses etc')
parser_simulation.add_argument('-type', '--objectType', help='Type of object to use for simulation', dest='objectType', choices=[
    'dice', 'coin', 'custom'
], default='dice')
parser_simulation.add_argument('-acceptable', '--acceptableOutcome', default=1, type=int, dest='acceptableOutcome')
parser_simulation.add_argument('-total', '--totalOutcome', default=6, type=int, dest='totalOutcome')
parser_simulation.add_argument('-tries', '-totalTries', default=10, type=int, dest='totalTries')

parser_analyser = subparsers.add_parser('analyser', help='Reads historical stock price CSV and ' \
'analyses their returns')
parser_analyser.add_argument('-a', '--all', help='Display stock analysis data from ' \
'the block for now', dest='testAnalyser')

args = parser.parse_args()

if args.myCommand == 'simulation':
    if args.objectType == 'custom':
        print('The object type is custom')
        sys.exit(0)
    else:
        if args.objectType == 'coin':
            try:
                simulate_probability_of_single_dice(args.totalTries, object_type=args.objectType)
            except ValueError as e: 
                print(f'There has been a value error: {e}')
            else:
                print(f'After {args.totalTries} tries for coin toss, the results are: \n')
                result = simulate_probability_of_single_dice(args.totalTries, object_type=args.objectType)
                display_distribution_table(result)
        else:
            try:
                simulate_probability_of_single_dice(args.totalTries, object_type=args.objectType)
            except ValueError as e: 
                print(f'There has been a value error: {e}')
            else:
                print(f'After {args.totalTries} tries of dice roll, the results are: \n')
                result = simulate_probability_of_single_dice(args.totalTries, object_type=args.objectType)
                display_distribution_table(result)
    sys.exit(0)

if args.myCommand == 'analyser':
    print('Successfully entered the analyser block')
    sys.exit(0)

else:
    print('The entered command is invalid.')
    sys.exit(1)
