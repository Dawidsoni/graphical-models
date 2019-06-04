import unittest

from factor import Factor
from graphical_model import GraphicalModel
from random_variables import RandomVariable
from ve_marginal_inference import VeMarginalInference
from ordering_strategies import min_neighbours_ordering


class TestVeMarginalInference(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_variables = [
            RandomVariable('x', (1, 2)),
            RandomVariable('y', (3, 4, 5)),
            RandomVariable('z', (2, ))
        ]

    def test_two_variables(self):
        x_factor = Factor([self.random_variables[0]])
        x_factor.add_value([1], 1).add_value([2], 2)
        y_factor = Factor([self.random_variables[1]])
        y_factor.add_value([3], 5).add_value([4], 10).add_value([5], 15)
        xy_factor = Factor([self.random_variables[0], self.random_variables[1]])
        xy_factor.add_value([1, 3], 10).add_value([1, 4], 10).add_value([2, 5], 20)
        graphical_model = GraphicalModel()
        graphical_model.add_factor(x_factor).add_factor(y_factor).add_factor(xy_factor)
        marginal_inference = VeMarginalInference(graphical_model, min_neighbours_ordering)
        marginal_factor = marginal_inference.get_marginal_factor([self.random_variables[0]], {})
        self.assertAlmostEqual(0.2, marginal_factor.get_value([1]))
        self.assertAlmostEqual(0.8, marginal_factor.get_value([2]))
        variables_evidence = {self.random_variables[0]: 2}
        marginal_factor = marginal_inference.get_marginal_factor([self.random_variables[0]], variables_evidence)
        self.assertAlmostEqual(1.0, marginal_factor.get_value([2]))
        marginal_factor = marginal_inference.get_marginal_factor([self.random_variables[1]], variables_evidence)
        self.assertAlmostEqual(0.0, marginal_factor.get_value([3]))
        self.assertAlmostEqual(0.0, marginal_factor.get_value([4]))
        self.assertAlmostEqual(1.0, marginal_factor.get_value([5]))
        marginal_factor = marginal_inference.get_marginal_factor(self.random_variables, {})
        self.assertAlmostEqual(1 / 15, marginal_factor.get_value({'x': 1, 'y': 3}))
        self.assertAlmostEqual(2 / 15, marginal_factor.get_value({'x': 1, 'y':4}))
        self.assertAlmostEqual(12 / 15, marginal_factor.get_value({'x': 2, 'y': 5}))

    def test_three_variables(self):
        xy_factor = Factor([self.random_variables[0], self.random_variables[1]])
        xy_factor.add_value([1, 3], 5).add_value([1, 4], 20).add_value([2, 5], 30)
        xz_factor = Factor([self.random_variables[0], self.random_variables[2]])
        xz_factor.add_value([1, 2], 10).add_value([2, 2], 20)
        yz_factor = Factor([self.random_variables[1], self.random_variables[2]])
        yz_factor.add_value([3, 2], 10).add_value([4, 2], 20).add_value([5, 2], 30)
        graphical_model = GraphicalModel()
        graphical_model.add_factor(xy_factor).add_factor(xz_factor).add_factor(yz_factor)
        marginal_inference = VeMarginalInference(graphical_model, min_neighbours_ordering)
        marginal_factor = marginal_inference.get_marginal_factor([self.random_variables[0]], {})
        self.assertAlmostEqual(0.2, marginal_factor.get_value([1]))
        self.assertAlmostEqual(0.8, marginal_factor.get_value([2]))
        variables_evidence = {self.random_variables[0]: 1}
        marginal_factor = marginal_inference.get_marginal_factor([self.random_variables[0]], variables_evidence)
        self.assertAlmostEquals(1.0, marginal_factor.get_value([1]))


