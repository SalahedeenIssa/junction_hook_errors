"""Figure 2 of the note: logical operators built from one or two string colours (d=9):
(a) a red string from the red boundary into the corner where the green and blue boundaries meet;
(b) the logical operator along the green boundary, which alternates between red and blue edges.
Solid links are edges of the string's colour (including the long sides of weight-4 boundary stabilizers);
dashed links are two data qubits of one stabilizer of the string's colour. Link types are computed in strings_examples.py."""
import math, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerPatch
from lattice import XY, FACES, pos
from lattice import OUT
from strings_examples import CORNER, BOUNDARY, link
FILL={'r':'#FFE0E0','g':'#E0FFE0','b':'#E0E0FF'}
LEG={'r':'#D9534F','g':'#3E9E57','b':'#4A74D0'}
EDGE='#8893AB'; DARK='#1A1A1A'; H=12*2*math.sqrt(3)

def base(ax):
    for f in FACES:
        pts=[pos(q) for q in f['qs']]; cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
        pts.sort(key=lambda p: math.atan2(p[1]-cy,p[0]-cx))
        ax.add_patch(Polygon(pts,closed=True,facecolor=FILL[f['c']],edgecolor=EDGE,lw=0.55,zorder=1))
    kw=dict(fontsize=7.5,color='#333333',fontfamily='serif')
    ax.text(24,-2.3,'red boundary',ha='center',va='top',**kw)
    ax.text(12-3.2,H/2,'green\nboundary',ha='right',va='center',**kw)
    ax.text(36+3.2,H/2,'blue\nboundary',ha='left',va='center',**kw)
    ax.set_aspect('equal'); ax.axis('off'); ax.set_xlim(-12,60); ax.set_ylim(-5.2,H+1.2)

def path(ax,Lq):
    for a,b in zip(Lq,Lq[1:]):
        kind,c=link(a,b)
        (x1,y1),(x2,y2)=pos(a),pos(b)
        ax.plot([x1,x2],[y1,y2],color=LEG[c],lw=3.6,solid_capstyle='round',dash_capstyle='round',
                ls='-' if kind=='edge' else (0,(1.6,1.3)),zorder=3)
    for q in XY:
        x,y=pos(q)
        if q in Lq: ax.plot(x,y,'o',ms=4.2,mfc=DARK,mec=DARK,zorder=6)
        else: ax.plot(x,y,'o',ms=2.6,mfc='white',mec='#666666',mew=0.45,zorder=5)

if __name__=='__main__':
    plt.rcParams['font.family']='serif'
    fig,(a,b)=plt.subplots(1,2,figsize=(6.6,2.95))
    for ax in (a,b): base(ax)
    path(a,CORNER); path(b,BOUNDARY)
    a.set_title('One string color',fontsize=9,pad=2); b.set_title('Two string colors',fontsize=9,pad=2)
    for ax,l in ((a,'a'),(b,'b')):
        ax.text(0.0,1.0,l,transform=ax.transAxes,fontsize=12,fontweight='bold',va='top')
    handles=[Line2D([],[],ls='none',marker='o',ms=4.2,mfc=DARK,mec=DARK),
             Line2D([],[],color='#555555',lw=3.2,solid_capstyle='round'),
             Line2D([],[],color='#555555',lw=3.2,ls=(0,(1.6,1.3)),dash_capstyle='round')]
    labels=['Minimum weight logical operator',"Edge of the string's color","Two data qubits of a stabilizer of the string's color"]
    fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,fontsize=6.7,handlelength=2.2,
               columnspacing=1.1,handletextpad=0.45)
    fig.subplots_adjust(left=0.0,right=1.0,top=0.93,bottom=0.075,wspace=0.02)
    fig.savefig(OUT/'fig_string_colors_d9.pdf'); fig.savefig(OUT/'fig_string_colors_d9.png',dpi=300)
    print('ok')
