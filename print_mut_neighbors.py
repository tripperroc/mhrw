import sys
import re
import math
import json
import networkx as nx
import pickle
#import pqdict
#from snap_write import *

def main():
    
    global di
    global u
    global v
    global gays
    global straights
    global gay_cliques
    global straight_cliques
    global B
    global x
    global y
 
    graph_file = file (sys.argv[1])
    u = pickle.load(graph_file)
    graph_file.close()

    print ("u v neighbs")
    for x, y in u.edges():
        print ("%d %d %f" % (x, y, u[x][y]["embeddedness"]))
        #print u[x][y]

if __name__ == "__main__":
    main()
