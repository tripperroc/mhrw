# usage  python -i read_entities_followed.py ../13-2015_social_graph.json LGBTQ-entities.txt ../13-2015_master_user_list.json
import networkx as nx
import pickle
from build_graph import *
from nxsp import *
import sys
import json
import operator
import numpy
import scipy
import scipy.stats
import math
from networkx.algorithms import bipartite as bp
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import TruncatedSVD
from sklearn import linear_model
from sklearn.metrics import roc_auc_score, roc_curve, auc
from sklearn.pipeline import Pipeline
from sklearn import cross_validation
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import normalize
from itertools import count

dims = 35 # optimal value for ROC AUC is around 35

Y = None
cf = list()
X = y = scores = None
tpr = fpr = thresholds = None
u = nx.DiGraph()
w = nx.Graph()
v = nx.DiGraph()
k = dict()
ents = []
user_nums = set()
users = dict()
filtered_users = set()
l = list()
gay_graph_vince = nx.Graph()
straight_graph_vince = nx.Graph()
naive_gay = dict()
naive_straight = dict()
conf = dict()
gay_users = dict()
straight_users = dict()
pr_gay = dict()
pr_straight = dict()
entity_apriori = dict()
entities = set ()
entity_given_gay = dict()
entity_given_straight = dict()
neighbors = set()
users = dict()
labeled_users  = dict()
likeliness = dict()
gay_apriori = float()
straight_apriori = float()
likely_orientation = list()
where_dey_is = list ()
entitylist = list()
userlist = list()
m_bi = np.zeros(0)
m_bi2 = np.zeros(0)
svd = TruncatedSVD(n_components=dims, random_state=42)
logistic = linear_model.LogisticRegression(class_weight = {1:11, 0:1})
pipe = Pipeline(steps=[('svd', svd), ('logistic', logistic)])
gnb = GaussianNB()
row = col = M = None
allusers = testing_users =  None

# return a list of gay, straight users based on 
def find_gay (entitylist, model, filename, userdata):

    global Y
    global X
    f = open(filename)
    featset = set(entitylist)
    z = nx.Graph()
    z.add_nodes_from(entitylist)
    
    labels = {}
    #userlist = []
    while True:
        u = z.copy()
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
            X = bp.biadjacency_matrix(u, [ego], entitylist)
            Y = model.decision_function(X)

        except ValueError:
            pass
        labels.update({x: ('Gay' if y > 15 else 'Straight') for x,y in zip(userlist,Y) if abs(y) > 15})
    f.close()
    
    #X = bp.biadjacency_matrix(u, userlist, entitylist)
    #Y = model.decision_function(X)
    
    
    #labels = {x: ('Gay' if y > 15 else 'Straight') for x,y in zip(userlist,Y) if abs(y) > 15}

    users = {x: y.update({'orientation': labels[x]}) for x,y in userdata.items() if x in labels}
    #return {}
    return users

def add_edges (u,v):
    w = u.copy()
   
        
    for x,y in v.edges():
        if (x in u) and (y in u) and (not u.has_edge(x,y)) and (x != y):
            w.add_edge(x,y)
    return w

def plot_roc (fpr, tpr, roc_auc, name, text = ""):
    plt.clf()
    plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic')
    plt.legend(loc="lower right")
    plt.savefig(name)
    plt.clf()


