"""Chooses the nine examples of Figure 4 (one per type of non-corner stabilizer): for each, a scheduled weight-2 hook
error that is a junction pair of a minimum weight logical operator, preferring operators whose strings are short.
Run without arguments to compare the choice with data/witnesses.json, or with --write to overwrite that file."""
import math, json
from panels import *
def polylen(pts): return sum(math.dist(pos(a),pos(b)) for a,b in zip(pts,pts[1:]))
USED=set()
def choose(key):
    title,qs=[(t,q) for k,t,q in PANELS if k==key][0]
    f=face_by_qs(qs)
    # the malign hook representative that forms a junction
    cands=[]
    for names in f['hooks']:
        a,b=(f['lab'][n] for n in names)
        com=NB[a]&NB[b]
        if len(com)!=1: continue
        v=next(iter(com))
        for L in cooc(a,b):
            r=legs(L)
            if r and r[0]==('v',v):
                J,lg=r
                score=sum(polylen([v]+p) for p in lg.values())
                cands.append((score,sorted(L),names,(a,b),v,lg))
    cands.sort(key=lambda t:(t[0],t[1]))
    pick=next((c for c in cands if tuple(c[1]) not in USED),cands[0])
    score,L,names,pair,v,lg=pick
    USED.add(tuple(L))
    phys_last = (names==f['hooks'][0]) if f['kind']=='trap' else (list(names)==f['order'][-2:])
    return dict(key=key,title=title,face=qs,colour=f['c'],kind=f['kind'],names=names,pair=pair,v=v,L=L,legs=lg,
                order=f['order'],times={n:SCHED[f['c']][n] for n in f['lab']},lab=f['lab'],centre=f['centre'],
                rep_is_last_two=phys_last, n_candidates=len(cands))
W={k:choose(k) for k,_,_ in PANELS}
if __name__=='__main__':
    import sys
    for k,w in W.items():
        print(k,w['title'],w['names'],w['pair'],'v',w['v'],'L',w['L'],'legs',{c:len(p) for c,p in w['legs'].items()},'last-two rep' if w['rep_is_last_two'] else 'FIRST-two rep')
    path=HERE.parent/'data'/'witnesses.json'
    if '--write' in sys.argv:
        json.dump(W,open(path,'w'),default=list); print('wrote',path)
    else:
        same=json.loads(json.dumps(W,default=list))==json.load(open(path))
        print('same examples as data/witnesses.json:',same); assert same
