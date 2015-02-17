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
from snap_write import *



def label_by_weighted_voting3 (u, ep, test_labeled):

    gay_labeled_gay = 0
    gay_labeled_straight = 0
    gay_unlabeled = 0
    straight_labeled_straight = 0
    straight_labeled_gay = 0
    straight_unlabeled = 0
    straight_count = 0
    gay_count = 0
    
    #################
    #
    # Create labels
    #
    for ego in u:
        if not "orientation" in u.node[ego]:
            u.node[ego]["orientation"] = 0
            continue
            u.node[ego]["total_weight"] = 0
            count = 0
            u.node[ego]["gay_weight"] = 0
            u.node[ego]["straight_weight"] = 0
            gay_list = list()
            straight_list = list()
            total_weight = 0
            for alter in u.neighbors(ego):
                if "orientation" in u.node[alter]:
                    if u.node[alter]["orientation"] == 1:
                        u.node[ego]["gay_weight"] += u[ego][alter]["embeddedness"]**ep
                        gay_list.append(alter)
                    elif u.node[alter]["orientation"] == -1:
                        u.node[ego]["straight_weight"] += u[ego][alter]["embeddedness"] **ep
                        straight_list.append(alter)
                #total_weight += u[ego][alter]["embeddedness"]**ep
                u.node[ego]["total_weight"] += u[ego][alter]["embeddedness"]**ep
            u.node[ego]["orientation"] = 0
    return u


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

    global labeled
    
    graph_file = file (sys.argv[3])
    u = pickle.load(graph_file)
    graph_file.close()

    # try w/ clique graph
    u = nx.make_clique_bipartite(u)
    for i,j in u.edges():
        u[i][j]["embeddedness"] = 1
    u = set_orientation_by_file (sys.argv[1], "orientation", u)
    u = set_orientation_by_file (sys.argv[2], "test_orientation", u)

    all = u.subgraph([x for x in u.node if "orientation" in u.node[x]])
    gay_graph = u.subgraph([y for y in [x for x in u.node if "orientation" in u.node[x]] if u.node[y]['orientation'] == 1])
    straight_graph = u.subgraph([y for y in [x for x in u.node if "orientation" in u.node[x]] if u.node[y]['orientation'] == -1])
    


    '''
    B = nx.make_clique_bipartite(u)
    '''
    for node in gay_graph:
        gay_cliques = gay_cliques | set (u.neighbors(node))
    for node in straight_graph:
        straight_cliques = straight_cliques | set (u.neighbors(node))
    
    #for node in straight_cliques & gay_cliques:
    #    print "Share clique: %s" % node
    #    print "Neighbors: %s " % u.neighbors(node)
    #    u.remove_node(node)
        
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

    #labeled = u.copy()
    
    pkl_file = open(sys.argv[7], "w")
    pickle.dump(node_trans, pkl_file)
    pkl_file.close()

    #u = label_by_voting (u)
    #u = label_by_weighted_voting (u, float(sys.argv[5]))
    #u = label_by_weighted_voting2 (u, float(sys.argv[5]), test_labeled)
    u = label_by_weighted_voting3 (u, float(sys.argv[5]), test_labeled)
    #dump_tests (u, test_labeled)
    #u = label_by_revoting (u, float(sys.argv[5]), test_labeled)
    #dump_tests (u, test_labeled)
    
    write_to_snap (sys.argv[4], u, node_trans, node_untrans, labeled, test_labels, float(sys.argv[5]))
    

if __name__ == "__main__":
    main()
