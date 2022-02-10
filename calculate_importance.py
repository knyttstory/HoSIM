import copy
import numpy as np
import networkx as nx

from parameter_setting import *


def diffuse_node(graph_data, dn, diffused_nodes, coefficient_nodes):
    if dn in diffused_nodes:
        return
    else:
        subgraph_nodes = sample_diffuse_nodes(graph_data, dn, coefficient_nodes)
        temp_subgraph = nx.subgraph(graph_data, subgraph_nodes)
        sorted_nodes = sorted(list(temp_subgraph.nodes))
        node_index = dict()
        for si, sn in enumerate(sorted_nodes):
            node_index[sn] = si
        seed_index = node_index[dn]
        A = nx.to_numpy_array(temp_subgraph, nodelist=sorted_nodes, dtype=np.float16)
        inverse_degree_array = [1/nx.degree(temp_subgraph, tn) for tn in sorted_nodes]
        inverse_D = np.diag(inverse_degree_array)
        transition_matrix = np.dot(inverse_D, A)
        probability_vector = np.zeros((1, len(sorted_nodes)))
        probability_vector[0, seed_index] = 1
        for i in range(pr_steps):
            probability_vector = np.dot(probability_vector, transition_matrix)
            if probability_vector[0][seed_index] > 0:
                probability_vector += probability_vector[0][seed_index] * transition_matrix[seed_index]
                probability_vector[0][seed_index] = 0
        diffused_nodes[dn] = dict()
        for si, sn in enumerate(sorted_nodes):
            diffused_nodes[dn][sn] = probability_vector[0, si]
        return

def sample_diffuse_nodes(graph_data, start_node, coefficient_nodes):
    subgraph_nodes = set()
    subgraph_nodes.add(start_node)
    seed_neighbors = set()
    seed_neighbors.add(start_node)
    for i in range(pr_hop):
        new_neighbors = set()
        for sn in seed_neighbors:
            temp_neighbors = set(pick_nodes_by_coefficient(graph_data, sn, coefficient_nodes))
            subgraph_nodes = subgraph_nodes.union(temp_neighbors)
            new_neighbors = new_neighbors.union(temp_neighbors)
        seed_neighbors = copy.deepcopy(new_neighbors)
    return subgraph_nodes

def pick_nodes_by_coefficient(graph_data, center_node, coefficient_nodes):
    if maximum_neighbor_number is not None and len(list(nx.neighbors(graph_data, center_node))) > maximum_neighbor_number:
        nodes_coefficients = list()
        for tn in nx.neighbors(graph_data, center_node):
            if tn not in coefficient_nodes:
                coefficient_nodes[tn] = nx.clustering(graph_data, tn)
            nodes_coefficients.append([tn, coefficient_nodes[tn]])
        nodes_coefficients = sorted(nodes_coefficients, key=lambda x: x[1], reverse=True)
        nodes_coefficients = nodes_coefficients[:maximum_neighbor_number]
        return [tn[0] for tn in nodes_coefficients]
    else:
        return list(nx.neighbors(graph_data, center_node))
