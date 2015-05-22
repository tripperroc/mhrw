# usage export PYTHONPATH=/usr/local/lib/python2.7/site-packages/; python -i read_entities_followed.py ../13-2015_social_graph.json LGBTQ-entities.txt ../13-2015_master_user_list.json
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

    print "Reading graph"
    v = read_json_graph_nonrecip(f)

    print "Reading vince graph"
    for (e,a) in v.edges_iter():
        if a in ids:
            u.add_edge(e,a)
    f.close()

    print "Loading users"
    f.open(sys.argv[3])
    users = json.load(f)
    f.close()

    print "Finding labeled users"
    users = {int(k) for k,v in users.items()}
    labeled_users = {k: v for k,v in users.items() if "orientation" in v}
    straight_users = {k: v for k,v in labeled_users.items() if v["orientation"] == "Heterosexual"}
    gay_users = {k: v for k,v in labeled_users.items() if v["orientation"] == "Gay"}


    print "Finding useful features"
    
    gay_plus_vince = set(gay_users.keys()).union(ids)
    straight_plus_vince = set(gay_users.keys()).union(ids)
    gay_graph_vince = u.subgraph(gay_plus_vince)
    straight_graph_vince = u.subgraph(straight_plus_vince)

    ids = list(ids)
    naive_gay = {x: (gay_graph_vince.degree(x) / float(len(gay_users))) for x in ids}
    naive_straight = {x : (straight_graph_vince.degree(x) / float(len(straight_users))) for x in ids}

    conf = {x: (naive_gay[x] - naive_straight) for x in ids}
    conf = sorted(conf.items(), key=operator.itemgetter(1))
    

    

  
    # currently the graph with 
if __name__ == "__main__":
    main()
