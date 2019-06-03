import unittest

from factor import Factor
from graphical_model import GraphicalModel
from random_variable import RandomVariable


class TestGraphicalModel(unittest.TestCase):

    def test_add_factors(self):
        graphical_model = GraphicalModel()
        factor1 = Factor([RandomVariable('x', (1, 2))])
        factor2 = Factor([RandomVariable('y', (2, 3, 4)), RandomVariable('z', (2, ))])
        factor3 = Factor([RandomVariable('x', (1, 2)), RandomVariable('z', (2, ))])
        graphical_model.add_factor(factor1).add_factor(factor2).add_factor(factor3)
        print(graphical_model.random_variables)
