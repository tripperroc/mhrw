import csv
import sys
jlabels = dict()

f = open("jubin-orientations-34.csv")
jreader = csv.reader(f)
for line in jreader:
    try:
        #print "%s %d" % (line[0], int(line[2]))
        jlabels[int(line[2])] = line[0]
    except ValueError:
        pass

#g = open("labeled_users.txt")
g = open(sys.argv[1])
newlabel  = 0
coverage = 0
gayagree = 0
straightagree = 0
autogay = 0
autostraight = 0
jubingay = 0
jubinstraight = 0
for line in g:
    try:
        daata = line.split('\t')
        (key, label) = (int(daata[2]), daata[0])
        #print "%s %d %d" % (daata[0], int(daata[2]), len(daata))
        try:
            if jlabels[key] != label:
                daata[2] = str(jlabels[key])
                newlabel += 1
            else:
                if label == "Gay":
                    gayagree += 1
                if label == "Straight":
                    straightagree += 1
            coverage +=1
            if jlabels[key] == "Gay":
                jubingay += 1
            if jlabels[key] == "Straight":
                #sys.stderr.write ("woohoo!!\n")
                jubinstraight +=1
            if label == "Gay":
                autogay += 1
            if label == "Straight":
                autostraight += 1
        except KeyError:
            pass
        stg = str("\t")
        sys.stdout.write (stg.join(daata))
        #jabels[int(daata[2])] = daata[0]
    except ValueError:
        pass

prgayagree = (jubingay/float(jubingay + jubinstraight)) * (autogay/float(autogay + autostraight))
prstraightagree = (jubinstraight/float(jubingay + jubinstraight)) * (autostraight/float(autogay + autostraight))
pre = prgayagree + prstraightagree
practualagree = 1 - newlabel/float(autogay + autostraight)
kappa = (practualagree - pre)/(1-pre)
sys.stderr.write ( "%d %d %d %d %d %d %d %d %f\n" % (newlabel, coverage, jubingay, jubinstraight, autogay, autostraight, gayagree, straightagree, kappa))
