from functools import reduce

from random_variables import get_variable_with_evidence


class VeMarginalInference(object):

    def __init__(self, graphical_model, ordering_strategy):
        self.graphical_model = graphical_model
        self.ordering_strategy = ordering_strategy
        self.normalizing_constant = self._get_marginal_potential_factor([], {}).get_value([])

    def _get_marginal_potential_factor(self, marginal_variables, variables_evidences):
        factors = list(map(lambda x: x.get_with_evidences(variables_evidences), self.graphical_model.factors))
        random_variables = self.graphical_model.random_variables
        random_variables = list(map(lambda x: get_variable_with_evidence(x, variables_evidences), random_variables))
        marginal_variables = list(map(lambda x: get_variable_with_evidence(x, variables_evidences), marginal_variables))
        variables_to_eliminate = list(set(random_variables).difference(marginal_variables))
        elimination_ordering = self.ordering_strategy(factors, variables_to_eliminate)
        variables_to_eliminate = list(map(lambda x: variables_to_eliminate[x], elimination_ordering))
        for random_variable in variables_to_eliminate:
            non_variable_factors = list(filter(lambda x: random_variable not in x.random_variables, factors))
            variable_factors = list(filter(lambda x: random_variable in x.random_variables, factors))
            product_factor = reduce(lambda x, y: x.get_multiplied(y), variable_factors)
            marginalized_factor = product_factor.get_sum_marginalized([random_variable])
            factors = non_variable_factors + [marginalized_factor]
        return reduce(lambda x, y: x.get_multiplied(y), factors)

    def get_marginal_probability_factor(self, marginal_variables, variables_evidences):
        potential_factor = self._get_marginal_potential_factor(marginal_variables, variables_evidences)
        return potential_factor.get_constant_multiplied(1 / self.normalizing_constant)

    def get_marginal_factor(self, marginal_variables, variables_evidences):
        marginal_factor = self.get_marginal_probability_factor(marginal_variables, variables_evidences)
        evidence_factor = self.get_marginal_probability_factor([], variables_evidences)
        return marginal_factor.get_constant_multiplied(1 / evidence_factor.get_value([]))
