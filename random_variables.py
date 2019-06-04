from collections import namedtuple

RandomVariable = namedtuple('RandomVariable', ['name', 'values'])


def get_variable_with_evidence(random_variable, variables_evidences):
    if random_variable in variables_evidences:
        return RandomVariable(random_variable.name, (variables_evidences[random_variable],))
    return random_variable
