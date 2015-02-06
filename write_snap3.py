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

def label_by_voting (u):

    #################
    #
    # Initialize priorities
    #
    unlabeled = pqdict.PQDict()
    for ego in u:
        if not "orientation" in u.node[ego]:
            count = 0
            for alter in u.neighbors(ego):
                if "orientation" in u.node[alter]:
                    count += 1
            priority = -float(count)/float(len(u.neighbors(ego)))
            unlabeled[ego] = priority

    #################
    #
    # Create labels
    #
    while len(unlabeled) > 0:
        (ego, score) = unlabeled.popitem()
        if score == 0:
            break
        gay_alters = 0
        straight_alters = 0
        for alter in u.neighbors(ego):
            if "orientation" in u.node[alter]:
                if u.node[alter]["orientation"] == 1:
                    gay_alters += 1
                else:
                    straight_alters += 1
            else:
                priority = -unlabeled[alter]
                fneighbs = float(len(u.neighbors(alter)))
                priority =  -(priority * fneighbs + 1)/fneighbs
                unlabeled[alter] = priority
        if gay_alters > straight_alters:
            u.node[ego]["orientation"] = 1
        else:
            u.node[ego]["orientation"] = -1
        #priority = -float(count)/float(len(u.neighbors(ego)))

    return u

def label_by_weighted_voting (u, ep):

    #################
    #
    # Initialize priorities
    #
    unlabeled = pqdict.PQDict()
    for ego in u:
        if not "orientation" in u.node[ego]:
            count = 0
            total_weight = 0
            for alter in u.neighbors(ego):
                if "orientation" in u.node[alter]:
                    count += u[ego][alter]["embeddedness"]**ep
                total_weight += u[ego][alter]["embeddedness"]**ep
            priority = -float(count)/float(total_weight)
            unlabeled[ego] = priority

    #################
    #
    # Create labels
    #
    while len(unlabeled) > 0:
        (ego, score) = unlabeled.popitem()
        if score == 0:
            break
        gay_alters = 0.0
        straight_alters = 0.0
        for alter in u.neighbors(ego):
            if "orientation" in u.node[alter]:
                if u.node[alter]["orientation"] == 1:
                    gay_alters += u[ego][alter]["embeddedness"]**ep
                else:
                    straight_alters += u[ego][alter]["embeddedness"] **ep
            else:
                priority = -unlabeled[alter]
                total_weight_alters = 0.0
                for alteralter in u.neighbors(alter):
                    total_weight_alters += u[alter][alteralter]["embeddedness"]**ep

                priority =  -(priority * float(total_weight_alters) + float((u[ego][alter]["embeddedness"])**ep))/float(total_weight_alters)
                unlabeled[alter] = priority
        if gay_alters > straight_alters:
            u.node[ego]["orientation"] = 1
        else:
            u.node[ego]["orientation"] = -1
        #priority = -float(count)/float(len(u.neighbors(ego)))

    return u

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
            else:
                u.node[ego][field_name] = 1

    test_data.close()
    return u

def write_to_snap (file_name, v, node_trans, node_untrans, labeled, test_labels):
    snap_graph = file (file_name, "w")

    snap_graph.write ("num_nodes %d\n" % len(v))
    snap_graph.write ("num_edges %d\n" % len(v.edges()))
    for x,y in v.edges():
        snap_graph.write ("%d %d %f\n" % (node_trans[x],node_trans[y],v[x][y]["embeddedness"]))
    snap_graph.write ("num_labeled %d\n" % len(labeled))
    #for label in labeled:
    #    snap_graph.write ("%d\n" % label)
    for i in range(0, len(v)):
        snap_graph.write ("%d\n" % v.node[node_untrans[i]]["orientation"])
    snap_graph.write ("num_test_labeled %d\n" % len(test_labels))
    for label in test_labels:
        snap_graph.write ("%d\n" % label)

