"""Figure 1 of the note: junction hook errors, on the d=9 triangular colour code.
The logical operator L below is one of the 464 weight-9 representatives. Its red, green and blue strings meet at the
junction v=33, which is not in L but whose three neighbours are. On each of the three stabilizers that contain v, the two
neighbours of v form a junction pair (dotted yellow): (34, 39) on the red stabilizer, (27, 34) on the green one and
(27, 39) on the blue one. Under the schedule of Kishony & Fowler these are the weight-2 hook errors at positions 5,6
(red), 1,2 (green) and 5,6 (blue). checks/fault_injection.py injects each into their circuit: the hook error plus the
7 remaining data errors fire no detector and flip the observable."""
import math, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon, Circle
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerTuple, HandlerPatch
from lattice import XY, FACES, OPS, pos, legs
from lattice import OUT

L=frozenset([3,11,27,34,35,36,39,42,43]); assert L in set(OPS)
(J,v),LEGS=legs(L); assert J=='v' and v==33
PAIRS=[(34,39),(27,34),(27,39)]   # junction pairs on the red, green and blue stabilizers that contain v
FILL={'r':'#FFE0E0','g':'#E0FFE0','b':'#E0E0FF'}
LEG={'r':'#E27575','g':'#6DBB7E','b':'#7394DE'}
EDGE='#8893AB'; DARK='#1A1A1A'; YELLOW='#E8A800'; CASE='#6B5200'

def draw(ax):
    for f in FACES:
        pts=[pos(q) for q in f['qs']]
        cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
        pts.sort(key=lambda p: math.atan2(p[1]-cy,p[0]-cx))
        ax.add_patch(Polygon(pts,closed=True,facecolor=FILL[f['c']],edgecolor=EDGE,lw=0.6,zorder=1))
    for c,path in LEGS.items():
        xs,ys=zip(*[pos(q) for q in [v]+path])
        ax.plot(xs,ys,color=LEG[c],lw=5.2,solid_capstyle='round',solid_joinstyle='round',zorder=2)
    for a,b in PAIRS:
        (x1,y1),(x2,y2)=pos(a),pos(b)
        ax.plot([x1,x2],[y1,y2],color=YELLOW,lw=2.8,alpha=0.9,ls=(0,(0.05,1.45)),dash_capstyle='round',zorder=4)
    for q in XY:
        x,y=pos(q)
        if q in L:    ax.plot(x,y,'o',ms=4.6,mfc=DARK,mec=DARK,mew=0,zorder=6)
        else:           ax.plot(x,y,'o',ms=3.4,mfc='white',mec='#666666',mew=0.5,zorder=5)
    x,y=pos(v)
    ax.add_patch(Circle((x,y),1.45,fill=False,ec=DARK,lw=1.0,ls=(0,(2.0,1.4)),zorder=7.5))
    H=12*2*math.sqrt(3)
    kw=dict(fontsize=9,color='#333333',fontfamily='serif')
    ax.text(24,-2.6,'red boundary',ha='center',va='top',**kw)
    ax.text(12-1.6,H/2,'green boundary',ha='right',va='center',**kw)
    ax.text(36+1.6,H/2,'blue boundary',ha='left',va='center',**kw)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(-17,65); ax.set_ylim(-5.2,H+1.0)

if __name__=='__main__':
    plt.rcParams['font.family']='serif'; plt.rcParams['mathtext.fontset']='cm'
    fig,ax=plt.subplots(figsize=(5.2,3.75))
    draw(ax)
    hook_handle=Line2D([],[],color=YELLOW,lw=2.8,alpha=0.9,ls=(0,(0.05,1.45)),dash_capstyle='round')
    string_handle=tuple(Line2D([],[],color=LEG[c],lw=4.6) for c in 'rgb')
    junction_handle=Circle((0,0),1,fill=False,ec=DARK,lw=1.0,ls=(0,(2.0,1.4)))
    handles=[Line2D([],[],ls='none',marker='o',ms=4.6,mfc=DARK,mec=DARK),string_handle,junction_handle,hook_handle]
    labels=['Minimum weight logical operator','Red, green and blue strings','Junction',
            'Possible junction hook errors']
    circ=HandlerPatch(patch_func=lambda legend,orig_handle,xdescent,ydescent,width,height,fontsize:
                      Circle((width/2-xdescent,height/2-ydescent),height*0.62))
    ax.legend(handles,labels,loc='upper left',bbox_to_anchor=(0.0,1.0),ncol=1,frameon=False,fontsize=7.6,
              handler_map={string_handle:HandlerTuple(ndivide=None,pad=0.25),Circle:circ},
              handlelength=2.8,handletextpad=0.6,labelspacing=0.55,borderaxespad=0.2)
    fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
    fig.savefig(OUT/'fig_junction_hook_d9.pdf',bbox_inches='tight',pad_inches=0.03); fig.savefig(OUT/'fig_junction_hook_d9.png',dpi=300,bbox_inches='tight',pad_inches=0.03)
    print('ok')
