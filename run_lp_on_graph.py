# usage python -i run_lp_on_graph.py 13-2015likely_core_graph.pkl ../13-2015_master_user_list.json
import networkx as nx
import pickle
from build_graph import *
from nxsp import *
import sys
import json
import operator
import numpy
from sklearn import datasets
from sklearn.semi_supervised import LabelPropagation

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

label_prop_model = LabelPropagation()
g = nx.Graph()
labels = list()

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
    global label_prop_model
    global g
    global labels

    print "Loading graph"
    f = open(sys.argv[1])
    g = pickle.load(f)
    f.close()
 
    print "Loading users"
    f = open(sys.argv[2])
    users = json.load(f)
    f.close()

    print "Finding labeled users"
    users = {int(k):v for k,v in users.items()}

    labeled_users = {k: v for k,v in users.items() if "orientation" in v and k in g}
    (users, testing_users) = split(labeled_users, "orientation", {"Straight", "Gay"})
    straight_users = {k: v for k,v in users.items() if v["orientation"] == "Straight"}
    gay_users = {k: v for k,v in users.items() if v["orientation"] == "Gay"}

    m = nx.adjacency_matrix(g)
    labels = [1 if "orientation" in g.node[v] and g.node[v]["orientation"] == "Gay" else (0 if "orientation" in g.node[v] else -1) for v in g.nodes()]

    label_prop_model.fit(m, labels)
