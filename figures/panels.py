from lattice import *
PANELS=[('a','Bulk red hexagon',[11,12,20,27,26,19]),('b','Bulk green hexagon',[38,39,44,48,47,43]),('c','Bulk blue hexagon',[28,29,35,41,40,34]),
        ('d','Boundary red trapezoid',[15,16,30,23]),('e','Boundary green trapezoid',[2,10,9,1]),('f','Boundary blue trapezoid',[54,55,57,59]),
        ('g','Boundary red hexagon',[9,10,18,25,24,17]),('h','Boundary green hexagon',[52,53,56,58,57,55]),('i','Boundary blue hexagon',[6,7,15,23,22,14])]
def face_by_qs(qs):
    return next(f for f in FACES if set(f['qs'])==set(qs))
