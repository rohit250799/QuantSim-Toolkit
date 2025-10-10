def simulate_probability_of_dice_roll(acceptable_outcome: int, total_possible_outcomes: int, total_tries: int) -> None:
    if acceptable_outcome <= 0 or total_possible_outcomes <= 0:
        raise ValueError('Cannot be less than or equal to 0')
    
    if total_possible_outcomes < acceptable_outcome:
        raise ValueError('Possible outcomes cannot be < acceptable outcomes')
    
    if total_tries <= 0:
        raise ValueError('Total tries should be >= 1')
    
    print(f'This is for the testing of the function. Total tries = {total_tries}')

    return 