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



def label_by_weighted_voting2 (u, ep, test_labeled, threshold):

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
    # Initialize priorities
    #
    unlabeled = pqdict.PQDict()
    for ego in u:
        if not "orientation" in u.node[ego]:
            u.node[ego]["total_weight"] = 0
            count = 0
            total_weight = 0
            for alter in u.neighbors(ego):
                if "orientation" in u.node[alter]:
                    count += u[ego][alter]["embeddedness"]**ep
                #total_weight += u[ego][alter]["embeddedness"]**ep
                u.node[ego]["total_weight"] += u[ego][alter]["embeddedness"]**ep
            priority = -float(count)/float(u.node[ego]["total_weight"])
            unlabeled[ego] = priority

    #################
    #
    # Create labels
    #
    logfile = file("labeling_log.txt", "w")
    while len(unlabeled) > 0:
        (ego, score) = unlabeled.popitem()
        if score == 0:
            break
        gay_alters = 0.0
        straight_alters = 0.0
        gay_list = list()
        straight_list = list()
        u.node[ego]["gay_weight"] = 0
        u.node[ego]["straight_weight"] = 0
        for alter in u.neighbors(ego):
            if "orientation" in u.node[alter]:
                if u.node[alter]["orientation"] == 1:
                    u.node[ego]["gay_weight"] += u[ego][alter]["embeddedness"]**ep
                    gay_list.append(alter)
                else:
                    u.node[ego]["straight_weight"] += u[ego][alter]["embeddedness"] **ep
                    straight_list.append(alter)
            else:
                priority = -unlabeled[alter]
                total_weight_alters = 0.0
                #for alteralter in u.neighbors(alter):
                #    total_weight_alters += u[alter][alteralter]["embeddedness"]**ep

                priority =  -(priority * float(u.node[alter]["total_weight"]) + float((u[ego][alter]["embeddedness"])**ep))/float(u.node[alter]["total_weight"])
                unlabeled[alter] = priority
        if float(u.node[ego]["gay_weight"] -u.node[ego]["straight_weight"])/float(u.node[ego]["total_weight"]) > threshold:
            u.node[ego]["orientation"] = 1
            logfile.write ("GAY\t\t");
            gay_count += 1
        else:
            u.node[ego]["orientation"] = -1
            logfile.write ("STRAIGHT\t");
            straight_count += 1
     
        if ego in test_labeled:
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
        logfile.write ("%d: degree: %d, priority: %f, gay: %s; straight %s\n" % (ego, u.degree(ego), score, str(gay_list), str(straight_list)))
        #print "%d %d %f %d %d %d %d %d %d"  % (ego, u.degree(ego) , u.node[ego]["total_weight"], gay_count, straight_count, gay_labeled_gay, gay_labeled_straight, straight_labeled_gay, straight_labeled_straight)
        #priority = -float(count)/float(len(u.neighbors(ego)))
    logfile.close()

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
    #u = label_by_weighted_voting (u, float(sys.argv[5]))
    #u = label_by_weighted_voting2 (u, float(sys.argv[5]), test_labeled)
    for x in range(-10, 11):
        threshold = float(x)/10.0
        v = u.copy()
        v = label_by_weighted_voting2 (v, float(sys.argv[5]), test_labeled, threshold)
        sys.stdout.write ("%f " % threshold)
        dump_tests (v, test_labeled)
    #u = label_by_revoting (u, float(sys.argv[5]), test_labeled)
    #dump_tests (u, test_labeled)

    u = label_by_weighted_voting2 (u, float(sys.argv[5]), test_labeled, 0)
    write_to_snap (sys.argv[4], u, node_trans, node_untrans, labeled, test_labels, float(sys.argv[5]))
    

if __name__ == "__main__":
    main()
