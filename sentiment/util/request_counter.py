import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from threading import Lock

from sentiment.util.exceptions import SentimentStatException


class Collector:
    def __init__(self):
        self.collector = deque()
        self.lock = Lock()

    def increment(self):
        current = datetime.now()
        with self.lock:
            self.collector.append(current)

    def per_minute(self):
        now = datetime.now()
        one_minute_before = now - timedelta(minutes=1)

        # remove all api calls that are older than one hour
        with self.lock:
            while self.collector and self.collector[0] < one_minute_before:
                self.collector.popleft()

        return len(self.collector)


class RequestStatistics:
    """Simple in-memory data structure to store API request details
    """

    def __init__(self):
        self.stat_cache = defaultdict(Collector)

    def register_new_call(self, api):
        """Use this method to register API calls.

        Args:
            api (str): API name for example: health, predict
        """
        self.stat_cache[api].increment()

    def num_calls_per_minute(self, api):
        """Calculates and returns the number of API calls happens in this minute 

        Args:
            api (str): API name for example: health, predict

        Returns:
            int: number of API calls of this minute
        """
        return self.stat_cache[api].per_minute()
