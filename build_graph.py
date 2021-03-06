import networkx as nx
import json
import pickle

def build_graph (unlabeled_data_name, graph_data_name):
    global di
    di = nx.DiGraph()

    unlabeled_data = file (unlabeled_data_name)
    graph_data = file (graph_data_name)

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
                if out_neighbor == ego:
                    print "self %d" % ego
                elif out_neighbor in di:
                    di.add_edge(ego, out_neighbor)
            for in_neighbor in j["friend_ids"]:
                if in_neighbor == ego:
                    print "self %d" % ego
                elif in_neighbor in di:
                    di.add_edge(in_neighbor, ego)
        except ValueError:
            pass
    graph_data.close()

    
    u = di.to_undirected(reciprocal=True)

    #return u

    ccs = nx.connected_component_subgraphs(u)
    l = sorted(ccs, key = lambda x: len(x), reverse=True)
    u = l[0]

    #l = list(u.nodes())
    #v = u.subgraph(l[0:8000])
    #ccs = nx.connected_component_subgraphs(v)
    #l = sorted(ccs, key = lambda x: len(x), reverse=True)
    #u = l[0]
    for ego,alter in u.edges():
        #u[ego][alter]["embeddedness"] = 1 + len(set(u.neighbors(ego)) & set(u.neighbors(alter)))
        u[ego][alter]["embeddedness"] = float(len(set(u.neighbors(ego)) & set(u.neighbors(alter))) + 1) / float(min(len(u.neighbors(ego)), len(u.neighbors(alter))) + 1)

    return u

neighbors = set()
def build_neighbor_graph (labeled_data_name, graph_pkl_name):
    global u
    global neighbors
    
    labeled_data = file (labeled_data_name)
    graph_file = file (graph_pkl_name)
    u = pickle.load(graph_file)

    print len(u)
    
    global neighbors 
    while True:
        line = labeled_data.readline()
        if line == "":
            break
        orientation, description, key, profile_image_url, profile_banner_url, profile_background_image_url = line.split("\t")
        
        ego = int(key)
        if ego in u:
            egoset = set()
            egoset.add(ego)
            neighbors = neighbors | set(u.neighbors(ego)) | egoset
            #print len(neighbors)

    labeled_data.close()
    u.remove_nodes_from(set(u.nodes()) - neighbors)
    print len(u)
    #u = di.to_undirected(reciprocal=True)
    ccs = nx.connected_component_subgraphs(u)
    l = sorted(ccs, key = lambda x: len(x), reverse=True)
    u = l[0]
    print len(u)
    return u

def read_json_graph (graph_data):

   #graph_data.seek(0)
   #global u
   nodes = set ()
   #global l
   while True:
        line = graph_data.readline()
        if line == "":
            break
        try:
            j = json.loads(line)
            nodes.add(int(j["user_id"]))

        except ValueError:
            pass
   u = nx.Graph()

   graph_data.seek(0)
   while True:
        line = graph_data.readline()
        if line == "":
            break
        #print line
        try:
            j = json.loads(line)
            ego = int(j["user_id"])
            u.add_node(ego)
            u.node[ego]["position"] = "core"
            for neighbor in set(j["follower_ids"]).intersection(set(j["friend_ids"])):
                if ego != neighbor:
                    u.add_edge(ego, neighbor)
                    if not neighbor in nodes:
                        u.node[ego]["position"] = "fringe"

            u.node[ego]["local"] = True
        except ValueError:
            pass

   return u

## START HERE
def read_likely_possible_graph (graph_data, likely_core_graph, possible_core_graph):

   extended_users = set()
   u = nx.Graph(likely_core_graph)
   while True:
        line = graph_data.readline()
        if line == "":
            break
        #print line
        try:
            j = json.loads(line)
            ego = int(j["user_id"])
            if u in likely_core_graph:
                #u.add_node(ego)
                #u.node[ego]["position"] = "core"
                for neighbor in (set(j["follower_ids"]).intersection(set(j["friend_ids"]))).difference(set(like_core_graph.neighbors(ego))):
                    if ego != neighbor:
                        u.add_edge(ego, neighbor)
                        if not neighbor in possible_users:
                            u.node[neighbor]["position"] = "fringe"
                        else:
                            u.node[neighbor]["position"] = "extended"
                            extended_users.add(neighbor)
        except ValueError:
            pass
   
   return (u, extended_users)

def read_core_graph (graph_data):
   #global u
   nodes = set ()
   #global l
   u = nx.Graph()

   
   while True:
        line = graph_data.readline()
        if line == "":
            break
        try:
            j = json.loads(line)
            nodes.add(int(j["user_id"]))

        except ValueError:
            pass

   graph_data.seek(0)
   while True:
        line = graph_data.readline()
        if line == "":
            break
        #print line
        try:
            j = json.loads(line)
            ego = int(j["user_id"])
            u.add_node(ego)
            for neighbor in set(j["follower_ids"]).intersection(set(j["friend_ids"])).intersection(nodes):
                if neighbor != ego:
                    u.add_edge(ego, neighbor)
            u.node[ego]["position"] = "core"
        except ValueError:
            pass

   return u

def read_json_graph_nonrecip(f):
   u = nx.DiGraph()
   while True:
        line = f.readline()
        if line == "":
            break
        #print line
        try:
            j = json.loads(line)
            ego = int(j["user_id"])
            u.add_node(ego)
            for neighbor in set(j["friend_ids"]).difference(j["follower_ids"]):
                if neighbor != ego:
                    u.add_edge(ego, neighbor)
            #u.node[ego]["local"] = True
        except ValueError:
            pass

   return u

def read_json_graph_nonrecip_restricted_to(f, users, ids):
   u = nx.DiGraph()
   while True:
        line = f.readline()
        if line == "":
            break
        #print line
        try:
            j = json.loads(line)
            ego = int(j["user_id"])
            if ego in users:
                u.add_node(ego)
                if "role" in u.node[ego] and  u.node[ego]["role"] == "entity":
                    #u.node[ego]["role"] = "user"
                    u.node[ego]["role"] = "other"
                else:
                    u.node[ego]["role"] = "user"
                followers = set(j["follower_ids"])
                friends = set(j["friend_ids"])
                for neighbor in (friends - followers).union(friends & ids):
                    if neighbor != ego:
                        u.add_edge(ego, neighbor)
                        if "role" in u.node[neighbor] and  u.node[neighbor]["role"] in {"user", "other"}:
                            u.node[neighbor]["role"] = "other"
                        else:
                            u.node[neighbor]["role"] = "entity"
        except ValueError:
            pass

   return u
