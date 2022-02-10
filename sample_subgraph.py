import copy
import networkx as nx

from calculate_importance import *
import ppr_cd


def sample_subgraph(graph_data, query_node, diffused_nodes, coefficient_nodes):
    sampled_nodes = diffusion_nodes(graph_data, query_node)
    if lorw_flag is True:
        sampled_nodes = lorw_nodes(graph_data, sampled_nodes, diffused_nodes, coefficient_nodes)
    core_nodes = copy.deepcopy(sampled_nodes)
    if add_boundary_number is not None and len(core_nodes) <= maximum_sample_subgraph_size:
        for i in range(add_boundary_number):
            sampled_nodes = sampled_nodes.union(get_neighbors(graph_data, sampled_nodes, coefficient_nodes, maximum_sample_subgraph_size - len(sampled_nodes)))
    return sampled_nodes, core_nodes

def diffusion_nodes(graph_data, query_node):
    temp_radius = 2
    while True:
        temp_subgraph = nx.ego_graph(graph_data, query_node, radius=temp_radius)
        if len(temp_subgraph.nodes) < diffusion_size:
            temp_radius += 1
        else:
            break
    if len(temp_subgraph.nodes) > diffusion_size:
        nodes_probabilities = ppr_cd.ppr_cd(temp_subgraph, [query_node, ], query_node, None, True)
        node_list = [np[0] for np in nodes_probabilities[:min(len(nodes_probabilities), int(diffusion_size))]]
        community_subgraph = nx.subgraph(graph_data, node_list)
        if nx.is_connected(community_subgraph) is False:
            components = nx.connected_components(community_subgraph)
            for nodes in components:
                if query_node in set(nodes):
                    temp_nodes = set(nodes)
                    break
        else:
            temp_nodes = set(node_list)
    else:
        temp_nodes = set(temp_subgraph.nodes)
    return temp_nodes

def lorw_nodes(graph_data, sample_nodes, diffused_nodes, coefficient_nodes):
    add_number = 0
    while add_number < lorw_size:
        temp_neighbors = get_neighbors(graph_data, sample_nodes, coefficient_nodes, lorw_size)
        temp_add_nodes = list()
        for tn in temp_neighbors:
            sum_inside = 0
            diffuse_node(graph_data, tn, diffused_nodes, coefficient_nodes)
            for dn in diffused_nodes[tn]:
                if dn in sample_nodes:
                    sum_inside += diffused_nodes[tn][dn]
            temp_add_nodes.append((tn, sum_inside))
        temp_add_nodes = sorted(temp_add_nodes, key=lambda x: x[1], reverse=True)
        add_nodes_list = [an[0] for an in temp_add_nodes[:min(len(temp_add_nodes), int(lorw_size / iters_number))]]
        sample_nodes = sample_nodes.union(set(add_nodes_list))
        add_number += len(add_nodes_list)
    return sample_nodes

def get_neighbors(graph_data, sampled_nodes, coefficient_nodes, maximum_size):
    neighbors_nodes = set()
    for tsn in sampled_nodes:
        for tn in nx.neighbors(graph_data, tsn):
            if tn not in sampled_nodes:
                neighbors_nodes.add(tn)
    if maximum_size is not None and len(neighbors_nodes) > maximum_size:
        temp_coefficient = list()
        for tn in neighbors_nodes:
            if tn not in coefficient_nodes:
                coefficient_nodes[tn] = nx.clustering(graph_data, tn)
            temp_coefficient.append([tn, coefficient_nodes[tn]])
        temp_coefficient = sorted(temp_coefficient, key=lambda x: x[1], reverse=True)
        neighbors_nodes = set([tc[0] for tc in temp_coefficient[:maximum_size]])
    return neighbors_nodes
