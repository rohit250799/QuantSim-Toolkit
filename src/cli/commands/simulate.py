import argparse
import logging

from src.modules.probability import display_distribution_table, display_multiple_dice_simulation_parameters

logger = logging.getLogger("cli")


def run_simulate(args: argparse.Namespace) -> None:
    object_type = args.objectType
    multi_dice = args.multiDice
    dice_number = args.diceNumber
    sides = args.diceTotalSides
    tries = args.totalTries

    dice_roll_frequency_results = display_multiple_dice_simulation_parameters(dice_number=dice_number, sides_per_dice=sides, total_rolls=tries)
    display_distribution_table(dice_roll_frequency_results, multi_dice=multi_dice)
    return