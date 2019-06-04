from collections import deque
from functools import reduce

from factor import Factor


class MpMarginalInference(object):

    def __init__(self, graphical_model):
        self.graphical_model = graphical_model
        self.factors_tree = self._generate_factors_tree()
        self.single_variable_factors = self._generate_single_variable_factors()
        self.variable_messages = self._generate_variable_messages()

    @staticmethod
    def _assert_valid_tree(tree):
        init_random_variable = list(tree.keys())[0]
        visited_nodes = set()
        source_nodes = {}
        nodes_queue = deque([init_random_variable])
        while len(nodes_queue) > 0:
            current_node = nodes_queue.popleft()
            visited_nodes.add(current_node)
            for neighbor_node, _factor in tree[current_node]:
                if neighbor_node in visited_nodes and source_nodes[current_node] != neighbor_node:
                    raise Exception("Constructed factor graph contains cycle")
                elif neighbor_node not in visited_nodes:
                    nodes_queue.append(neighbor_node)
                    source_nodes[neighbor_node] = current_node

    @staticmethod
    def _create_default_factor(random_variable):
        factor = Factor([random_variable])
        for value in random_variable.values:
            factor.add_value([value], 1)
        return factor

    def _generate_factors_tree(self):
        factors_tree = {random_variable: [] for random_variable in self.graphical_model.random_variables}
        for factor in self.graphical_model.factors:
            if len(factor.random_variables) > 2:
                raise Exception("Cannot construct tree with factor having more than 2 variables")
            elif len(factor.random_variables) == 2:
                factors_tree[factor.random_variables[0]].append((factor.random_variables[1], factor))
                factors_tree[factor.random_variables[1]].append((factor.random_variables[0], factor))
        self._assert_valid_tree(factors_tree)
        return factors_tree

    def _generate_single_variable_factors(self):
        single_variable_factors = {x: self._create_default_factor(x) for x in self.graphical_model.random_variables}
        for factor in self.graphical_model.factors:
            if len(factor.random_variables) == 1:
                single_variable_factors[factor.random_variables[0]] = factor
        return single_variable_factors

    def _generate_variable_messages(self):
        variable_messages = {}
        received_messages_counts = {x: 0 for x in self.graphical_model.random_variables}
        node_queue = deque(filter(lambda x: len(self.factors_tree[x]) == 1, self.graphical_model.random_variables))
        while len(node_queue) > 0:
            current_node = node_queue.popleft()
            for neighbor_node, factor in self.factors_tree[current_node]:
                if (current_node, neighbor_node) in variable_messages:
                    continue
                other_neighbors = set(map(lambda x: x[0], self.factors_tree[current_node])).difference([neighbor_node])
                if any([(x, current_node) not in variable_messages for x in other_neighbors]):
                    continue
                neighbours_messages = list(map(lambda x: variable_messages[(x, current_node)], other_neighbors))
                factor_messages = neighbours_messages + [factor, self.single_variable_factors[current_node]]
                joint_variables_message = reduce(lambda x, y: x.get_multiplied(y), factor_messages)
                marginal_message = joint_variables_message.get_sum_marginalized([current_node])
                variable_messages[(current_node, neighbor_node)] = marginal_message
                received_messages_counts[neighbor_node] += 1
                if received_messages_counts[neighbor_node] + 1 >= len(self.factors_tree[neighbor_node]):
                    node_queue.append(neighbor_node)
        return variable_messages

    def get_marginal_factor(self, marginal_variable):
        neighbours = map(lambda x: x[0], self.factors_tree[marginal_variable])
        neighbors_messages = list(map(lambda x: self.variable_messages[(x, marginal_variable)], neighbours))
        marginal_messages = neighbors_messages + [self.single_variable_factors[marginal_variable]]
        return reduce(lambda x, y: x.get_multiplied(y), marginal_messages).get_normalized()
