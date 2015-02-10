
# Generates max clique bipartite graph from a graph.
# See makefile for default arguments

# usage:
# python generate_max_clique_graph.py [source_graph] [dest_graph]

import sys
import re
import math
import json
import networkx as nx
import pickle
from build_graph import *


###################
#
# Global variables
#
di = nx.DiGraph()
u = nx.Graph()
v = nx.Graph()
node_trans = dict()
gay_set = set()
straight_set = set()
gay_cliques = set()
straight_cliques = set ()
B = nx.Graph()

def main():

    missing = file ("missing.txt", "w")
    
    global di
    global u
    global v
    global gay_set
    global straight_set
    global gay_cliques
    global straight_cliques
    global B

    graph_file = file (sys.argv[1])
    u = pickle.load(graph_file)
    graph_file.close()
        

    for ego in u:
        if "orientation" in u.node[ego]:
            if u.node[ego]["orientation"] == 1:
                gay_set.add(ego)
            else:
                straight_set.add(ego)
              


    B = nx.make_clique_bipartite(u)

    for node in gay_set:
        gay_cliques = gay_cliques | set (B.neighbors(node))
    for node in straight_set:
        straight_cliques = straight_cliques | set (B.neighbors(node))

    print "Gay max cliques: %d" % len(gay_cliques)
    print "Straight max cliques: %d" % len(straight_cliques)
    print "Intersection: %d" % len(straight_cliques & gay_cliques)
   
    for ego in u:
        if "orientations" in u.node[ego]:
            B.node[ego]["orientation"] = u.node[ego]["orientation"]

    for (ego, alter) in B.edges():
        B[ego][alter]["embeddedness"] = 1.0;
        
    bipartite_output_file = file (sys.argv[2], "w")
    pickle.dump(B, bipartite_output_file)
    bipartite_output_file.close()
    
if __name__ == "__main__":
    main()
