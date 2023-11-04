import json
import random


def generate():
    config_file_path = 'config.json'

    with open(config_file_path, 'r') as file:
        config = json.load(file)

    rand_numbers = []
    for i in range(0, config.get('cities_per_round')):
        rand = random.randint(0, 55)
        while rand in rand_numbers:
            rand = random.randint(0, 55)
        rand_numbers.append(rand)
    return rand_numbers
