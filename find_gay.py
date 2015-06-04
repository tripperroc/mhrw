# return a list of gay, straight users based on 
def find_gay (entitylist, model, filename, userdata):

    global userlist
    
    u = nx.Graph()
    f = open(filename)
    featset = set(entitylist)
    userlist = []
    while True:
        line = f.readline()
        if line == "":
            break
        #print line
        try:
            j = json.loads(line)
            ego = int(j["user_id"])
            if ego not in featset:
                u.add_node(ego)
                userlist.append(ego)
                for neighbor in (set(j["friend_ids"]).union(set(j["follower_ids"]))).intersection(featset):
                     u.add_edge(ego, neighbor)
        except ValueError:
            pass
        
    X = bp.biadjacency_matrix(u, userlist, entitylist)
    y = model.decision_function(X)
    
    labels = {x: ('Gay' if y > .2 else 'Straight') for x,y in zip(userlist,X) if math.abs(y) > 15}

    users = {x: y.update({'orientation': labels[x]}) for x,y in userdata if x in labels}

    return users

    
