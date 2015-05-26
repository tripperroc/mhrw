def split (data, label, values):
    test = dict()
    train = dict()
    counts = {k: 0 for k in values}
    
    for k,v in data.items():
        counts[v[label]] +=1
    for k,v in data.items():
        if counts[v[label]] > 0:
            counts[v[label]] -= 2
            test[k] = v
        else:
            train[k] = v
    return (train, test)
