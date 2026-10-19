"""Figure 4 of the note: one junction hook error for every type of non-corner stabilizer under the schedule of
Kishony & Fowler, d=9. Each panel shows a scheduled weight-2 hook error and a minimum-weight logical operator
containing it. The examples are chosen by witnesses.py and stored in data/witnesses.json; checks/fault_injection.py
injects each into the authors' circuit."""
import math, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon, Circle
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerTuple, HandlerPatch
from lattice import XY, FACES, pos
from lattice import OUT
W=json.load(open(OUT.parent.parent/'data'/'witnesses.json'))
FILL={'r':'#E9BAB7','g':'#C1DFC5','b':'#BFCAED'}
LEG={'r':'#C62828','g':'#1B7F3B','b':'#2743A8'}
EDGE='#9A9C9C'; ORANGE='#D9773D'; DARK='#1A1A1A'
NAMES={'r':'red','g':'green','b':'blue'}

def _segdist(p,seg):
    (ax_,ay),(bx,by)=seg; px,py=p; dx,dy=bx-ax_,by-ay
    t=max(0,min(1,((px-ax_)*dx+(py-ay)*dy)/(dx*dx+dy*dy or 1)))
    return math.hypot(px-ax_-t*dx,py-ay-t*dy)

def panel(ax,w):
    for f in FACES:
        pts=[pos(q) for q in f['qs']]
        cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
        pts.sort(key=lambda p: math.atan2(p[1]-cy,p[0]-cx))
        ax.add_patch(Polygon(pts,closed=True,facecolor=FILL[f['c']],edgecolor=EDGE,lw=0.45,zorder=1))
    v=w['v']
    # hooked plaquette outline and CNOT time steps
    f=next(F for F in FACES if set(F['qs'])==set(w['face']))
    pts=[pos(q) for q in f['qs']]
    cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
    ring=sorted(pts,key=lambda p: math.atan2(p[1]-cy,p[0]-cx))
    ax.add_patch(Polygon(ring,closed=True,fill=False,edgecolor=DARK,lw=1.3,zorder=3,joinstyle='round'))
    # CNOT time steps: place each number where it clears the hook pair, the qubits and the other labels
    hook=[pos(w['pair'][0]),pos(w['pair'][1])]
    obstacles_seg=[(hook,1.35)]
    obstacles_pt=[(pos(q),1.35) for q in w['pair']]+[(pos(q),0.9) for q in XY]
    placed=[]
    for name,q in w['lab'].items():
        x,y=pos(q); r=math.hypot(cx-x,cy-y); ux,uy=(cx-x)/r,(cy-y)/r
        cands=[(x+t*r*ux,y+t*r*uy) for t in ((0.53,0.40,0.66,0.30) if len(w['face'])==6 else (0.62,0.45,0.75))]
        for ang in (35,-35,60,-60,90,-90,125,-125):
            a=math.radians(ang)
            ox,oy=-(ux*math.cos(a)-uy*math.sin(a)), -(ux*math.sin(a)+uy*math.cos(a))   # outward direction rotated by ang
            for rr in (1.7,2.2): cands.append((x+rr*ox,y+rr*oy))
        H=12*2*math.sqrt(3)
        inside=lambda p: p[1]>=0.3 and p[1]<=H and abs(p[0]-24)<=24*(1-p[1]/H)-0.3
        def clearance(p):
            m=min(_segdist(p,sg)-rad for sg,rad in obstacles_seg)
            m=min(m,min(math.dist(p,o)-rad for o,rad in obstacles_pt))
            if placed: m=min(m,min(math.dist(p,o)-2.1 for o in placed))
            return m
        best=next((p for p in cands if inside(p) and clearance(p)>=0),max([p for p in cands if inside(p)] or cands,key=clearance))
        placed.append(best)
        ax.text(best[0],best[1],str(w['times'][name]),fontsize=5.6,ha='center',va='center',zorder=3.4,color=DARK,
                fontfamily='serif',path_effects=[pe.withStroke(linewidth=1.4,foreground='white')])
    # hook pair
    (x1,y1),(x2,y2)=pos(w['pair'][0]),pos(w['pair'][1])
    ax.plot([x1,x2],[y1,y2],color=ORANGE,lw=2.3,zorder=4,solid_capstyle='round',
            path_effects=[pe.Stroke(linewidth=3.4,foreground=DARK),pe.Normal()])
    # qubits, logical support, hook endpoints
    L=set(w['L'])
    for q in XY:
        x,y=pos(q)
        if q in w['pair']:
            ax.plot(x,y,'o',ms=4.6,mfc=ORANGE,mec=DARK,mew=0.6,zorder=7)
        elif q in L:
            ax.plot(x,y,'o',ms=3.6,mfc=DARK,mec=DARK,mew=0,zorder=6)
        else:
            ax.plot(x,y,'o',ms=2.0,mfc='white',mec='#8A8A8A',mew=0.35,zorder=5)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(-1,49); ax.set_ylim(-1.2,12*2*math.sqrt(3)+1.2)
    ax.set_title(r'$\mathbf{('+w['key']+')}$ '+w['title'],fontsize=8,loc='left',pad=3,fontfamily='serif')

if __name__=='__main__':
    plt.rcParams['font.family']='serif'; plt.rcParams['mathtext.fontset']='cm'
    fig,axs=plt.subplots(3,3,figsize=(6.5,6.35))
    for ax,k in zip(axs.flat,'abcdefghi'): panel(ax,W[k])
    handles=[Line2D([],[],ls='none',marker='o',ms=4,mfc=DARK,mec=DARK),
             Line2D([],[],color=ORANGE,lw=2.3,marker='o',ms=4.6,mfc=ORANGE,mec=DARK,mew=0.6,
                    path_effects=[pe.Stroke(linewidth=3.4,foreground=DARK),pe.Normal()]),
             Polygon([[0,0],[1,0],[1,1],[0,1]],fill=False,ec=DARK,lw=1.3)]
    labels=['Weight-9 logical support','Scheduled hook pair','Hooked plaquette (CNOT time steps)']
    fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,fontsize=7,handlelength=2.6,columnspacing=1.6,handletextpad=0.5)
    fig.subplots_adjust(left=0.01,right=0.99,top=0.965,bottom=0.045,wspace=0.04,hspace=0.14)
    fig.savefig(OUT/'fig_single_hook_shortcuts_d9.pdf'); fig.savefig(OUT/'fig_single_hook_shortcuts_d9.png',dpi=250)
    print('ok')
