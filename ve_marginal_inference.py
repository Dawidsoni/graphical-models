from functools import reduce


class VeMarginalInference(object):

    def __init__(self, graphical_model, ordering_strategy):
        self.graphical_model = graphical_model
        self.ordering_strategy = ordering_strategy
        self.normalizing_constant = self.get_marginal_factor([], {})

    def _get_marginal_probability_factor(self, marginal_variables, variables_evidences):
        factors = list(map(lambda x: x.get_with_evidences(variables_evidences), self.graphical_model.factors))
        variables_to_eliminate = list(set(self.graphical_model.random_variables).difference(marginal_variables))
        elimination_ordering = self.ordering_strategy(factors, variables_to_eliminate)
        variables_to_eliminate = list(map(lambda x: variables_to_eliminate[x], elimination_ordering))
        for random_variable in variables_to_eliminate:
            non_variable_factors = list(filter(lambda x: random_variable not in x.random_variables, factors))
            variable_factors = list(filter(lambda x: random_variable in x.random_variables, factors))
            product_factor = reduce(lambda x, y: x.get_multiplied(y), variable_factors)
            marginalized_factor = product_factor.get_sum_marginalized([random_variable])
            factors = non_variable_factors + [marginalized_factor]
        return reduce(lambda x, y: x.get_multiplied(y), factors).get_multiplied(1 / self.normalizing_constant)

    def get_marginal_factor(self, marginal_variables, variables_evidences):
        marginal_factor = self._get_marginal_probability_factor(marginal_variables, variables_evidences)
        evidence_factor = self._get_marginal_probability_factor([], variables_evidences)
        return marginal_factor.get_multiplied(evidence_factor.get_inverse())