###################
#
# Global variables
#
di = nx.DiGraph()
u = nx.Graph()
v = nx.Graph()
node_trans = dict()
gays = set()
straights = set()
gay_cliques = set()
straight_cliques = set ()
B = nx.Graph()

def main():

    missing = file ("missing.txt", "w")
    
    global di
    global u
    global v
    global gays
    global straights
    global gay_cliques
    global straight_cliques
    global B

    graph_file = file (sys.argv[3])
    u = pickle.load(graph_file)
    graph_file.close()
        

    u = set_orientation_by_file (sys.argv[1], "orientation", u)
    u = set_orientation_by_file (sys.argv[2], "test_orientation", u)

    '''
    B = nx.make_clique_bipartite(u)

    for node in gays:
        gay_cliques = gay_cliques | set (B.neighbors(node))
    for node in straights:
        straight_cliques = straight_cliques | set (B.neighbors(node))
    '''

    ##################################
    #
    # Invent new node labels that snap will understand
    # i.e., from 0 to n-1
    # put the labeled training nodes first, followed by test nodes,
    # followed by the rest
    #
    # Not that u is not actually relabeled. The labels are applied
    # when the output file is written.
    #
    count = 0
    not_labeled = list()
    labeled = list()
    test_labeled = list()
    test_labels = list()
    labeled_data_for_snap = file("snap_labels.txt", "w")
    node_untrans = dict()
    
    for ego in u:
        if "orientation" in u.node[ego]:
            node_trans[ego] = count
            node_untrans[count] = ego
            labeled_data_for_snap.write("%d\n" % u.node[ego]["orientation"])
            labeled.append(u.node[ego]["orientation"])
            count += 1
        elif "test_orientation" in u.node[ego]:
            test_labeled.append(ego)
            test_labels.append(u.node[ego]["test_orientation"])
        else:
            not_labeled.append(ego)
    labeled_data_for_snap.close()
    
    for ego in test_labeled:
        node_trans[ego] = count
        node_untrans[count] = ego
        count +=1
    for ego in not_labeled:
        node_trans[ego] = count
        node_untrans[count] = ego
        count +=1
        

    ######################
    #
    # Output graph with labels and node translations
    # These are intermediate outputs that may later be
    # helpful in interpreting the data
    #
    pkl_file = open(sys.argv[6], "w")
    pickle.dump(u, pkl_file)
    pkl_file.close()

    pkl_file = open(sys.argv[7], "w")
    pickle.dump(node_trans, pkl_file)
    pkl_file.close()

    #u = label_by_voting (u)
    u = label_by_weighted_voting (u, float(sys.argv[5]))
    ########################
    #
    # Evaluate labels on test data
    #
    gay_labeled_gay = 0
    gay_labeled_straight = 0
    gay_unlabeled = 0
    straight_labeled_straight = 0
    straight_labeled_gay = 0
    straight_unlabeled = 0
    
    for ego in test_labeled:
        if "orientation" in u.node[ego]:
            if u.node[ego]["orientation"] == 1:
                if u.node[ego]["test_orientation"] == 1:
                    gay_labeled_gay += 1
                else:
                    straight_labeled_gay += 1
            else:
                if u.node[ego]["test_orientation"] == 1:
                    gay_labeled_straight += 1
                else:
                    straight_labeled_straight += 1
        else:
            if u.node[ego]["test_orientation"] == 1:
                gay_unlabeled += 1
            else:
                straight_unlabeled += 1
    print "gay_labeled_gay: %d" % gay_labeled_gay
    print "gay_labeled_straight: %d" % gay_labeled_straight
    print "gay_unlabeled: %d" % gay_unlabeled
    print "straight_labeled_gay: %d" % straight_labeled_gay
    print "straight_labeled_straight: %d" % straight_labeled_straight
    print "straight_unlabeled: %d" % straight_unlabeled


    
    write_to_snap (sys.argv[4], u, node_trans, node_untrans, labeled, test_labels)
    

if __name__ == "__main__":
    main()
