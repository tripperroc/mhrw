# usage export PYTHONPATH=/usr/local/lib/python2.7/site-packages/; python read_reciprocal_graph.py ../greater_roch_filtered/greater_roch_filtered_social_graph.json ../rochester/18-2015_master_user_list.json ../rochester/17-2015_social_graph.json filtered_users.json
import networkx as nx
import pickle
from build_graph import *
import sys
import json

u = nx.Graph()
w = nx.Graph()
v = nx.Graph()
k = dict()
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

    global u
    global v
    global k
    global w
    global l
    global user_nums
    global users
    global filtered_users
    f = open(sys.argv[1])
    u = read_json_graph(f)
    f.close()

    ccs = nx.connected_components(u)
    l = sorted(ccs, key = lambda x: len(x), reverse=True)
   
    #v = u.subgraph([x for x in u if u.degree(x) > 1])
    #ccs = nx.connected_components(v)
    #m = sorted(ccs, key = lambda x: len(x), reverse=True)

    #largest_2deg_cc = m[0]
    f = open(sys.argv[2])
    users = json.load(f)
    f.close()
    #user_nums = set([int(x) for x in users.keys()])
    
    f = open(sys.argv[3])
    w = read_core_graph(f)
    f.close()

    print "Adding edges"
    v = add_edges(u,w)

    print "filtering users"
    filtered_users = set(v.nodes()).intersection(set([int(x) for x in users.keys()]))
    filtered_users = [str(x) for x in list(filtered_users)]
    output_users = dict()
    for usy in filtered_users:
        output_users[usy] = users[usy]

    f = open(sys.argv[4],'w')
    json.dump(output_users, f)
    f.close()

    print "computing core numbers"
    k = nx.core_number(v)
    l = [e for (e,y) in k.items() if y > 1]

    # currently the graph with 
if __name__ == "__main__":
    main()
