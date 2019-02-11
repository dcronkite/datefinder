import pytest
from dtfinder import dtfinder


def test_just_number():
    s = 'spouse, 3 children'
    assert len(list(dtfinder.find_dates(s))) == 0


def test_day_only():
    s = 'on the 3rd'
    assert len(list(dtfinder.find_dates(s))) == 1
