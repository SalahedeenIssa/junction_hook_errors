"""Link-by-link description of the two logical operators in the string-colour figure."""
import math
from lattice import XY, FACES, OPS, pos
BCOL={'left':'g','right':'b','bottom':'r'}
def faces_with(*qs): return [f for f in FACES if set(qs)<=set(f['qs'])]
def polygon_sides(f):
    pts=f['qs']; c=[sum(pos(q)[i] for q in pts)/len(pts) for i in (0,1)]
    ring=sorted(pts,key=lambda q: math.atan2(pos(q)[1]-c[1],pos(q)[0]-c[0]))
    return {frozenset((ring[i],ring[(i+1)%len(ring)])) for i in range(len(ring))}
def boundary_of(a,b):
    (x1,y1),(x2,y2)=XY[a],XY[b]
    if y1==0 and y2==0: return 'bottom'
    if abs(x1-2*y1)<=2 and abs(x2-2*y2)<=2: return 'left'
    if abs(48-x1-2*y1)<=2 and abs(48-x2-2*y2)<=2: return 'right'
def link(a,b):
    """('edge', colour) if a,b form a side of a stabilizer, else ('pair', colour of the stabilizer holding both)."""
    fs=faces_with(a,b)
    if any(frozenset((a,b)) in polygon_sides(f) for f in fs):
        present={f['c'] for f in fs}
        if len(fs)==1: present.add(BCOL[boundary_of(a,b)])
        return 'edge',({'r','g','b'}-present).pop()
    assert len(fs)==1
    return 'pair',fs[0]['c']
CORNER=[4,12,27,33,44,48,55,57,60]      # red string from the red boundary into the green-blue corner
BOUNDARY=[0,17,24,37,42,51,54,59,60]    # the logical operator along the green boundary
def syn(E): return [f['c'] for f in FACES if len(set(f['qs'])&set(E))%2]
if __name__=='__main__':
    for name,Lq in (('corner',CORNER),('boundary',BOUNDARY)):
        assert frozenset(Lq) in set(OPS)
        print(name)
        for a,b in zip(Lq,Lq[1:]):
            kind,c=link(a,b)
            (x1,y1),(x2,y2)=pos(a),pos(b)
            ang=round(math.degrees(math.atan2(y2-y1,x2-x1)))%180
            print(f'  {a:2d}-{b:2d}: {kind:4s} {c}  orientation {ang:3d} deg  | X on both flips: {syn([a,b])}')
