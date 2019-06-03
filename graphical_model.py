class GraphicalModel(object):

    def __init__(self):
        self.random_variables = set()
        self.factors = []

    def add_factor(self, factor):
        self.random_variables.update(factor.random_variables)
        self.factors.append(factor)
        return self
