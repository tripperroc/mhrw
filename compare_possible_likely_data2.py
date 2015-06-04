# usage export PYTHONPATH=/usr/local/lib/python2.7/site-packages/; python -i compare_possible_likely_data2.py ../13-2015_social_graph.json ../13-2015_master_user_list.json ../grf_13-2015_master_user_list.json
import networkx as nx
import pickle
from build_graph import *
import sys
import json
import numpy

possible_graph = nx.Graph()
likely_graph = nx.Graph()
possible_enhanced_likely_graph = nx.Graph()
possible_core_graph = nx.Graph()
likely_core_graph = nx.Graph()
possible_users = dict()
likely_users = dict()
extended_users = set()

def main():
    global possible_graph
    global likely_graph
    global possible_users
    global likely_users
    global possible_enhanced_likely_graph
    global possible_core_graph
    global likely_core_grap
    
    # f = open(sys.argv[1])
    #possible_graph = read_json_graph(f)
    #f.close()
    f = open(sys.argv[2])
    possible_users = json.load(f)
    possible_users = dict([(int(k),v) for k,v in possible_users.items()])
    f.close()
    f = open(sys.argv[3])
    likely_users = json.load(f)
    likely_users = dict([(int(k), v) for k,v in likely_users.items()])
    f.close()

   
    f = open(sys.argv[1])
    possible_core_graph = read_core_graph(f)
    possible_core_graph.graph["name"] = "possible_core_graph"
    
    likely_core_graph = nx.Graph(possible_core_graph.subgraph(likely_users.keys()))
    likely_core_graph.graph["name"] = "likely_core_graph"
    f.seek(0)
    (likely_graph, extended_users) = read_likely_possible_graph(f, likely_core_graph, possible_core_graph)
    f.close()
   
    possible_enhanced_likely_graph = nx.Graph(likely_graph)
    for node in extended_users:
       for neighbor in set(possible_graph.neighbors(node)).intersection(extended_users):
           possible_enhanced_likely_graph.add_edge(node, neighbor)

    possible_enhanced_likely_graph.graph["name"] = "possible_enhanced_likely_graph"
    
    likely_extended_and_core_only_graph = nx.Graph(possible_enhanced_likely_graph)
    likely_extended_and_core_only_graph.graph["name"] = "likely_extended_and_core_only"
    likely_extended_and_core_only_graph.remove_nodes_from([x for x in possible_enhanced_likely_graph if possible_enhanced_likely_graph.node[x]["position"] == "fringe"])
    
    graphs = [possible_core_graph, likely_core_graph, possible_enhanced_likely_graph, likely_extended_and_core_only_graph]

    prefix = sys.argv[1].split("/")[-1].split("_")[0]

    for graph in graphs:
       
        ccs = nx.connected_component_subgraphs(graph)
        l = sorted(ccs, key = lambda x: len(x), reverse=True)
        lcc = l[0]
        #print  

        f = open(prefix + "_" + graph.graph["name"] + ".pkl", "w")
        pickle.dump (lcc, f)
        f.close()

    
    
    
if __name__ == "__main__":
    main()
