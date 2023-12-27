import random
import time

from pkg.xlog import logger


def generate_random_number(length):
    random_number = random.randint(10**(length-1), 10**length - 1)
    return str(random_number).zfill(length)


def calc_func_elapsed_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f'Function {func.__name__} took {elapsed_time:.2f} seconds')
        return result
    return wrapper