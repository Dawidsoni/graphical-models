import unittest

from factor import Factor
from random_variable import RandomVariable


class TestFactor(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_variables = [
            RandomVariable('x', (1, 2)),
            RandomVariable('y', (3, 4, 5)),
            RandomVariable('z', (2, ))
        ]

    def test_get_assignments(self):
        factor = Factor(self.random_variables)
        assignments = factor.get_random_variables_assignments()
        self.assertEqual({(1, 3, 2), (1, 4, 2), (1, 5, 2), (2, 3, 2), (2, 4, 2), (2, 5, 2)}, set(assignments))

    def test_get_value(self):
        factor = Factor(self.random_variables)
        factor.add_value([1, 3, 2], 10).add_value([2, 4, 2], 20).add_value([2, 5, 2], 30)
        self.assertEqual(factor.get_value([1, 3, 2]), 10)
        self.assertEqual(factor.get_value([2, 4, 2]), 20)
        self.assertEqual(factor.get_value([2, 5, 2]), 30)
        self.assertEqual(factor.get_value([1, 4, 2]), 0)
        self.assertEqual(factor.get_value([2, 3, 2]), 0)

    def test_get_constant_multiplied(self):
        factor = Factor(self.random_variables)
        factor.add_value([1, 3, 2], 10).add_value([2, 4, 2], 20).add_value([2, 5, 2], 30)
        factor = factor.get_constant_multiplied(2)
        self.assertEqual(factor.get_value([1, 3, 2]), 20)
        self.assertEqual(factor.get_value([2, 4, 2]), 40)
        self.assertEqual(factor.get_value([2, 5, 2]), 60)
        self.assertEqual(factor.get_value([1, 4, 2]), 0)
        self.assertEqual(factor.get_value([2, 3, 2]), 0)

    def test_get_inverse(self):
        factor = Factor(self.random_variables)
        factor.add_value([1, 3, 2], 10).add_value([2, 4, 2], 20).add_value([2, 5, 2], 30)
        factor = factor.get_inverse()
        self.assertEqual(factor.get_value([1, 3, 2]), 1 / 10)
        self.assertEqual(factor.get_value([2, 4, 2]), 1 / 20)
        self.assertEqual(factor.get_value([2, 5, 2]), 1 / 30)
        self.assertEqual(factor.get_value([1, 4, 2]), float("inf"))
        self.assertEqual(factor.get_value([2, 3, 2]), float("inf"))

    def test_get_with_evidences(self):
        init_factor = Factor(self.random_variables)
        init_factor.add_value([1, 3, 2], 10).add_value([2, 4, 2], 20).add_value([2, 5, 2], 30)
        factor = init_factor.get_with_evidences({self.random_variables[0]: 2})
        self.assertEqual({(2, 3, 2), (2, 4, 2), (2, 5, 2)}, set(factor.get_random_variables_assignments()))
        self.assertEqual(factor.get_value([2, 4, 2]), 20)
        self.assertEqual(factor.get_value([2, 5, 2]), 30)
        factor = init_factor.get_with_evidences({self.random_variables[0]: 2, self.random_variables[1]: 4})
        self.assertEqual({(2, 4, 2)}, set(factor.get_random_variables_assignments()))
        self.assertEqual(factor.get_value([2, 4, 2]), 20)

    def test_get_sum_marginalized(self):
        init_factor = Factor(self.random_variables)
        init_factor.add_value([1, 3, 2], 10).add_value([1, 4, 2], 5).add_value([1, 5, 2], 2)
        init_factor.add_value([2, 4, 2], 20).add_value([2, 5, 2], 30)
        factor = init_factor.get_sum_marginalized([self.random_variables[0]])
        self.assertEqual(25, factor.get_value({'y': 4, 'z': 2}))
        self.assertEqual(32, factor.get_value({'y': 5, 'z': 2}))
        self.assertEqual(10, factor.get_value({'y': 3, 'z': 2}))
        factor = init_factor.get_sum_marginalized(self.random_variables)
        self.assertEqual(67, factor.get_value([]))

    def test_get_max_marginalized_with_assignments(self):
        init_factor = Factor(self.random_variables)
        init_factor.add_value([1, 3, 2], 10).add_value([1, 4, 2], 5).add_value([1, 5, 2], 2)
        init_factor.add_value([2, 4, 2], 20).add_value([2, 5, 2], 30)
        factor, assignment = init_factor.get_max_marginalized_with_assignments([self.random_variables[0]])
        marginalized_variables = [self.random_variables[1], self.random_variables[2]]
        self.assertEqual(20, factor.get_value({'y': 4, 'z': 2}))
        self.assertEqual(30, factor.get_value({'y': 5, 'z': 2}))
        self.assertEqual(10, factor.get_value({'y': 3, 'z': 2}))
        variable_permutation = list(map(lambda x: factor.random_variables.index(x), marginalized_variables))
        mapped_assignment = {}
        for key, value in assignment.items():
            mapped_key = tuple(map(lambda x: key[variable_permutation[x]], range(len(key))))
            mapped_assignment[mapped_key] = value
        self.assertEqual({(3, 2): (1,), (4, 2): (2,), (5, 2): (2,)}, mapped_assignment)
        factor, assignment = init_factor.get_max_marginalized_with_assignments(self.random_variables)
        self.assertEqual(30, factor.get_value([]))
        self.assertEqual({(): (2, 5, 2)}, assignment)

    def test_get_multiplied(self):
        factor1 = Factor([self.random_variables[0], self.random_variables[1]])
        factor2 = Factor([self.random_variables[1], self.random_variables[2]])
        factor1.add_value([1, 3], 10).add_value([1, 4], 20).add_value([2, 4], 30)
        factor2.add_value([3, 2], 5).add_value([4, 2], 2)
        product_factor = factor1.get_multiplied(factor2)
        self.assertEqual(product_factor.get_value({'x': 1, 'y': 3, 'z': 2}), 50)
        self.assertEqual(product_factor.get_value({'x': 1, 'y': 4, 'z': 2}), 40)
        self.assertEqual(product_factor.get_value({'x': 2, 'y': 4, 'z': 2}), 60)
        self.assertEqual(product_factor.get_value({'x': 1, 'y': 5, 'z': 2}), 0)
        self.assertEqual(product_factor.get_value({'x': 2, 'y': 5, 'z': 2}), 0)
        self.assertEqual(product_factor.get_value({'x': 2, 'y': 5, 'z': 2}), 0)

