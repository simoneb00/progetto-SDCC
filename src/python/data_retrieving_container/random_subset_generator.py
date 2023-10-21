import random


def generate():
    rand_numbers = []
    for i in range(0, 10):
        rand = random.randint(0, 55)
        while rand in rand_numbers:
            rand = random.randint(0, 55)
        rand_numbers.append(rand)
    return rand_numbers
