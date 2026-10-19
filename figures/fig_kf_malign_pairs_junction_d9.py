"""Panel (a) of Figure 3 of the note: Fig. 1(a) of Kishony & Fowler, "Color code off-the-hook" (arXiv:2603.28852),
redrawn on the d=9 triangular colour code, with the junction hook errors added in yellow.
Pairs in red/green/blue are transcribed from their Fig. 1(a); every one was checked against the 464
minimum-weight logical operators (see check_fig1a_pairs below)."""
import math, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.patheffects as pe
from lattice import XY, FACES, NB, OPS, pos, cooc, is_junction_pair
from lattice import OUT

FILL={'r':'#FFE0E0','g':'#E0FFE0','b':'#E0E0FF'}          # face colours of their figure
LINE={'r':'#E71223','g':'#03B153','b':'#0070C0'}          # pair colours of their figure
EDGE='#8893AB'; YELLOW='#FFC400'
# (qubit, qubit, colour) exactly as highlighted in their Fig. 1(a)
KF_PAIRS=[
 # green hexagon (bulk)
 (47,48,'b'),(47,43,'r'),(48,44,'r'),(44,39,'b'),(47,44,'g'),(47,39,'g'),(43,44,'g'),(43,39,'g'),
 # blue hexagon (bulk)
 (41,35,'g'),(34,28,'r'),(35,29,'r'),(28,29,'g'),(41,34,'b'),(34,35,'b'),(41,28,'b'),(35,28,'b'),
 # red hexagon (bulk)
 (26,27,'g'),(26,19,'b'),(19,11,'g'),(11,12,'b'),(26,11,'r'),(27,12,'r'),(26,12,'r'),(27,11,'r'),
 # blue trapezoid (left boundary)
 (24,37,'r'),(37,31,'g'),(31,25,'r'),(24,25,'g'),
 # red trapezoid (right boundary)
 (53,56,'b'),(56,50,'g'),(53,49,'g'),(49,50,'b'),
 # green trapezoid (bottom boundary)
 (5,13,'r'),(13,14,'b'),(14,6,'r'),(5,6,'b'),
]
# junction hook errors added here. On each hexagon: the pair of neighbours of the junction vertex.
# On each trapezoid: both diagonals, which are the same hook error up to the stabilizer (one is a junction pair).
JUNCTION=[(48,43),(41,29),(12,19),(25,37),(24,31),(50,53),(49,56),(14,5),(6,13)]

def check_fig1a_pairs():
    for a,b,_ in KF_PAIRS: assert cooc(a,b), (a,b)
    for a,b in JUNCTION:  assert cooc(a,b), (a,b)
    # each hexagon junction pair is a junction pair in every logical that contains it
    for a,b in JUNCTION[:3]: assert all(is_junction_pair(a,b,L) for L in cooc(a,b))
    # on each trapezoid exactly one diagonal is itself a junction pair
    for d1,d2 in (JUNCTION[3:5],JUNCTION[5:7],JUNCTION[7:9]):
        j=[all(is_junction_pair(*d,L) for L in cooc(*d)) for d in (d1,d2)]
        assert sorted(j)==[False,True], (d1,d2,j)
    return True

def draw(ax, lw_pair=2.3):
    for f in FACES:
        pts=[pos(q) for q in f['qs']]
        cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
        pts.sort(key=lambda p: math.atan2(p[1]-cy,p[0]-cx))
        ax.add_patch(Polygon(pts,closed=True,facecolor=FILL[f['c']],edgecolor=EDGE,lw=0.7,zorder=1,joinstyle='round'))
        c=f['centre']; ax.plot(c[0],c[1]*2*math.sqrt(3),'o',ms=1.6,color='#333333',zorder=4.5)
    for a,b,col in KF_PAIRS:
        (x1,y1),(x2,y2)=pos(a),pos(b)
        ax.plot([x1,x2],[y1,y2],color=LINE[col],lw=lw_pair,solid_capstyle='butt',zorder=3)
    for a,b in JUNCTION:
        (x1,y1),(x2,y2)=pos(a),pos(b)
        ax.plot([x1,x2],[y1,y2],color=YELLOW,lw=lw_pair,solid_capstyle='butt',zorder=4,
                path_effects=[pe.Stroke(linewidth=lw_pair+1.1,foreground='#6B5200'),pe.Normal()])
    for q in XY:
        x,y=pos(q); ax.plot(x,y,'o',ms=3.2,mfc='white',mec='#666666',mew=0.5,zorder=5)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(-1.5,49.5); ax.set_ylim(-1.5,12*2*math.sqrt(3)+1.5)

if __name__=='__main__':
    assert check_fig1a_pairs()
    fig,ax=plt.subplots(figsize=(4.0,3.62))
    draw(ax)
    fig.subplots_adjust(0,0,1,1)
    fig.savefig(OUT/'fig_kf_malign_pairs_junction_d9.pdf'); fig.savefig(OUT/'fig_kf_malign_pairs_junction_d9.png',dpi=300)
    print('ok')
