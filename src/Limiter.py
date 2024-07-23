import random
import time
from pyrate_limiter import Rate, Limiter, Duration, BucketFullException
from contextlib import contextmanager
from typing import List, Union
import requests

class RateLimiter:
    total_time = 0

    def __init__(self, requests_per_second):
        self.rate = Rate(requests_per_second, Duration.SECOND)
        self.limiter = Limiter(self.rate)

    def _wait_for_available_slot(self):
        while True:
            try:
                self.limiter.try_acquire('key')
                break
            except BucketFullException as e:
                delay = random.uniform(1, 2)
                print(f"Rate limit exceeded. Retrying in {delay:.2f} seconds.")
                time.sleep(delay)

    def apply(self, func, *args, **kwargs):
        self._wait_for_available_slot()
        with self.time_it():
            result = func(*args, **kwargs)
        return result

    @contextmanager
    def time_it(self):
        start_time = time.time()
        yield
        end_time = time.time()
        elapsed_time = end_time - start_time
        RateLimiter.total_time += elapsed_time

    def __del__(self):
        print(f"Total time taken for API requests: {RateLimiter.total_time:.2f} seconds")