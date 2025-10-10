import logging
import random

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s -  %(message)s')

def simulate_single_probability(acceptable_outcome: int, total_possible_outcomes: int, total_tries: int) -> dict:

    """
    Simulates the probability of the object based on given parameters

    Args:
    acceptable_outcome(int): Total number of outcomes acceptable to the user
    total_possible_outcomes(int): Total number of outcomes that can occur
    total_tries(int): Number of tries that can be made in the simulation

    Returns:
    The probability based on the above args
    """

    if acceptable_outcome <= 0 or total_possible_outcomes <= 0:
        raise ValueError('Cannot be less than or equal to 0')
    
    if total_possible_outcomes < acceptable_outcome:
        raise ValueError('Possible outcomes cannot be < acceptable outcomes')
    
    if total_tries <= 0:
        raise ValueError('Total tries should be >= 1')
    

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
        i[1][1] = i[1][0] / total_possible_outcomes

    return frequency_storage_dict

def display_distribution_table(frequency_storage_dict: dict) -> None:
    for key, (frequency, probability) in frequency_storage_dict.items():
        print(f'Number: {key}, Frequency: {frequency}, Probability: {probability}')

    return