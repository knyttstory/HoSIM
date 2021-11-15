import os
import time
import tqdm
import pickle
import networkx as nx

import preprocess_data
from data_setting import *
from parameter_setting import *
from sample_subgraph import *
from detect_community import *
import evaluate_community


def read_graph_data():
    with open(os.path.join(dataset_path, dataset_name, dataset_graph), 'rb') as gf:
        graph_data = pickle.load(gf)
    return graph_data

def read_diffusion_information():
    diffusion_path = dataset_name + '_diffusion_r%d_p%d_n%d_a%.2f.pkl' % (pr_hop, pr_steps, maximum_neighbor_number, alpha)
    os.makedirs(os.path.join(output_path, dataset_name), exist_ok=True)
    if os.path.exists(os.path.join(output_path, dataset_name, diffusion_path)):
        with open(os.path.join(output_path, dataset_name, diffusion_path), 'rb') as df:
            diffused_nodes, coefficient_nodes = pickle.load(df)
    else:
        diffused_nodes = dict()
        coefficient_nodes = dict()
    return diffused_nodes, coefficient_nodes, diffusion_path

def sample_all_subgraphs(graph_data, diffused_nodes, coefficient_nodes):
    sample_path = "ds%d_lf%s_ls%d_in%d_af%s" % (diffusion_size, "T" if lorw_flag else "F", lorw_size, iters_number, "T" if add_boundary_flag else "F")
    os.makedirs(os.path.join(output_path, dataset_name, sample_path), exist_ok=True)
    if os.path.exists(os.path.join(output_path, dataset_name, sample_path, output_sampled_graph)):
        with open(os.path.join(output_path, dataset_name, sample_path, output_sampled_graph), 'rb') as sf:
            sampled_all_subgraphs, sampled_all_cores = pickle.load(sf)
    else:
        sampled_all_subgraphs = dict()
        sampled_all_cores = dict()
        print("Start to sample nodes")
        for i in range(len(dataset_seeds)):
            with open(os.path.join(dataset_path, dataset_name, dataset_seeds[i]), 'rb') as sf:
                query_nodes = pickle.load(sf)
            for qn in tqdm.tqdm(query_nodes):
                sampled_all_subgraphs[qn], sampled_all_cores[qn] = sample_subgraph(graph_data, qn, diffused_nodes, coefficient_nodes)
        with open(os.path.join(output_path, dataset_name, sample_path, output_sampled_graph), 'wb') as sf:
            pickle.dump((sampled_all_subgraphs, sampled_all_cores), sf)
    return sampled_all_subgraphs, sampled_all_cores, sample_path


def main():
    graph_data = read_graph_data()
    diffused_nodes, coefficient_nodes, diffusion_path = read_diffusion_information()
    sampled_all_subgraphs, sampled_all_cores, sample_path = sample_all_subgraphs(graph_data, diffused_nodes, coefficient_nodes)
    detect_path = "sf%s_cn%d_at%.1f_rf%s_rt%.1f" % ("T" if speedup_flag else "F", components_number, add_threshold, "T" if remove_flag else "F", remove_threshold)
    os.makedirs(os.path.join(output_path, dataset_name, sample_path, detect_path), exist_ok=True)
    print("Start to detect communities")
    for i in range(len(dataset_seeds)):
        with open(os.path.join(dataset_path, dataset_name, dataset_seeds[i]), 'rb') as sf:
            query_nodes = pickle.load(sf)
        detected_communities = dict()
        for qn in tqdm.tqdm(query_nodes):
            subgraph_data = nx.subgraph(graph_data, sampled_all_subgraphs[qn])
            detected_communities[qn] = detect_multiple_communities(graph_data, subgraph_data, sampled_all_cores[qn], qn, diffused_nodes, coefficient_nodes)
        with open(os.path.join(output_path, dataset_name, sample_path, detect_path, output_detected_community[i]), 'wb') as df:
            pickle.dump(detected_communities, df)
    with open(os.path.join(output_path, dataset_name, diffusion_path), 'wb') as df:
        pickle.dump((diffused_nodes, coefficient_nodes), df)
    return sample_path, detect_path

if __name__ == '__main__':
    print(dataset_name)
    preprocess_data.main(dataset_name)
    start_time = time.time()
    sample_path, detect_path = main()
    print(round(time.time() - start_time, 2) / 500)
    evaluate_community.main_run(sample_path, detect_path)
