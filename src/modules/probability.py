import logging
import random

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s -  %(message)s')

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
        
    if object_type != 'dice' and object_type != 'coin': 
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

def display_distribution_table(frequency_storage_dict: dict) -> None:
    for key, (frequency, probability) in frequency_storage_dict.items():
        print(f'Number: {key}, Frequency: {frequency}, Probability: {probability}')

    return
