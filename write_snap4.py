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
    logfile = file("labeling_log.txt", "w")
    while len(unlabeled) > 0:
        (ego, score) = unlabeled.popitem()
        if score == 0:
            break
        gay_alters = 0
        straight_alters = 0
        gay_list = list()
        straight_list = list()
        for alter in u.neighbors(ego):
            if "orientation" in u.node[alter]:
                if u.node[alter]["orientation"] == 1:
                    gay_alters += 1
                    gay_list.append(alter)
                else:
                    straight_alters += 1
                    straight_list.append(alter)
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
    logfile = file("labeling_log.txt", "w")
    while len(unlabeled) > 0:
        (ego, score) = unlabeled.popitem()
        if score == 0:
            break
        gay_alters = 0.0
        straight_alters = 0.0
        gay_list = list()
        straight_list = list()
        for alter in u.neighbors(ego):
            if "orientation" in u.node[alter]:
                if u.node[alter]["orientation"] == 1:
                    gay_alters += u[ego][alter]["embeddedness"]**ep
                    gay_list.append(alter)
                else:
                    straight_alters += u[ego][alter]["embeddedness"] **ep
                    straight_list.append(alter)
            else:
                priority = -unlabeled[alter]
                total_weight_alters = 0.0
                for alteralter in u.neighbors(alter):
                    total_weight_alters += u[alter][alteralter]["embeddedness"]**ep

                priority =  -(priority * float(total_weight_alters) + float((u[ego][alter]["embeddedness"])**ep))/float(total_weight_alters)
                unlabeled[alter] = priority
        if gay_alters > straight_alters:
            u.node[ego]["orientation"] = 1
            logfile.write ("GAY\t\t");
        else:
            u.node[ego]["orientation"] = -1
            logfile.write ("STRAIGHT\t");
        logfile.write ("%d: degree: %d, priority: %f, gay: %s; straight %s\n" % (ego, u.degree(ego), score, str(gay_list), str(straight_list)))
        
        #priority = -float(count)/float(len(u.neighbors(ego)))
    logfile.close()
    return u

def label_by_weighted_voting2 (u, ep, test_labeled):

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
        if u.node[ego]["gay_weight"] > u.node[ego]["straight_weight"]:
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
        print "%d %d %f %d %d %d %d %d %d"  % (ego, u.degree(ego) , u.node[ego]["total_weight"], gay_count, straight_count, gay_labeled_gay, gay_labeled_straight, straight_labeled_gay, straight_labeled_straight)
        #priority = -float(count)/float(len(u.neighbors(ego)))
    logfile.close()

    return u

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
            
        
        u.node[ego]["orientation"] = 0
    return u

# Does greedy continuous (soft) voting
def label_by_weighted_voting4 (u, ep, test_labeled):

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
        u.node[ego]["orientation"] =  (u.node[ego]["gay_weight"] - u.node[ego]["straight_weight"])/float(u.node[ego]["total_weight"])

        
        logfile.write ("%d: degree: %d, priority: %f, gay: %s; straight %s\n" % (ego, u.degree(ego), score, str(gay_list), str(straight_list)))
        print "%d %d %f %f %f %f"  % (ego, u.degree(ego), u.node[ego]["gay_weight"], u.node[ego]["straight_weight"] , u.node[ego]["total_weight"], u.node[ego]["orientation"] )
        #priority = -float(count)/float(len(u.neighbors(ego)))
    logfile.close()

    for ego in u:
        if u.node[ego]["orientation"] > 0:
            u.node[ego]["orientation"] = 1;
        else:
            u.node[ego]["orientation"] = -1;
             
    return u

def dump_tests (u, test_labeled):
        
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

    
    print "%d %d %d %d %d %d" % (gay_labeled_gay, gay_labeled_straight, gay_unlabeled, straight_labeled_gay, straight_labeled_straight, straight_unlabeled)
    

def label_by_revoting (u, ep, test_labeled):

    
    #################
    #
    # Initialize priorities
    #
    tolabel = pqdict.PQDict()
    for ego in u:
        if "total_weight" in u.node[ego]:
            tolabel[ego] = u.node[ego]["orientation"] * (u.node[ego]["gay_weight"] - u.node[ego]["straight_weight"])/u.node[ego]["total_weight"]
            #print ego
            #sys.stdout.write ("%d %d %f %f %f\n" % (ego, u.node[ego]["orientation"], u.node[ego]["gay_weight"], u.node[ego]["straight_weight"], u.node[ego]["total_weight"]))
            


    #################
    #
    # Create labels
    #
    #logfile = file("labeling_log.txt", "w")
    while True:
        (ego, score) = tolabel.popitem()
        if score >= 0:
            break
        for alter in u.neighbors(ego):
            if "total_weight" in u.node[alter]:
                u[alter]["gay_weight"] -= u.node[ego]["orientation"] * u.node[ego][alter]["embeddedness"]**ep
                u[alter]["straight_weight"] += u.node[ego]["orientation"] * u.node[ego][alter]["embeddedness"]**ep
                tolabel[alter] = u.node[alter]["orientation"] * (u.node[alter]["gay_weight"] - u.node[alter]["straight_weight"])/u.node[alter]["total_weight"];
                
        u.node[ego]["orientation"] *= -1;
        tolabel[ego] = u.node[ego]["orientation"] * (u.node[ego]["gay_weight"] - u.node[ego]["straight_weight"])/u.node[ego]["total_weight"];

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

def write_to_snap (file_name, v, node_trans, node_untrans, labeled, test_labels, ep):
    snap_graph = file (file_name, "w")

    snap_graph.write ("num_nodes %d\n" % len(v))
    snap_graph.write ("num_edges %d\n" % len(v.edges()))
    for x,y in v.edges():
        snap_graph.write ("%d %d %f\n" % (node_trans[x],node_trans[y],v[x][y]["embeddedness"]**ep))
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
    #u = label_by_weighted_voting (u, float(sys.argv[5]))
    #u = label_by_weighted_voting2 (u, float(sys.argv[5]), test_labeled)
    u = label_by_weighted_voting4 (u, float(sys.argv[5]), test_labeled)
    dump_tests (u, test_labeled)
    u = label_by_revoting (u, float(sys.argv[5]), test_labeled)
    dump_tests (u, test_labeled)
    
    write_to_snap (sys.argv[4], u, node_trans, node_untrans, labeled, test_labels, float(sys.argv[5]))
    

if __name__ == "__main__":
    main()
