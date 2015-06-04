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
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
from sklearn.metrics import classification_report, confusion_matrix

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
testing_users = dict()
training_users = dict()
labeled_users  = dict()
gay_apriori = float()
m = nx.adjacency_matrix(nx.complete_graph(1))
label_prop_model = LabelSpreading()
g = nx.Graph()
labels = list()
real_labels = list()
predicted_labels = list()
cm = confusion_matrix([],[])
def main():
    global v
    global m
    global cm
    global real_labels
    global predicted_labels
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
    global training_users
    global testing_users
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
    (training_users, testing_users) = split(labeled_users, "orientation", {"Straight", "Gay"})
    straight_users = {k: v for k,v in training_users.items() if v["orientation"] == "Straight"}
    gay_users = {k: v for k,v in training_users.items() if v["orientation"] == "Gay"}

    real_labels = [1 if v["orientation"] == "Gay" else 0 for k,v in testing_users.items()]

    i = 0
    indx = dict()
    for n in g.nodes():
        indx[n] = i
        i += 1
        

    m = nx.adjacency_matrix(g)
    labels = [1 if (v in training_users and "orientation" in training_users[v] and training_users[v]["orientation"] == "Gay") else (0 if (v in training_users and "orientation" in training_users[v]) else -1) for v in g.nodes()]

    label_prop_model.fit(m, labels)

    predicted_labels = [label_prop_model.transduction_[indx[x]] for x in testing_users]

    cm = confusion_matrix(real_labels, predicted_labels,labels=label_prop_model.classes_)

    print cm
    
if __name__ == "__main__":
    main()
