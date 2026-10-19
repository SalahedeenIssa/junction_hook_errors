"""The d=9 triangular colour code in the orientation of Fig. 1 of Kishony & Fowler (red boundary at the bottom, green
on the left, blue on the right), used by the figure scripts. Coordinates: x in half-edge units, y = row index (row 0
at the bottom); data qubit indices are those of the authors' code.

data/d9_lattice.json holds the lattice and all 464 weight-9 logical operators. checks/enumerate_logicals.py verifies
that it has the authors' layout and the same operators as the enumeration. Figures are written to figures/output/."""
import json, math, itertools, collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE/'output'; OUT.mkdir(exist_ok=True)
A=json.load(open(HERE.parent/'data'/'d9_lattice.json'))
XY={int(k):tuple(v) for k,v in A['xy'].items()}
FACES=[{'qs':list(f['qs']),'c':f['c']} for f in A['faces']]
OPS=[frozenset(o) for o in A['ops']]            # all 464 weight-9 logical representatives
ROW=2*math.sqrt(3)
def pos(q): x,y=XY[q]; return (x, y*ROW)       # Cartesian, edge length 4
NB={q:{p for p in XY if p!=q and abs(math.dist(pos(p),pos(q))-4)<1e-6} for q in XY}
OFF={'TL':(-2,1),'TR':(2,1),'R':(4,0),'BR':(2,-1),'BL':(-2,-1),'L':(-4,0)}
# CNOT time step per corner, from the schedule in the authors' repository (index 0):
# code offsets a..f = TL,TR,R,BR,BL,L;  R=[1,3,2,5,4,6], G=[5,1,4,3,6,2], B=[1,5,3,6,2,4]
SCHED={'r':dict(zip(['TL','TR','R','BR','BL','L'],[1,3,2,5,4,6])),
       'g':dict(zip(['TL','TR','R','BR','BL','L'],[5,1,4,3,6,2])),
       'b':dict(zip(['TL','TR','R','BR','BL','L'],[1,5,3,6,2,4]))}
def corners(f):
    """map corner name -> qubit, using the (possibly virtual) hexagon centre."""
    qs=f['qs']
    for q0 in qs:
        for n0,(dx,dy) in OFF.items():
            cx,cy=XY[q0][0]-dx, XY[q0][1]-dy
            lab={}
            for q in qs:
                d=(XY[q][0]-cx, XY[q][1]-cy)
                m=[n for n,o in OFF.items() if o==d]
                if not m: break
                lab[m[0]]=q
            else:
                if len(lab)==len(qs): return lab,(cx,cy)
    raise ValueError(f)
for f in FACES:
    f['lab'],f['centre']=corners(f)
    f['kind']='hex' if len(f['qs'])==6 else 'trap'
    f['interior']=all(len(NB[q])==3 for q in f['qs'])
    order=sorted(f['lab'],key=lambda n:SCHED[f['c']][n])
    f['order']=order
    f['hooks']=[tuple(order[:2]),tuple(order[-2:])] if f['kind']=='hex' else [tuple(order[-2:]),tuple(order[:2])]
DEAD=set(XY)-set().union(*OPS)
def ecol(a,b):
    """colour of edge (a,b): the colour of the two faces it connects at its endpoints.
    For an edge on the patch boundary the face missing across it has the boundary's colour."""
    if b not in NB[a]: return None
    sh={f['c'] for f in FACES if a in f['qs'] and b in f['qs']}
    if len(sh)==2: return ({'r','g','b'}-sh).pop()
    present={f['c'] for f in FACES if a in f['qs'] or b in f['qs']}
    missing={'r','g','b'}-present
    rest={'r','g','b'}-sh-missing
    return rest.pop() if len(missing)==1 and len(rest)==1 else None
def face_of(q,c):
    for f in FACES:
        if f['c']==c and q in f['qs']: return f
    return None
def cooc(a,b): return [L for L in OPS if a in L and b in L]
def is_junction_pair(a,b,L):
    """a and b are the two neighbours, on one stabilizer, of a junction of L: a data qubit not in L whose three
    neighbours are all in L."""
    return any(v not in L and len(NB[v])==3 and NB[v]<=L for v in NB[a]&NB[b])
def _trace(L,starts):
    out={}
    for s,c in starts:
        path=[s]; q=s
        while True:
            F=face_of(q,c)
            if F is None: break                      # q sits on the c boundary: leg ends
            p=list((set(F['qs'])&L)-{q})
            if len(p)!=1: return None
            p=p[0]; path.append(p)
            nx=[x for x in NB[p] if ecol(p,x)==c]
            if not nx: break                          # p's c-edge is missing: leg ends on the c boundary
            if nx[0] in L: path.append(nx[0]); q=nx[0]
            else: return None
        out[c]=path
    cov=[q for p in out.values() for q in p]
    return out if (set(cov)==set(L) and len(cov)==len(L)) else None
def legs(L):
    """Decompose a weight-9 logical into coloured legs meeting at one junction.
    Returns (('v',vertex) or ('q',qubit), {colour: [qubits along the leg, junction end first]}) or None."""
    L=set(L)
    for v in XY:
        if v not in L and len(NB[v])==3 and NB[v]<=L:
            out=_trace(L,[(t,ecol(v,t)) for t in NB[v]])
            if out: return ('v',v),out
    for j in L:
        if all(face_of(j,c) is not None for c in 'rgb'):
            out=_trace(L,[(j,c) for c in 'rgb'])
            if out: return ('q',j),out
    return None
