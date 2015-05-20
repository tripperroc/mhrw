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
extended_users = set()

def main():
    global possible_graph
    global likely_graph
    global possible_users
    global likely_users
    
    # f = open(sys.argv[1])
    #possible_graph = read_json_graph(f)
    #f.close()
    f = open(sys.argv[2])
    possible_users = json.load(f)
    f.close()
    f = open(sys.argv[3])
    likely_users = json.load(f)
    f.close()

   
    f = open(sys.argv[1])
    possible_graph = read_core_graph(f)
    f.seek(0)
    (likely_graph, extended_users) = read_likely_possible_graph(f, likely_users.keys(), possible_users.keys())
    f.close()
   

    for node in extended_users:
       for neighbor in set(possible_graph.neighbors(node)).intersection(extended_users):
           likely_graph.add_edge(node, neighbor)
           
    
if __name__ == "__main__":
    main()
