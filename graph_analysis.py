f = file("34-2014_labeled_twitter_graph.pkl")
 g34 = pickle.load(f)
 f.close()
 f = file("02-2015_labeled_twitter_graph.pkl")
 g02 = pickle.load(f)
 labeled34 = [x for x in g34.nodes() if "orientation" in g34.node[x]]
 gay34 = [x for x in labeled34 if g34.node[x]["orientation"] == 1]
 sorted(34.degree(gay34), key=operator.itemgetter(1))
straight34 = [x for x in labeled34 if g34.node[x]["orientation"] == 1]
 sorted(34.degree(straight34), key=operator.itemgetter(1))

 
 
