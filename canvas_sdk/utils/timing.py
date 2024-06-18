from time import time


def get_duration_ms(start_time: time) -> int:
    return int((time() - start_time) * 1000)
