# usage export PYTHONPATH=/usr/local/lib/python2.7/site-packages/; python -i read_entities_followed.py ../13-2015_social_graph.json LGBTQ-entities.txt ../13-2015_master_user_list.json
import networkx as nx
import pickle
from build_graph import *
from nxsp import *
import sys
import json
import operator
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
gay_plus_vince = set()
straight_plus_vince = set()
gay_graph_vince = nx.Graph()
straight_graph_vince = nx.Graph()
naive_gay = dict()
naive_straight = dict()
conf = dict()
gay_users = dict()
straight_users = dict()
pr_gay = dict()
entity_apriori = dict()
entities = set ()
entity_given_gay = dict()
neighbors = set()
users = dict()
labeled_users  = dict()
gay_apriori = float()

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
    global ids
    global gay_plus_vince
    global straight_plus_vince
    global gay_graph_vince
    global straight_graph_vince

    global naive_gay
    global naive_straight
    global gay_users
    global straight_users
    global conf
    global entity_apriori
    global entities
    global entity_given_gay
    global neighbors 
    global pr_gay
    global users
    global labeled_users
    global gay_apriori
    
    ents = numpy.genfromtxt(sys.argv[2], delimiter="\t", skip_header=1, dtype=[('username', 'S32'), ('num_followers', 'i4'), ('entity_type', 'S2'), ('id', 'i8')])
    ids = set(ents['id'][0:-1])  # need to remove last entity because it currently has no id label

    print "Loading users"
    f = open(sys.argv[3])
    users = json.load(f)
    f.close()



    print "Finding labeled users"
    users = {int(k):v for k,v in users.items()}

    labeled_users = {k: v for k,v in users.items() if "orientation" in v}
    (users, testing_users) = split(labeled_users, "orientation", {"Straight", "Gay"})
    straight_users = {k: v for k,v in users.items() if v["orientation"] == "Straight"}
    gay_users = {k: v for k,v in users.items() if v["orientation"] == "Gay"}

    gay_apriori = len(gay_users)/float(len(straight_users) + len(gay_users))
    
    print "Reading graph"
    f = open(sys.argv[1])
    v = read_json_graph_nonrecip_restricted_to(f, users.keys())
    f.close()

    print "Reading vince graph"
    u = nx.DiGraph(v)
    u.remove_nodes_from ([k for k,w in v.node.items() if (not k in users) and (w["role"] != "entity")])
    u.remove_edges_from([(x,y) for (x,y) in v.edges() if v.node[x]["role"] == v.node[y]["role"]])
    

    print "Finding useful features"

    gay_plus_vince = set(gay_users.keys()).union(ids)
    #straight_plus_vince = set(straight_users.keys()).union(ids)
    gay_graph_vince = u.subgraph([k for k,w in u.node.items() if (w["role"] == "entity") or (k in gay_users)])
    #straight_graph_vince = u.subgraph([k for k,w in u.node.items() if (w["role"] == "entity") or (k in straight_users)])
    entities = [x for x,y in u.node.items() if y["role"] == "entity" and gay_graph_vince.degree([x])[x] > 0 ]
    entity_count = float(sum([u.degree([x])[x] for x in entities]))
    entity_given_gay = {x: ((gay_graph_vince.degree([x])[x]) / float(len(gay_users))) for x in entities}

    entity_apriori = {x : (u.degree([x])[x])/float(entity_count) for x in entities}
    
                       
    #naive_straight = {x : (straight_graph_vince.degree([x])[x] / float(len(straight_users))) for x,y in straight_graph_vince.node.items()  if y["role"] == "entity"}

    #gay_graph_vince = v.subgraph([k for k,w in u.node.items() if (k in ids) or (k in gay_users)])
    #straight_graph_vince = v.subgraph([k for k,w in u.node.items() if (k in ids) or (k in straight_users)])

    #ids = list(ids)
    #naive_gay = {x: (gay_graph_vince.degree([x])[x] / float(len(gay_users))) for x,y in gay_graph_vince.node.items() if x in ids}
    #naive_straight = {x : (straight_graph_vince.degree([x])[x] / float(len(straight_users))) for x,y in straight_graph_vince.node.items()  if x in ids}

    #conf = {x: (naive_gay[x] - naive_straight[x]) for x in set(naive_gay.keys()).union(set(naive_straight.keys()))}
    #(set(gay_graph_vince.nodes()).union(set(straight_graph_vince.nodes()))) - (set(gay_users.keys()).union(set(straight_users.keys())))}
    #conf = sorted(conf.items(), key=operator.itemgetter(1))

    #test a naive classifier on the training set to see how well it fits the observations
    for k in set(users.keys()).intersection(u.nodes()):
        neighbors = set(u.neighbors(k)) 
        e_given_g = reduce (lambda x, y : x*y, map(lambda z: entity_given_gay[z] if z in neighbors else 1 - entity_given_gay[z], entities))
        e_apriori = reduce (lambda x, y : x*y, map(lambda z: entity_apriori[z] if z in neighbors else 1 - entity_apriori[z], entities))
        pr_gay[k] = 0 if e_apriori == 0 else (e_given_g  * gay_apriori / e_apriori)
    # currently the graph with

    
if __name__ == "__main__":
    main()
