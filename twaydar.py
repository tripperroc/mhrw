# Filters twitter json profiles file for sexual orientation based on keyword
# python -OO gaydar.py master_user_list.json

# usage:
# export PYTHONIOENCODING=utf-8; python twaydar.py TWITTER_USER_FILE

import nltk
import sys
import re
import json

def printout (orientation, key, value):
    description = value["description"].replace("\n", " ")
    description = description.replace('\r', '')
    sys.stdout.write(orientation + "\t" + description.encode('utf-8') + "\t" + key.encode('utf-8'))
                
    sys.stdout.write("\t")
    if "profile_image_url" in value:
        sys.stdout.write(value["profile_image_url"])
    sys.stdout.write("\t")
    if "profile_banner_url"  in value:
        sys.stdout.write(value["profile_banner_url"])
    sys.stdout.write("\t")
    if "profile_background_image_url" in value:
        sys.stdout.write(value["profile_background_image_url"])
                
    sys.stdout.write("\n")

j = dict()
              
def main():
    global j
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
                j[key]["orientation"] = "Gay"
            if tokens & {"straight", "heterosexual", "husband", "wife"}:
                printout("Straight", key, value)
                j[key]["orientation"] = "Straight"
    f.close()

    f = file (sys.argv[1], 'w')
    json.dump(j,f)
    
if __name__ == "__main__":
    main()
