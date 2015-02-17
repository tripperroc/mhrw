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


def dump_tests (u, test_labeled):
        
    gay_labeled_gay = 0
    gay_labeled_straight = 0
    gay_unlabeled = 0
    straight_labeled_straight = 0
    straight_labeled_gay = 0
    straight_unlabeled = 0

    
    for ego in test_labeled:
        if "orientation" in u.node[ego] and  u.node[ego]["test_orientation"] !=0:
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

    accuracy = float(gay_labeled_gay + straight_labeled_straight) / float(gay_labeled_gay + straight_labeled_gay + gay_labeled_straight + straight_labeled_straight)
    if gay_labeled_gay + straight_labeled_gay == 0:
        precision = 0.0
    else:
        precision = float(gay_labeled_gay) / float (gay_labeled_gay + straight_labeled_gay)
    if gay_labeled_gay + gay_labeled_straight == 0:
        recall = 0.0
    else:
        recall = float(gay_labeled_gay)/ float(gay_labeled_gay + gay_labeled_straight)
    if straight_labeled_gay + straight_labeled_straight == 0:
        false_positive = 0.0
    else:
        false_positive = float(straight_labeled_gay)/float(straight_labeled_gay + straight_labeled_straight)
    if gay_labeled_gay + gay_labeled_straight == 0:
        true_positive = 0.0
    else:
        true_positive = float(gay_labeled_gay)/float(gay_labeled_gay + gay_labeled_straight)
    if precision + recall == 0:
        f = 0
    else:
        f = 2.0 * precision * recall / (precision + recall)
    print "%d %d %d %d %d %d %f %f %f %f %f %f" % (gay_labeled_gay, gay_labeled_straight, gay_unlabeled, straight_labeled_gay, straight_labeled_straight, straight_unlabeled, accuracy, f, precision, recall, true_positive, false_positive)
    

def label_by_revoting (u, ep, test_labeled):

    
    #################
    #
    # Initialize priorities
    #
    tolabel = pqdict.PQDict()
    for ego in u:
        if "total_weight" in u.node[ego]:
            if u.node[ego]["orientation"] == 0:
                if u.node[ego]["gay_weight"] > u.node[ego]["straight_weight"]:
                    u.node[ego]["orientation"] = -1
                elif u.node[ego]["gay_weight"] < u.node[ego]["straight_weight"]:
                    u.node[ego]["orientation"] = 1
        
            tolabel[ego] = u.node[ego]["orientation"] * (u.node[ego]["gay_weight"] - u.node[ego]["straight_weight"])/u.node[ego]["total_weight"]
                #print ego
            sys.stdout.write ("%d %d %f %f %f\n" % (ego, u.node[ego]["orientation"], u.node[ego]["gay_weight"], u.node[ego]["straight_weight"], u.node[ego]["total_weight"]))
            



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
                u.node[alter]["gay_weight"] -= u.node[ego]["orientation"] * u[ego][alter]["embeddedness"]**ep
                u.node[alter]["straight_weight"] += u.node[ego]["orientation"] * u[ego][alter]["embeddedness"]**ep

                if u.node[alter]["orientation"] == 0:
                    if u.node[alter]["gay_weight"] > u.node[alter]["straight_weight"]:
                        u.node[alter]["orientation"] = -1
                    elif u.node[alter]["gay_weight"] < u.node[alter]["straight_weight"]:
                        u.node[alter]["orientation"] = 1
                tolabel[alter] = u.node[alter]["orientation"] * (u.node[alter]["gay_weight"] - u.node[alter]["straight_weight"])/u.node[alter]["total_weight"];
                
        u.node[ego]["orientation"] *= -1
        tolabel[ego] = u.node[ego]["orientation"] * (u.node[ego]["gay_weight"] - u.node[ego]["straight_weight"])/u.node[ego]["total_weight"];
        print "%d %f" % (ego, score)
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


def set_orientation_by_file2 (filename, legal_names, field_name, u):
    #print "HoHO"
    test_data = file(filename)
    legal = file (legal_names)
    lines = legal.readlines()
    legal.close()
    
    legal =  [int(x) for x in lines]
    legal = set(legal)

    #for ja in legal:
    #    print ja
    lines = test_data.readlines()
    test_data.close()
    for line in lines:
        k,v = line.split()
        ego = int(k)
        cl = 2 * int(v) - 1
        #print ego
        if ego in legal:
            u.node[ego][field_name] = cl
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
        snap_graph.write ("%d %d\n" % (node_untrans[i], v.node[node_untrans[i]]["orientation"]))
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

