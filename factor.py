from collections import Counter

from random_variables import RandomVariable


class Factor(object):

    def __init__(self, random_variables):
        self.random_variables = random_variables
        self.factor_values = {}

    def _get_processed_variable_values(self, variable_values):
        if type(variable_values) == dict:
            return tuple(map(lambda x: variable_values[x.name], self.random_variables))
        elif type(variable_values) == list:
            return tuple(variable_values)
        elif type(variable_values) == tuple:
            return variable_values
        raise Exception("Invalid type of variable values")

    def _assert_valid_variables_values(self, variable_values):
        for i in range(len(self.random_variables)):
            if variable_values[i] not in self.random_variables[i].values:
                raise Exception("Invalid value for at least one random variable")

    def add_value(self, variables_values, factor_value):
        variables_values = self._get_processed_variable_values(variables_values)
        self._assert_valid_variables_values(variables_values)
        self.factor_values[variables_values] = factor_value
        return self

    def get_random_variables_assignments(self):
        if len(self.random_variables) == 0:
            return [[]]
        assignments = list(map(lambda x: (x, ), self.random_variables[0].values))
        for i in range(1, len(self.random_variables)):
            assignments = [assignment + (x, ) for assignment in assignments for x in self.random_variables[i].values]
        return assignments

    def get_value(self, variables_values):
        variables_values = self._get_processed_variable_values(variables_values)
        self._assert_valid_variables_values(variables_values)
        if variables_values not in self.factor_values:
            return 0
        return self.factor_values[variables_values]

    def get_constant_multiplied(self, constant):
        multiplied_factor = Factor(self.random_variables)
        for assignment in self.get_random_variables_assignments():
            multiplied_factor.add_value(assignment, self.get_value(assignment) * constant)
        return multiplied_factor

    def get_inverse(self):
        inverse_factor = Factor(self.random_variables)
        for assignment in self.get_random_variables_assignments():
            assigned_value = self.get_value(assignment)
            inverse_factor.add_value(assignment, 1 / assigned_value if assigned_value != 0 else float("inf"))
        return inverse_factor

    def get_multiplied(self, factor):
        summed_random_variables = list(set(self.random_variables).union(factor.random_variables))
        indexes_of_variables = {x[1]: x[0] for x in enumerate(summed_random_variables)}
        product_factor = Factor(summed_random_variables)
        for assignment in product_factor.get_random_variables_assignments():
            left_assignment = tuple(map(lambda x: assignment[indexes_of_variables[x]], self.random_variables))
            right_assignment = tuple(map(lambda x: assignment[indexes_of_variables[x]], factor.random_variables))
            product_factor.add_value(assignment, self.get_value(left_assignment) * factor.get_value(right_assignment))
        return product_factor

    def get_sum_marginalized(self, eliminated_random_variables):
        factor_random_variables = list(set(self.random_variables).difference(eliminated_random_variables))
        indexes_of_variables = {x[1]: x[0] for x in enumerate(self.random_variables)}
        indexes_of_factor_variables = list(map(lambda x: indexes_of_variables[x], factor_random_variables))
        marginalized_factor = Factor(factor_random_variables)
        marginalized_assignments = Counter()
        for assignment in self.get_random_variables_assignments():
            marginalized_assignment = tuple(map(lambda x: assignment[x], indexes_of_factor_variables))
            marginalized_assignments[marginalized_assignment] += self.get_value(assignment)
        for variable_values, factor_value in marginalized_assignments.items():
            marginalized_factor.add_value(variable_values, factor_value)
        return marginalized_factor

    def get_max_marginalized(self, eliminated_random_variables):
        factor_random_variables = list(set(self.random_variables).difference(eliminated_random_variables))
        indexes_of_variables = {x[1]: x[0] for x in enumerate(self.random_variables)}
        indexes_of_eliminated_variables = list(map(lambda x: indexes_of_variables[x], eliminated_random_variables))
        indexes_of_factor_variables = list(map(lambda x: indexes_of_variables[x], factor_random_variables))
        marginalized_factor = Factor(factor_random_variables)
        marginalized_assignments = Counter()
        eliminated_variables_assignments = {}
        for assignment in self.get_random_variables_assignments():
            marginalized_assignment = tuple(map(lambda x: assignment[x], indexes_of_factor_variables))
            eliminated_assignment = tuple(map(lambda x: assignment[x], indexes_of_eliminated_variables))
            if marginalized_assignments[marginalized_assignment] <= self.get_value(assignment):
                marginalized_assignments[marginalized_assignment] = self.get_value(assignment)
                eliminated_variables_assignments[marginalized_assignment] = eliminated_assignment
        for variable_values, factor_value in marginalized_assignments.items():
            marginalized_factor.add_value(variable_values, factor_value)
        return marginalized_factor, eliminated_variables_assignments

    def get_with_evidences(self, variables_evidences):
        evidence_random_variables = []
        for random_variable in self.random_variables:
            if random_variable in variables_evidences:
                evidence_values = (variables_evidences[random_variable], )
                evidence_random_variables.append(RandomVariable(random_variable.name, evidence_values))
            else:
                evidence_random_variables.append(random_variable)
        evidence_factor = Factor(evidence_random_variables)
        for assignment in evidence_factor.get_random_variables_assignments():
            evidence_factor.add_value(assignment, self.get_value(assignment))
        return evidence_factor

    def get_normalized(self):
        factors_sum = sum(map(lambda x: self.get_value(x), self.get_random_variables_assignments()))
        return self.get_constant_multiplied(1 / factors_sum)
