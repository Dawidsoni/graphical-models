class GraphicalModel(object):

    def __init__(self):
        self.random_variables = set()
        self.factors = []

    def add_factor(self, factor):
        for random_variable in factor.random_variables:
            self.random_variables.add(random_variable)
        self.factors.append(factor)
        return self
