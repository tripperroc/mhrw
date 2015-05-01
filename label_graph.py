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

def main():
    
    global u

    graph_file = file (sys.argv[1])
    u = pickle.load(graph_file)
    graph_file.close()
        

    u = set_orientation_by_file (sys.argv[3], "orientation", u)
    if len(sys.argv) > 4:
        u = set_orientation_by_file (sys.argv[4], "test_orientation", u)

    pkl_file = open(sys.argv[2], "w")
    pickle.dump(u, pkl_file)
    pkl_file.close()


    

if __name__ == "__main__":
    main()
