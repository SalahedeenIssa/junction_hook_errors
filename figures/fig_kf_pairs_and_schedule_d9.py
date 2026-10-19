"""Figure 3 of the note: two panels mirroring Fig. 1 of Kishony & Fowler (arXiv:2603.28852) on the d=9 triangular colour code:
(a) their malign pairs (red/green/blue, transcribed from their Fig. 1(a)) with the junction pairs added in yellow;
(b) their schedule, i.e. the CNOT time step of every data qubit in every stabilizer, from the orderings released with
their circuits (R=[1,3,2,5,4,6], G=[5,1,4,3,6,2], B=[1,5,3,6,2,4] over corners TL,TR,R,BR,BL,L)."""
import math, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon
from lattice import XY, FACES, pos, SCHED
from lattice import OUT
import fig_kf_malign_pairs_junction_d9 as A

NUM={'r':'#C8102E','g':'#028A3F','b':'#005A9E'}

def draw_schedule(ax):
    for f in FACES:
        pts=[pos(q) for q in f['qs']]
        cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
        ring=sorted(pts,key=lambda p: math.atan2(p[1]-cy,p[0]-cx))
        ax.add_patch(Polygon(ring,closed=True,facecolor=A.FILL[f['c']],edgecolor=A.EDGE,lw=0.7,zorder=1))
        c=f['centre']; ax.plot(c[0],c[1]*2*math.sqrt(3),'o',ms=1.6,color='#333333',zorder=2)
        for name,q in f['lab'].items():
            x,y=pos(q); t=0.33 if len(f['qs'])==6 else 0.36
            ax.text(x+t*(cx-x),y+t*(cy-y),str(SCHED[f['c']][name]),fontsize=6.3,fontweight='bold',
                    ha='center',va='center',color=NUM[f['c']],zorder=3,fontfamily='DejaVu Sans')
    for q in XY:
        x,y=pos(q); ax.plot(x,y,'o',ms=3.2,mfc='white',mec='#666666',mew=0.5,zorder=5)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(-1.5,49.5); ax.set_ylim(-1.5,12*2*math.sqrt(3)+1.5)

if __name__=='__main__':
    assert A.check_fig1a_pairs()
    plt.rcParams['font.family']='serif'
    fig,(a,b)=plt.subplots(1,2,figsize=(6.6,3.05))
    A.draw(a,lw_pair=1.9); draw_schedule(b)
    for ax,l in ((a,'a'),(b,'b')):
        ax.text(0.0,0.97,l,transform=ax.transAxes,fontsize=13,fontweight='bold',va='top',fontfamily='serif')
    fig.subplots_adjust(left=0.005,right=0.995,top=0.99,bottom=0.01,wspace=0.04)
    fig.savefig(OUT/'fig_kf_pairs_and_schedule_d9.pdf'); fig.savefig(OUT/'fig_kf_pairs_and_schedule_d9.png',dpi=300)
    print('ok')