def main():
    global likely_orientation
    global where_dey_is
    global pipe
    global v
    global cf
    global likeliness
    global u
    global ents
    global ids
    global gay_graph_vince
    global straight_graph_vince
    global allusers
    global naive_gay
    global naive_straight
    global gay_users
    global straight_users
    global conf
    global entity_apriori
    global entities
    global entitylist
    global userlist
    global entity_given_gay
    global entity_given_straight
    global neighbors 
    global pr_gay
    global pr_straight
    global users
    global labeled_users
    global gay_apriori
    global straight_apriori
    global m_bi
    global m_bi2
    global svd
    global linear_model
    global fpr
    global tpr
    global thresholds
    global w
    global X
    global y
    global scores
    global gnb
    global testing_users
    
    ents = numpy.genfromtxt(sys.argv[2], delimiter="\t", skip_header=1, dtype=[('username', 'S32'), ('num_followers', 'i4'), ('entity_type', 'S2'), ('id', 'i8')])
    ids = set(ents['id'][0:-1])  # need to remove last entity because it currently has no id label

    print "Loading users"
    f = open(sys.argv[3])
    users = json.load(f)
    f.close()



    print "Finding labeled users"
    users = {int(k):v for k,v in users.items()}

    allusers = users
    labeled_users = {k: v for k,v in users.items() if "orientation" in v}
    (users, testing_users) = split(labeled_users, "orientation", {"Straight", "Gay"})
    straight_users = {k: v for k,v in users.items() if v["orientation"] == "Straight"}
    gay_users = {k: v for k,v in users.items() if v["orientation"] == "Gay"}

    gay_apriori = len(gay_users)/float(len(straight_users) + len(gay_users))
    straight_apriori = len(straight_users)/float(len(straight_users) + len(gay_users))
    print "Reading graph"
    f = open(sys.argv[1])
    v = read_json_graph_nonrecip_restricted_to(f, users.keys(), ids)
    #v = read_json_graph_with_ids(f, users.keys())
    f.close()

    print "Reading vince graph"
    u = nx.DiGraph(v)
    # Gives us all entities defined as those who don't recipocate
    u.remove_nodes_from ([k for k,w in v.node.items() if (not k in users) and (w["role"] != "entity")])
    vincy = u.copy()
    allzy = u.copy()
    # Gives us all entities as defined by Vince
    vincy.remove_nodes_from ([k for k,w in v.node.items() if (not k in users) and (not k in ids)])
    vincy.graph['name'] = "Vince"
    # Gives us all entities as defined by Vince
    allzy.remove_edges_from([(x,y) for (x,y) in v.edges() if v.node[x]["role"] == v.node[y]["role"]])
    allzy.graph['name'] = "All"
    

    for u in [vincy, allzy]:
        print "Finding useful features"

        gay_graph_vince = u.subgraph([k for k,w in u.node.items() if (w["role"] == "entity") or (k in gay_users)])
        straight_graph_vince = u.subgraph([k for k,w in u.node.items() if (w["role"] == "entity") or (k in straight_users)])
        # Gives us all entities defined as those who don't recipocate
        entities = [x for x,y in u.node.items() if y["role"] == "entity" and gay_graph_vince.degree([x])[x] > 0 and straight_graph_vince.degree([x])[x] > 0 ]
        # Gives us all entities as defined by Vince
        #entities = [x for x in list(ids.intersection(u.nodes())) if u.degree([x])[x] > 0]

        cf = [(y, scipy.stats.bayes_mvs([0 if users[x]['orientation'] == 'Straight' else 1 for x in u.predecessors(y)])[0][1]) for y in entities if len(u.predecessors(y)) > 1]
        
        #entities = [x for x,y in cf if y > gay_apriori]
        #entities = [x for (x,(y,z)) in cf if y > .2 or z < 1 - .2]
        entity_count = float(sum([u.degree([x])[x] for x in entities]))
        entity_given_gay = {x: ((gay_graph_vince.degree([x])[x]) / float(len(gay_users))) for x in entities}
        entity_given_straight = {x: ((straight_graph_vince.degree([x])[x]) / float(len(straight_users))) for x in entities }

        entity_apriori = {x : (u.degree([x])[x])/float(len(users)) for x in entities}
    
    
        #test a naive classifier on the training set to see how well it fits the observations
        for k in set(users.keys()).intersection(u.nodes()):
            neighbors = set(u.neighbors(k)) 
            e_apriori = reduce (lambda x, y : x*y, map(lambda z: entity_apriori[z] if z in neighbors else 1 - entity_apriori[z], entities))
            e_given_g = reduce (lambda x, y : x*y, map(lambda z: entity_given_gay[z] if z in neighbors else 1 - entity_given_gay[z], entities))
            e_given_s = reduce (lambda x, y : x*y, map(lambda z: entity_given_straight[z] if z in neighbors else 1 - entity_given_straight[z], entities))
            pr_gay[k] = 0 if e_apriori == 0 else (e_given_g  * gay_apriori / e_apriori)
            pr_straight[k] = 0 if e_apriori == 0 else (e_given_s  * straight_apriori / e_apriori)
    # currently the graph with

        sorted([(z, entity_given_straight[z]/entity_apriori[z]) for z in entities], key=operator.itemgetter(1))

        min_straight = min([pr_straight[z] for z in set(users.keys()).intersection(u.nodes()) if pr_straight[z] > 0])
        pr_straight = {z: (pr_straight[z] if pr_straight[z] > 0 else min_straight) for z in set(users.keys()).intersection(u.nodes())} 
        likeliness = {z: pr_gay[z]/pr_straight[z] for z in set(users.keys()).intersection(u.nodes())}
        likely_orientation = [(x,y, users[x]["orientation"]) for x,y in sorted(likeliness.items(), key=operator.itemgetter(1))]
        where_dey_is = [x for x,y in enumerate (likely_orientation) if y[2] == "Gay"]
        likeliness_gay = [math.log(y) for x,y in likeliness.items() if users[x]["orientation"] == "Gay" and y > 0]
        likeliness_straight = [math.log(y) for x,y in likeliness.items() if users[x]["orientation"] == "Straight" and y > 0]
        uzers = list(set(users.keys()).intersection(u.nodes()))
        uzers_est = [likeliness[x] for x in uzers]
    
        uzers_real = [1 if users[x]["orientation"] == 'Gay' else 0 for x in uzers]
    

        fpr, tpr, thresholds = roc_curve(uzers_real, uzers_est)
        roc_auc = auc(fpr, tpr)
        plot_roc(fpr, tpr,roc_auc, "charts/naive_roc.pdf", "(Naive Bayes)")
        print "%s: Naive bayes: Area under the ROC curve : %f" % (u.graph["name"], roc_auc)

        plt.hist([likeliness_gay, likeliness_straight],20, normed=1, histtype='bar', color=['crimson', 'burlywood'], label=['Gay', 'Straight'], log=True)
        plt.ylabel("Frequency (Log)")
        plt.xlabel("Log-Likeliness")
        plt.title("Naive Bayes Model")
        plt.legend()
        plt.savefig('charts/naive-bayes-normed-%s.pdf' % u.graph["name"],bbox_inches='tight')

        plt.clf()

    
        w = u.to_undirected()
        userlist = uzers
        entitylist = list(set(entities).intersection(w.nodes()))
        
        
        #m_bi = bim(w, entitylist, userlist)
        m_bi = bp.biadjacency_matrix(w, entitylist, userlist)
   
        m_bi2 = np.matrix.transpose(m_bi)

        #m_bi2 = normalize(m_bi2)
        
        #gayrowi=[x for x,y in enumerate(userlist) if users[y]["orientation"] == "Gay"]
        #gayrows = m_bi2[gayrowi]

        #for i in range(11):
        #    m_bi2 = np.concatenate((m_bi2, gayrows))
        
        #U, s, Vh = np.linalg.svd(m_bi2)
    
    
        X = svd.fit_transform(m_bi2)
        y = [1 if users[x]["orientation"] == "Gay" else 0 for x in userlist] # + [1]*11*len(gayrows)
        
        logistic.fit(X,y)
        yp = logistic.decision_function(X)

        fpr, tpr, thresholds = roc_curve(y, yp)
        roc_auc = auc(fpr, tpr)
        print "%s: SVD -> Logit: Area under the ROC curve : %f" % (u.graph["name"], roc_auc)

        #roc_auc_score(y, yp)
        likeliness_gay = [z for x,z in zip(userlist,yp) if users[x]['orientation'] == 'Gay']
        likeliness_straight = [z for x,z in zip(userlist,yp) if users[x]['orientation'] == 'Straight']
    
        plt.hist([likeliness_gay, likeliness_straight],30, normed=1, histtype='bar', color=['crimson', 'burlywood'], label=['Gay', 'Straight'])
        plt.ylabel("Frequency")
        plt.xlabel("Confidence")
        plt.title("SVD Plus Logistic Regression")
        plt.legend()
        plt.savefig('charts/svd-logit-normed-%s.pdf' % u.graph["name"], bbox_inches='tight')
        plt.clf()

        plt.hist([likeliness_gay, likeliness_straight],30, histtype='bar', log=True, color=['crimson', 'burlywood'], label=['Gay', 'Straight'])
        plt.ylabel("Frequency")
        plt.xlabel("Confidence")
        plt.title("SVD Plus Logistic Regression")
        plt.legend()
        plt.savefig('charts/svd-logit-%s.pdf' % u.graph["name"], bbox_inches='tight')
        plt.clf()

        plot_roc(fpr, tpr, roc_auc, "charts/svd-logit_roc-%s.pdf"  % u.graph["name"], "(SVD-Logit, %d Dims)" % dims)

        scores = cross_validation.cross_val_score(pipe, m_bi2, y, cv=10, scoring='roc_auc')
        # Yo! You might want to call '%pylab' if you exit into the ipython environment

        print "%s: svd->logit" % u.graph['name']
        print scores
        print scores.mean()
        
        #gnb.fit(m_bi2, y)
        
        scores = cross_validation.cross_val_score(gnb, m_bi2, y, cv=10, scoring='roc_auc')
        # Yo! You might want to call '%pylab' if you exit into the ipython environment

        print "%s: naive" % u.graph['name']
        print scores
        print scores.mean()
    new_users = find_gay(entitylist, pipe, sys.argv[1], allusers)
        
if __name__ == "__main__":
    main()
