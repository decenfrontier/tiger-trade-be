import pickle
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


def save_obj_into_file(obj, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(obj, file)


def load_obj_from_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            obj = pickle.load(file)
    except:
        obj = None
    return obj
