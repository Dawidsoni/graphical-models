import unittest

from factor import Factor
from graphical_model import GraphicalModel
from random_variables import RandomVariable
from mp_marginal_inference import MpMarginalInference


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
        marginal_inference = MpMarginalInference(graphical_model)
        marginal_factor = marginal_inference.get_marginal_factor(self.random_variables[0])
        self.assertAlmostEqual(0.2, marginal_factor.get_value([1]))
        self.assertAlmostEqual(0.8, marginal_factor.get_value([2]))

    def test_marginal_x_three_variables(self):
        x_factor = Factor([self.random_variables[0]])
        x_factor.add_value([1], 1).add_value([2], 2)
        xy_factor = Factor([self.random_variables[0], self.random_variables[1]])
        xy_factor.add_value([1, 3], 5).add_value([1, 4], 20).add_value([2, 5], 30)
        xz_factor = Factor([self.random_variables[0], self.random_variables[2]])
        xz_factor.add_value([1, 2], 12).add_value([2, 2], 20)
        graphical_model = GraphicalModel()
        graphical_model.add_factor(x_factor).add_factor(xy_factor).add_factor(xz_factor)
        marginal_inference = MpMarginalInference(graphical_model)
        marginal_factor = marginal_inference.get_marginal_factor(self.random_variables[0])
        self.assertAlmostEqual(0.2, marginal_factor.get_value([1]))
        self.assertAlmostEqual(0.8, marginal_factor.get_value([2]))

    def test_marginal_y_three_variables(self):
        x_factor = Factor([self.random_variables[0]])
        x_factor.add_value([1], 1).add_value([2], 2)
        xy_factor = Factor([self.random_variables[0], self.random_variables[1]])
        xy_factor.add_value([1, 3], 5).add_value([1, 4], 20).add_value([2, 5], 30)
        xz_factor = Factor([self.random_variables[0], self.random_variables[2]])
        xz_factor.add_value([1, 2], 12).add_value([2, 2], 20)
        graphical_model = GraphicalModel()
        graphical_model.add_factor(x_factor).add_factor(xy_factor).add_factor(xz_factor)
        marginal_inference = MpMarginalInference(graphical_model)
        marginal_factor = marginal_inference.get_marginal_factor(self.random_variables[1])
        self.assertAlmostEqual(0.04, marginal_factor.get_value([3]))
        self.assertAlmostEqual(0.16, marginal_factor.get_value([4]))
        self.assertAlmostEqual(0.8, marginal_factor.get_value([5]))

    @unittest.expectedFailure
    def test_cycle(self):
        xy_factor = Factor([self.random_variables[0], self.random_variables[1]])
        xz_factor = Factor([self.random_variables[0], self.random_variables[2]])
        yz_factor = Factor([self.random_variables[1], self.random_variables[2]])
        graphical_model = GraphicalModel()
        graphical_model.add_factor(xy_factor).add_factor(xz_factor).add_factor(yz_factor)
        marginal_inference = MpMarginalInference(graphical_model)
        marginal_inference.get_marginal_factor([self.random_variables[0]], {})
