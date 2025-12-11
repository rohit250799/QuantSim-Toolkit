import logging
import random
import math

from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class Frequency:
    connt: int
    probability: float = 0.0

def display_distribution_table(frequency_storage_dict: Dict[int, List[float]], multi_dice: bool = False) -> None:
    """
    Displays the distribution table with different table on the terminal
    """
    print('\n Distribution table:  \n')
    for key, (frequency, probability) in frequency_storage_dict.items():
        print(f'Number / sum: {key}, Frequency: {frequency}, Probability: {probability}')
    if multi_dice:
        expected_value = calculate_expected_value_in_multi_dice_roll(frequency_storage_dict)
        print(f'\n The expected value is: {expected_value}')
        print(f'\n The variance is: {calculate_variance_of_data(frequency_storage_dict)}')
        print(f'\n The standard deviation from the distribution table is: {math.sqrt(calculate_variance_of_data(frequency_storage_dict))}')
    return

def display_multiple_dice_simulation_parameters(dice_number: int = 2, sides_per_dice: int = 6, total_rolls: int = 1000) -> Dict[int, List[float]]:

    """
    Simulates the probability of multiple dice rolls and displays the distribution of sums with summary stats

    Args: 
    dice_number(int): number of dice used in the simulation
    sides_per_dice(int): number of sides that each die has
    total_rolls(int): the total number of tries in this simulation

    Returns: 
    The distribution of sums of all dice rolls with their summary statistics
    """

    print(f"""
        Quantsim toolkit - Dice roll simulation:
        
          Simulation Parameters:

          Dice: {dice_number},
          Sides per dice: {sides_per_dice},
          Total rolls: {total_rolls}
    """)

    if total_rolls <= 0: 
        raise ValueError('There should at least be 1 dice roll in the simulation')
    
    if not (1 <= dice_number <= 4):
        raise ValueError("dice_number must be between 1 and 4.")
    
    if not (1 <= sides_per_dice <= 10):
        raise ValueError("sides_per_dice must be between 1 and 10.")
    
    total_sum_possible: range = range(dice_number, dice_number * sides_per_dice + 1)

    # Dict: sum_value → [count, probability]
    frequency_storage_dict: Dict[int, List[float]] = {
        outcome: [0.0, 0.0] for outcome in total_sum_possible
    }

    # to run simulation
    for _ in range(total_rolls):
        dice_values = [random.randint(1, sides_per_dice) for _ in range(dice_number)]
        total_value = sum(dice_values)

        # Incrementing count
        frequency_storage_dict[total_value][0] += 1.0

    # Calculating probabilities
    for sum_value, pair in frequency_storage_dict.items():
        count = pair[0]  # first element is count
        if count == 0:
            continue
        pair[1] = count / total_rolls
    return frequency_storage_dict

def calculate_expected_value_in_multi_dice_roll(frequency_storage_dict: Dict[int, List[float]]) -> float:
    """
    Returns the expected value from the distribution table 
    """

    if not frequency_storage_dict: 
        raise ValueError('Distribution table data not available!')

    current_sum: float = 0.0
    for key, (_, probability) in frequency_storage_dict.items():
        product_value = key * probability
        current_sum += product_value

    return current_sum
        
def calculate_variance_of_data(frequency_storage_dict: Dict[int, List[float]]) -> float:
    """
    Returns the variance of data points in the given dataset and return it 
    """

    total_data_points: int = len(frequency_storage_dict)
    data_points: List[int] = list(frequency_storage_dict.keys())
    probability_values: List[List[float]] = list(frequency_storage_dict.values())
    data_point_difference_from_mean: List[float] = [0] * len(data_points)

    data_points_sum = 0

    for data in data_points:
        data_points_sum += data

    mean_of_data_points: float = data_points_sum / total_data_points

    for index, data in enumerate(data_points):
        data_point_difference_from_mean[index] = ((data - mean_of_data_points) ** 2) * probability_values[index][1]

    variance: float = sum(data_point_difference_from_mean)

    return variance