
def min_neighbours_ordering(factors, random_variables):
    coupled_variables_sets = {x: set() for x in random_variables}
    for factor in factors:
        for random_variable in factor.random_variables:
            if random_variable in coupled_variables_sets:
                coupled_variables_sets[random_variable].update(factor.random_variables)
    sorted_variables = sorted(enumerate(random_variables), key=lambda x: len(coupled_variables_sets[x[1]]))
    return list(map(lambda x: x[0], sorted_variables))
