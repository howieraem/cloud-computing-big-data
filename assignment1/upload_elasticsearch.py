"""
HOW TO RUN in Unix shell:
ES_USR={elasticsearch master username} ES_PWD={elasticsearch master password} ES_ENDPOINT={elasticsearch endpoint} DATA_DIR={path to directory with data jsons} python upload_elasticsearch.py
"""
import json
import os
import subprocess as sp


data_dir = os.get('DATA_DIR', 'hw1_data')
files = os.listdir(data_dir)
res = 'es-cuisines.json'


C = {"chinese", "newamerican", "japanese", "korean", "indpak", "italian", "french", "mexican", "portuguese", "turkish"}
american = {'newamerican', 'tradamerican'}
chinese = {'chinese', 'cantonese', 'dimsum', 'hainan', 'szechuan', 'shanghainese', 'noodles'}
italian = {'italian', 'calabrian', 'sardinian', 'sicilian', 'tuscan'}
french = {'french', 'mauritius', 'reunion'}
japanese = {'japanese', 'conveyorsushi', 'izakaya', 'japacurry', 'ramen', 'teppanyaki'}


def paraphrase(cuisine):
    if cuisine in chinese:
        return 'chinese'
    elif cuisine in american:
        return 'newamerican'
    elif cuisine in italian:
        return 'italian'
    elif cuisine in french:
        return 'french'
    elif cuisine in japanese:
        return 'japanese'
    return cuisine


def get_cuisines(cuisines):
    res = set()
    for c in cuisines:
        c = paraphrase(c['alias'])
        if c in C:
            res.add(c)
    return list(res)


cnt = 0
with open(res, 'w+') as wf:
    for f in files:
        try:
            d = json.load(open(os.path.join(data_dir, f)))
            d1 = {"index": {"_index": "restaurants", "_id": d['id']}}
            cuisines = get_cuisines(d['categories'])
            if not len(cuisines):
                continue
            d2 = {"cuisine": cuisines}
            wf.write('{}\n{}\n'.format(json.dumps(d1), json.dumps(d2)))
            cnt += 1
        except Exception:
            continue

print(f"Got {cnt} restaurants after processing!") 

ES_USR = os.environ['ES_USR']
ES_PWD = os.environ['ES_PWD']
ES_ENDPOINT = os.environ['ES_ENDPOINT']
proc = sp.run(f"curl -XPOST -u '{ES_USR}:{ES_PWD}' '{ES_ENDPOINT}/_bulk' --data-binary @{res} -H 'Content-Type: application/json'")
while proc.returncode != 0:
    proc = sp.run(f"curl -XPOST -u '{ES_USR}:{ES_PWD}' '{ES_ENDPOINT}/_bulk' --data-binary @{res} -H 'Content-Type: application/json'")

