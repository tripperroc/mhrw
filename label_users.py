# Filters twitter json profiles file for sexual orientation based on keyword
# python -OO gaydar.py master_user_list.json

# usage:
# export PYTHONIOENCODING=utf-8; python twaydar.py TWITTER_USER_FILE

import nltk
import sys
import re
import json

def printout (orientation, key, value):
                
    value["orientation"] = orientation
    k[key] = value

j = dict()
k = dict()

def main():
    global j
    global k
    lmtzr = nltk.stem.wordnet.WordNetLemmatizer()
    f = file (sys.argv[1])
    j = json.load(f)
    for key, value in j.iteritems():
        description = value["description"]
        if description:
            tokens = nltk.word_tokenize(value["description"])
            tokens = [lmtzr.lemmatize(w.lower()) for w in tokens]
            tokens = frozenset(tokens)
            if tokens & frozenset({"homosexual", "homo", "lesbian", "dike", "gay"}):
                printout("Gay", key, value)
            if tokens & {"straight", "heterosexual", "husband", "wife"}:
                printout("Straight", key, value)
    f.close()
    g = file(sys.argv[2], 'w')
    json.dump(k, g)
    
if __name__ == "__main__":
    main()
