# usage export PYTHONPATH=/usr/local/lib/python2.7/site-packages/; python -i read_entities_followed.py ../greater_roch_filtered/greater_roch_filtered_social_graph.json LGBTQ-entities.txt
import networkx as nx
import pickle
from build_graph import *
import sys
import json
import numpy

u = nx.DiGraph()
w = nx.Graph()
v = nx.DiGraph()
k = dict()
ents = []
user_nums = set()
users = dict()
filtered_users = set()
l = list()
def add_edges (u,v):
    w = u.copy()
   
        
    for x,y in v.edges():
        if (x in u) and (y in u) and (not u.has_edge(x,y)) and (x != y):
            w.add_edge(x,y)
    return w
            
def main():
    global v
    global u
    global ents
    f = open(sys.argv[1])
    ents = numpy.genfromtxt(sys.argv[2], delimiter="\t", skip_header=1, dtype=[('username', 'S32'), ('num_followers', 'i4'), ('entity_type', 'S2'), ('id', 'i8')])
    ids = set(ents['id'][0:-1])  # need to remove last entity because it currently has no id label

    v = read_json_graph_nonrecip(f)
    
    for (e,a) in v.edges_iter():
        if a in ids:
            u.add_edge(e,a)
    f.close()

    
    
    # currently the graph with 
if __name__ == "__main__":
    main()
