# Filters twitter json file text field 
# python -OO twep.py TWITTER_FILE REGEX

# usage:
# export PYTHONIOENCODING=utf-8; python twaydar.py TWITTER_USER_FILE
import sys
import re
import json
import networkx as nx


di = nx.DiGraph()
u = nx.Graph()           
def main():
    labeled_data = file (sys.argv[1]) # This should be the labeled data file
    unlabeled_data = file (sys.argv[2])
    graph_data = file (sys.argv[3])
    global di
    global u
    j = json.load(unlabeled_data)
    unlabeled_data.close ()
   
    
    for key, value in j.iteritems():
        #print key
        di.add_node(int(key))
    
    while True:
        line = graph_data.readline()
        if line == "":
            break
        #print line
        try:
            j = json.loads(line)
            ego = int(j["user_id"])
            for out_neighbor in j["follower_ids"]:
                if out_neighbor in di:
                    di.add_edge(ego, out_neighbor)
            for in_neighbor in j["friend_ids"]:
                if in_neighbor in di:
                    di.add_edge(in_neighbor, ego)
        except ValueError:
            pass
    graph_data.close()

    u = di.to_undirected(reciprocal=True)

    ccs = nx.connected_component_subgraphs(u)
    l = sorted(ccs, key = lambda x: len(x), reverse=True)
    u = l[0]
 
    gay_count = 0
    straight_count = 0
    while True:
        line = labeled_data.readline()
        if line == "":
            break
        orientation, description, key, profile_image_url, profile_banner_url, profile_background_image_url = line.split("\t")
        ego = int(key)
        if ego in u:
            if orientation == "Straight":
                straight_count += 1
            else:
                gay_count += 1

    labeled_data.close()

    print "# Gay labels:\t%d" % gay_count
    print "# Straight labels:\t%d" % straight_count
    
   

if __name__ == "__main__":
    main()
