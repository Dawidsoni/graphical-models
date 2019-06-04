import unittest

from factor import Factor
from graphical_model import GraphicalModel
from random_variables import RandomVariable, get_variable_with_evidence
from ve_max_inference import VeMaxInference
from ordering_strategies import min_neighbours_ordering


class TestVeMaxInference(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_variables = [
            RandomVariable('x', (1, 2)),
            RandomVariable('y', (3, 4, 5)),
            RandomVariable('z', (2, ))
        ]

    def _generate_two_variables_model(self):
        x_factor = Factor([self.random_variables[0]])
        x_factor.add_value([1], 1).add_value([2], 2)
        y_factor = Factor([self.random_variables[1]])
        y_factor.add_value([3], 5).add_value([4], 10).add_value([5], 15)
        xy_factor = Factor([self.random_variables[0], self.random_variables[1]])
        xy_factor.add_value([1, 3], 10).add_value([1, 4], 10).add_value([2, 5], 20)
        graphical_model = GraphicalModel()
        graphical_model.add_factor(x_factor).add_factor(y_factor).add_factor(xy_factor)
        return graphical_model

    def _generate_three_variables_model(self):
        xy_factor = Factor([self.random_variables[0], self.random_variables[1]])
        xy_factor.add_value([1, 3], 5).add_value([1, 4], 20).add_value([2, 5], 30)
        xz_factor = Factor([self.random_variables[0], self.random_variables[2]])
        xz_factor.add_value([1, 2], 10).add_value([2, 2], 20)
        yz_factor = Factor([self.random_variables[1], self.random_variables[2]])
        yz_factor.add_value([3, 2], 10).add_value([4, 2], 20).add_value([5, 2], 30)
        graphical_model = GraphicalModel()
        graphical_model.add_factor(xy_factor).add_factor(xz_factor).add_factor(yz_factor)
        return graphical_model

    def test_two_variables_x_marginal_no_evidence(self):
        graphical_model = self._generate_two_variables_model()
        max_inference = VeMaxInference(graphical_model, min_neighbours_ordering)
        max_factor, assignment = max_inference.get_factor_assignment([self.random_variables[0]], {})
        self.assertEqual(4, assignment[(1, )][self.random_variables[1]])
        self.assertEqual(5, assignment[(2, )][self.random_variables[1]])
        self.assertAlmostEqual(2 / 15, max_factor.get_value([1]))
        self.assertAlmostEqual(12/ 15, max_factor.get_value([2]))
        self.assertEqual(4, assignment[(1, )][self.random_variables[1]])
        self.assertEqual(5, assignment[(2, )][self.random_variables[1]])

    def test_two_variables_x_marginal_with_evidence(self):
        graphical_model = self._generate_two_variables_model()
        max_inference = VeMaxInference(graphical_model, min_neighbours_ordering)
        variables_evidence = {self.random_variables[0]: 2}
        max_factor, assignment = max_inference.get_factor_assignment([self.random_variables[0]], variables_evidence)
        self.assertEqual(5, assignment[(2, )][self.random_variables[1]])
        self.assertAlmostEqual(1.0, max_factor.get_value([2]))
        self.assertEqual(5, assignment[(2, )][self.random_variables[1]])

    def test_two_variables_y_marginal_with_evidence(self):
        graphical_model = self._generate_two_variables_model()
        max_inference = VeMaxInference(graphical_model, min_neighbours_ordering)
        variables_evidence = {self.random_variables[0]: 2}
        max_factor, assignment = max_inference.get_factor_assignment([self.random_variables[1]], variables_evidence)
        self.assertAlmostEqual(0.0, max_factor.get_value([3]))
        self.assertAlmostEqual(0.0, max_factor.get_value([4]))
        self.assertAlmostEqual(1.0, max_factor.get_value([5]))
        x_with_evidence = get_variable_with_evidence(self.random_variables[0], variables_evidence)
        self.assertEqual(2, assignment[(3, )][x_with_evidence])
        self.assertEqual(2, assignment[(4, )][x_with_evidence])
        self.assertEqual(2, assignment[(5, )][x_with_evidence])

    def test_two_variables_xy_marginal_no_evidence(self):
        graphical_model = self._generate_two_variables_model()
        max_inference = VeMaxInference(graphical_model, min_neighbours_ordering)
        max_factor, assignment = max_inference.get_factor_assignment(self.random_variables, {})
        self.assertAlmostEqual(1 / 15, max_factor.get_value({'x': 1, 'y': 3}))
        self.assertAlmostEqual(2 / 15, max_factor.get_value({'x': 1, 'y':4}))
        self.assertAlmostEqual(12 / 15, max_factor.get_value({'x': 2, 'y': 5}))
        for key, val in assignment.items():
            dict_key = {max_factor.random_variables[i]: key[i] for i in range(len(max_factor.random_variables))}
            self.assertEqual(dict_key, val)

    def test_three_variables_x_marginal_no_evidence(self):
        graphical_model = self._generate_three_variables_model()
        max_inference = VeMaxInference(graphical_model, min_neighbours_ordering)
        max_factor, assignment = max_inference.get_factor_assignment([self.random_variables[0]], {})
        self.assertEqual([1, 4, 2], list(map(lambda x: assignment[(1,)][x], self.random_variables)))
        self.assertEqual([2, 5, 2], list(map(lambda x: assignment[(2,)][x], self.random_variables)))
        self.assertAlmostEqual(8 / 45, max_factor.get_value([1]))
        self.assertAlmostEqual(36 / 45, max_factor.get_value([2]))

    def test_three_variables_x_marginal_with_evidence(self):
        graphical_model = self._generate_three_variables_model()
        max_inference = VeMaxInference(graphical_model, min_neighbours_ordering)
        variables_evidence = {self.random_variables[0]: 1}
        max_factor, assignment = max_inference.get_factor_assignment([self.random_variables[0]], variables_evidence)
        self.assertEqual(4, assignment[(1, )][self.random_variables[1]])
        self.assertEqual(2, assignment[(1, )][self.random_variables[2]])
        self.assertAlmostEqual(8 / 9, max_factor.get_value([1]))


