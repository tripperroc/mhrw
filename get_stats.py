# Prepares data for input to snap-base mhrw system 
# See makefile for default arguments

# usage:
#python write_snap.py [labeled_users] [all_users] [test_users] [graph_data] [snap_output]
#
import sys
import re
import math
import json
import networkx as nx
import pickle
import pqdict
from build_graph import *



def set_orientation_by_file (filename, field_name, u):
    test_data = file(filename)

    while True:
        line = test_data.readline()
        if line == "":
            break
        orientation, description, key, profile_image_url, profile_banner_url, profile_background_image_url = line.split("\t")
        ego = int(key)
        if ego in u:
            if orientation == "Straight":
                u.node[ego][field_name] = -1
            if orientation == "Gay":
                u.node[ego][field_name] = 1

    test_data.close()
    return u


###################
#
# Global variables
#
u = nx.Graph()
v = nx.Graph()
gay_friends = list()
straight_friends = list()

def main():
    
    global u
    global v
    global gay_friends
    global straight_friends

    graph_file = file (sys.argv[1])
    u = pickle.load(graph_file)
    graph_file.close()

    v = u.subgraph([i for i in u.node if "orientation" in u.node[i]])

    gay_friends = [e for e in v.edges() if v.node[e[0]]["orientation"] == 1 and v.node[e[1]]["orientation"] == 1]
    straight_friends = [e for e in v.edges() if v.node[e[0]]["orientation"] == -1 and v.node[e[1]]["orientation"] == -1]
    pkl_file = open(sys.argv[2], "w")

    c = list(nx.find_cliques(v))
    d = [cl in c if len(cl) > 2]
    e = [[v.node[i]['orientation'] for i in de] for de in d]
    
    pickle.dump(u, pkl_file)
    pkl_file.close()

 
    


    

if __name__ == "__main__":
    main()
