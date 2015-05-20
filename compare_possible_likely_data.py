# usage export PYTHONPATH=/usr/local/lib/python2.7/site-packages/; python -i read_entities_followed.py ../greater_roch_filtered/greater_roch_filtered_social_graph.json LGBTQ-entities.txt
import networkx as nx
import pickle
from build_graph import *
import sys
import json
import numpy

possible_graph = nx.Graph()
likely_graph = nx.Graph()
possible_users = dict()
likely_users = dict()


def main():
    global possible_graph
    global likely_graph
    global possible_users
    global likely_users
    
    # f = open(sys.argv[1])

    #possible_graph = read_json_graph(f)
    #f.close()
    f = open(sys.argv[1])
    possible_graph = read_json_graph(f)
    f.close()
    f = open(sys.argv[2])
    possible_users = json.load(f)
    f.close()
    f = open(sys.argv[3])
    likely_users = json.load(f)
    f.close()

    likely_graph = nx.Graph(G.subgraph(likely_users.keys()))
    lgn = set(likely_graph.nodes())
    for x in likely_graph:
        for y in set(possible_graph.neighbors(x)).difference(lgn):
            likely_graph.add_edges(x,y)
            if possible_graph.node[y]["position"] == "core":
                likely_graph.node[y]["position"] = "possible_core"
            else:
                likely_graph.node[y]["position"] = "fringe"

if __name__ == "__main__":
    main()
