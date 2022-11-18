from diagnosis import Diagnose
from datetime import datetime, date, timedelta

import pytest

parent = None
dg = Diagnose(parent)


def test_name():
    with pytest.raises(ValueError):
        dg.name = None


def test_date_none():
    with pytest.raises(ValueError):
        dg.date = None


def test_date_tomorrow():
    with pytest.raises(ValueError):
        dg.date = date.today() + timedelta(days=1)


def test_date_string():
    with pytest.raises(ValueError):
        dg.date = "today"


def test_hand():
    with pytest.raises(ValueError):
        dg.hand = "some"


def test_thumb():
    with pytest.raises(ValueError):
        dg.finger = 0


def test_alien_finger():
    with pytest.raises(ValueError):
        dg.finger = 5


def test_pulleys():
    with pytest.raises(ValueError):
        dg.pulleys = None


def test_pulleys_strings():
    with pytest.raises(ValueError):
        dg.pulleys = [
            "words",
            "no",
            "numbers",
        ]


def test_pulleys_a5():
    with pytest.raises(ValueError):
        dg.pulleys = [0, 1, 2, 3]


def test_pulleys_a1():
    with pytest.raises(ValueError):
        dg.pulleys = [
            -1,
            0,
            1,
            2,
        ]


def test_grade():
    with pytest.raises(ValueError):
        dg.grade = 0


def test_pulleys_strings():
    with pytest.raises(ValueError):
        dg.grade = "words"


def test_pulleys_none():
    with pytest.raises(ValueError):
        dg.grade = None
