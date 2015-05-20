# Filters twitter json profiles file for sexual orientation based on keyword
# python -OO gaydar.py master_user_list.json

# usage:
# export PYTHONIOENCODING=utf-8; python twaydar.py TWITTER_USER_FILE

import nltk
import sys
import re
import json
import collections

j = dict()

or = collections.defaultdict(int)
def main():
    global j
    lmtzr = nltk.stem.wordnet.WordNetLemmatizer()
    f = file (sys.argv[1])
    j = json.load(f)
    for key, value in j.iteritems():
        if "orientation" in value:
            or[value["orientation"]] +=1
    f.close()

    print or
    
if __name__ == "__main__":
    main()
