import datetime

import pytest
from dtfinder import dtfinder


def test_just_number():
    s = 'spouse, 3 children'
    assert len(list(dtfinder.find_dates(s))) == 0


def test_day_only():
    s = 'on the 3rd'
    assert len(list(dtfinder.find_dates(s))) == 1


def test_two_weeks_ago():
    s = '2 weeks ago'
    assert list(dtfinder.find_dates(s))[0] == datetime.timedelta(days=-14)


def test_large_number():
    s = 'Mirena NDC 5041942101 EXP 01/15'
    assert list(dtfinder.find_dates(s))[0] == datetime.datetime(year=1900, month=1, day=15)
