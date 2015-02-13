# Creates reciprocal twitter graph pkl file
# See makefile for default arguments

# usage:
#python write_snap.py [all_users] [graph_data] [output_file]
#
import sys
import re
import json
import networkx as nx
import pickle
from build_graph import *

v = nx.Graph()
u = nx.Graph()
def main():

    
    u = build_at_graph(sys.argv[1], sys.argv[2], sys.arg[3])
        
    pkl_file = open(sys.argv[3], "w")
    pickle.dump(u, pkl_file)
    pkl_file.close()


if __name__ == "__main__":
    main()
