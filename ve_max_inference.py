from functools import reduce

from random_variables import get_variable_with_evidence
from ve_marginal_inference import VeMarginalInference


class VeMaxInference:

    def __init__(self, graphical_model, ordering_strategy):
        self.graphical_model = graphical_model
        self.ordering_strategy = ordering_strategy
        self.marginal_inference = VeMarginalInference(graphical_model, ordering_strategy)
        self.normalizing_constant = self.marginal_inference.normalizing_constant

    @staticmethod
    def _reconstruct_assignments(applied_assignment, variables_assignments):
        local_variables_assignments = variables_assignments.copy()
        while len(local_variables_assignments) > 0:
            for needed_variables in list(local_variables_assignments.keys()):
                if any([x not in applied_assignment.keys() for x in needed_variables]):
                    continue
                assignment_values = tuple(map(lambda x: applied_assignment[x], needed_variables))
                applied_assignment.update(local_variables_assignments[needed_variables][assignment_values])
                del local_variables_assignments[needed_variables]
        return applied_assignment

    def get_factor_assignment(self, marginal_variables, variables_evidences):
        factors = list(map(lambda x: x.get_with_evidences(variables_evidences), self.graphical_model.factors))
        random_variables = self.graphical_model.random_variables
        random_variables = list(map(lambda x: get_variable_with_evidence(x, variables_evidences), random_variables))
        marginal_variables = list(map(lambda x: get_variable_with_evidence(x, variables_evidences), marginal_variables))
        variables_to_eliminate = list(set(random_variables).difference(marginal_variables))
        elimination_ordering = self.ordering_strategy(factors, variables_to_eliminate)
        variables_to_eliminate = list(map(lambda x: variables_to_eliminate[x], elimination_ordering))
        variables_assignments = {}
        for random_variable in variables_to_eliminate:
            non_variable_factors = list(filter(lambda x: random_variable not in x.random_variables, factors))
            variable_factors = list(filter(lambda x: random_variable in x.random_variables, factors))
            product_factor = reduce(lambda x, y: x.get_multiplied(y), variable_factors)
            marginalized_factor, assignment = product_factor.get_max_marginalized([random_variable])
            assignment = {key: {random_variable: x for x in val} for key, val in assignment.items()}
            variables_assignments[tuple(marginalized_factor.random_variables)] = assignment
            factors = non_variable_factors + [marginalized_factor]
        max_factor = reduce(lambda x, y: x.get_multiplied(y), factors)
        evidence_factor = self.marginal_inference.get_marginal_probability_factor([], variables_evidences)
        max_factor = max_factor.get_constant_multiplied(1 / (evidence_factor.get_value([]) * self.normalizing_constant))
        max_assignments = {}
        for assignment in max_factor.get_random_variables_assignments():
            variables_assignment = {max_factor.random_variables[i]: assignment[i] for i in range(len(assignment))}
            max_assignments[assignment] = self._reconstruct_assignments(variables_assignment, variables_assignments)
        return max_factor, max_assignments


