import logging
import random
import math

logging.basicConfig(filename='my_log_file.txt', level=logging.DEBUG, 
                    format=' %(asctime)s -  %(levelname)s -  %(message)s')

def simulate_probability_of_single_dice(total_tries: int, object_type: str = 'dice') -> dict:

    """
    Simulates the probability of a single dice roll for times provided by the user

    Args:
    total_tries(int): Number of tries that can be made in the simulation

    Returns:
    The probability based on the above args
    """
    
    if total_tries <= 0:
        raise ValueError('Total tries should be >= 1')
        
    if object_type not in {'dice', 'coin'}: 
        raise ValueError('Object type should be dice or coin')
    
    if object_type == 'dice':

        frequency_storage_dict: dict = {
            1: [0,0],
            2: [0,0],
            3: [0,0],
            4: [0,0],
            5: [0,0],
            6: [0,0]
        }
        

        for i in range(total_tries):
            current_number: int = random.randint(1, 6)
            frequency_storage_dict[current_number][0] += 1

        for i in frequency_storage_dict.items():
            if i[1][0] == 0: 
                continue
            i[1][1] = i[1][0] / total_tries

    else:

        frequency_storage_dict: dict = {
            'Heads': [0,0],
            'Tails': [0,0]
        }

        possible_results = ['Heads', 'Tails']

        for i in range(total_tries):
            current_result: str = random.choice(possible_results)
            frequency_storage_dict[current_result][0] += 1

        for i in frequency_storage_dict.items():
            if i[1][0] == 0: 
                continue
            i[1][1] = i[1][0] / total_tries

    return frequency_storage_dict

def display_distribution_table(frequency_storage_dict: dict, multi_dice: bool = False) -> None:
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

def display_multiple_dice_simulation_parameters(dice_number: int = 2, sides_per_dice: int = 6, total_rolls: int = 1000):

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
    
    if dice_number < 0 or dice_number > 4: 
        raise ValueError('Choose number of dice between 1 and 4')
    
    if sides_per_dice < 1 or sides_per_dice > 10: 
        raise ValueError('Entered incorrect value for sides per dice. Enter value between 1 and 10')
    
    total_sum_possible: range = range(dice_number, dice_number * sides_per_dice + 1)

    frequency_storage_dict: dict = {}

    dice_roll_results: list = []

    for i in total_sum_possible:
        key: int = i
        value_list: list = [0, 0]
        frequency_storage_dict[key] = value_list

    for i in range(total_rolls):
        dice_values = [random.randint(1, sides_per_dice) for _ in range(dice_number)]
        total: int = sum(dice_values)
        dice_roll_results.append((dice_values, total))
        frequency_storage_dict[total][0] += 1

    for i in frequency_storage_dict.items():
        if i[1][0] == 0: 
            continue
        i[1][1] = i[1][0] / total_rolls

    return frequency_storage_dict

def calculate_expected_value_in_multi_dice_roll(frequency_storage_dict: dict) -> float:
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
        
def calculate_variance_of_data(frequency_storage_dict: dict):
    """
    Returns the variance of data points in the given dataset
    """

    total_data_points: int = len(frequency_storage_dict)
    data_points: list = list(frequency_storage_dict.keys())
    probability_values: list = list(frequency_storage_dict.values())
    data_point_difference_from_mean: list = [0] * len(data_points)

    data_points_sum = 0

    for data in data_points:
        data_points_sum += data

    mean_of_data_points: float = data_points_sum / total_data_points
    #print(f'The data_points in the distribution table are: {data_points}')

    for index, data in enumerate(data_points):
        data_point_difference_from_mean[index] = ((data - mean_of_data_points) ** 2) * probability_values[index][1]

    #print(data_point_difference_from_mean)
    variance: float = sum(data_point_difference_from_mean)

    return variance