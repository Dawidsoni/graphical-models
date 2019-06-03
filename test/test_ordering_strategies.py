import unittest

from factor import Factor
from ordering_strategies import min_neighbours_ordering
from random_variable import RandomVariable


class TestOrderingStrategies(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_variables = [
            RandomVariable('a', (1, 2)),
            RandomVariable('b', (3, 4, 5)),
            RandomVariable('c', (2, )),
            RandomVariable('d', (1, 2, 3, 4, 5, 6)),
        ]
        self.factors = [
            Factor([self.random_variables[0]]),
            Factor([self.random_variables[0], self.random_variables[1]]),
            Factor([self.random_variables[1], self.random_variables[2]])
        ]

    def test_neighbours_ordering(self):
        self.assertEqual([3, 0, 2, 1], min_neighbours_ordering(self.factors, self.random_variables))
