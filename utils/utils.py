import random


def generate_random_number(length):
    random_number = random.randint(10**(length-1), 10**length - 1)
    return str(random_number).zfill(length)


