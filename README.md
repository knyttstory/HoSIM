Multiple Local Community Detection based on Higher-order Structural Importance (HoSIM)
===============================================

About
-----

A powerful method for multiple local community detection based on higher-order structural importance, named HoSIM. HoSIM utilizes two new metrics to evaluate the HoSI score of a subgraph to a node and the HoSI score of a node, where the first metric is used to judge whether the node belongs to the community structure, and the second metric estimates whether there exist dense structures around the node. Then, HoSIM enforces a three-stage processing, namely subgraph sampling, core member identification, and local community detection. The key idea is utilizing HoSI to find and identify the core members of communities relevant to the query node and optimize the generated communities.


The descriptions of python files
----------------------------

* calculate_importance.py: calculate the higher-order structural importance
* data_setting.py: dataset setting
* detect_community.py: detect local communities
* evaluate_community.py: evaluate detected communities on F1-score
* hosim_run.py: run HoSIM
* parameter_setting.py: parameter setting
* ppr_cd.py: PRN algorithm
* preprocess_data.py: remove copies from original communities and select seeds
* sample_subgraph.py: sample subgraph


How to use your own datasets
----------------------------

You can create a new folder and copy the graph data as well as the community data into the folder. Note that, you should also change the corresponding variables in "data_setting.py". 

The detection results are generated in the folder of "Results". You can open an excel file to check the F1-socres.
