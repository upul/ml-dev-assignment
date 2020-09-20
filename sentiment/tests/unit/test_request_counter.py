import time

import pytest

from sentiment.util.request_counter import RequestStatistics


def test_request_stat_counter_happy_path():
    counter = RequestStatistics()

    counter.register_new_call('health')
    counter.register_new_call('health')
    counter.register_new_call('health')

    # three calls in current minute
    num_calls = counter.num_calls_per_minute('health')
    assert num_calls == 3, f'expected: 6 actual: {num_calls}'

    time.sleep(60)

    # zero calls in the current minute
    num_calls = counter.num_calls_per_minute('health')
    assert num_calls == 0, f'expected: 6 actual: {num_calls}'


def test_request_stat_counter_time_span_more_than_one_min():
    counter = RequestStatistics()

    counter.register_new_call('health')
    counter.register_new_call('health')
    counter.register_new_call('health')

    # wait for 30 seconds
    time.sleep(30)

    counter.register_new_call('health')
    counter.register_new_call('health')
    counter.register_new_call('health')

    num_calls = counter.num_calls_per_minute('health')
    assert num_calls == 6, f'expected: 6 actual: {num_calls}'

    # wait another 35 second
    time.sleep(30)

    num_calls = counter.num_calls_per_minute('health')
    assert num_calls == 3, f'expected: 6 actual: {num_calls}'


def test_request_stat_counter_two_apis():
    counter = RequestStatistics()

    counter.register_new_call('health')
    counter.register_new_call('health')
    counter.register_new_call('health')

    counter.register_new_call('predict')
    counter.register_new_call('predict')
    counter.register_new_call('predict')

    num_calls = counter.num_calls_per_minute('health')
    assert num_calls == 3, f'api: health, expected: 6 actual: {num_calls}'

    num_calls = counter.num_calls_per_minute('predict')
    assert num_calls == 3, f'api: predict, expected: 6 actual: {num_calls}'

# TODO: (upul) a lot more cases such as concurrent insert to cover
