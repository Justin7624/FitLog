"""Original anatomical loft / implicit surface. No external mesh or texture assets.
Coordinates in cm; x right, y up, z anterior. Rebuild with numpy, scipy, scikit-image.
"""
import numpy as np, json
from scipy.interpolate import PchipInterpolator
from skimage.measure import marching_cubes
from pathlib import Path
# Shape is sculpted from anatomical cross sections with front/back asymmetry.
# Rings: height, center x, center z, lateral radius, anterior-posterior radius.
step=1.05
X,Y,Z=np.meshgrid(np.arange(-57,57+step,step,dtype=np.float32),np.arange(-3,179+step,step,dtype=np.float32),np.arange(-26,31+step,step,dtype=np.float32),indexing='ij',sparse=True)

def loft(rings, sculpt=None):
    a=np.array(rings); lo,hi=a[0,0],a[-1,0]; yy=np.clip(Y,lo,hi)
    cx,cz,rx,rz=[PchipInterpolator(a[:,0],a[:,i])(yy).astype(np.float32) for i in range(1,5)]
    x=(X-cx)/rx; z=(Z-cz)/rz
    d=(np.sqrt(x*x+z*z)-1)*np.minimum(rx,rz)
    if sculpt is not None: d=d+sculpt(x,z,yy)
    return np.maximum(d,np.maximum(lo-Y,Y-hi)).astype(np.float32)

def ga(v,c,s):return np.exp(-((v-c)/s)**2)
def smin(a,b,k):
    h=np.maximum(k-np.abs(a-b),0)/k
    return np.minimum(a,b)-h*h*k*.25

def torso_shape(x,z,y):
    # subtly raised pectorals, lats, gluteal lobes, abdominal wall, scapulae
    return (-.95*ga(y,134,5)*ga(np.abs(x),.45,.38)*ga(z,.92,.35)
            -.72*ga(y,119,9)*ga(np.abs(x),.85,.32)*ga(z,-.45,.55)
            -.8*ga(y,91,6)*ga(np.abs(x),.48,.32)*ga(z,-.95,.32)
            +.55*ga(y,91,6)*ga(x,0,.15)*ga(z,-.98,.30)
            -.45*ga(y,109,8)*ga(x,0,.75)*ga(z,.95,.32))
# torso includes taper into neck, rounded pelvis; hips connect to both thighs
field=loft([(76,0,-.2,2,2),(80,0,-.4,10.5,8),(86,0,-.5,15.4,10.4),(92,0,-.3,17,11.1),(99,0,0,16.1,10.1),(108,0,0,13.5,9.0),(115,0,0,14,9.1),(123,0,-.5,16.3,10.5),(132,0,-.5,18.2,11.3),(139,0,-.3,18.6,10.0),(143,0,-.3,17.2,8),(147,0,0,10.5,5.7),(150,0,0,5.4,4.8),(155,0,0,5,4.6)],torso_shape)
# neck, skull, jaw and face, smooth silhouette, small facial relief, no detailed identity
head=loft([(148,0,0,4.6,4.6),(153,0,.2,5,4.8),(156,0,1.1,5.5,5.5),(158,0,1,6.5,6.1),(163,0,.1,7.3,7.6),(169,0,-.5,7.4,7.5),(173,0,-.7,5.8,5.7),(175,0,-.7,.5,.6)],lambda x,z,y: -.25*ga(y,163,1.5)*ga(z,.95,.3)*ga(np.abs(x),.5,.23)+.4*ga(y,165,1.2)*ga(z,.96,.25)*ga(np.abs(x),.48,.23))
field=smin(field,head,2.5)
def ell(cx,cy,cz,rx,ry,rz):return (np.sqrt(((X-cx)/rx)**2+((Y-cy)/ry)**2+((Z-cz)/rz)**2)-1)*min(rx,ry,rz)
field=smin(field,ell(0,163.4,7.5,1.2,2.6,2),.9)
for side in [-1,1]:
    def L(rows,sc=None):return loft([(y,side*x,z,rx,rz) for y,x,z,rx,rz in rows],sc)
    # relaxed A-pose arms, deltoid / biceps / triceps / forearm contours, tapered hand
    arm=L([(75,39.5,0,1.7,1.6),(79,38.7,.4,3.5,2.1),(84,36.7,.5,4.1,2.5),(89,35.2,.4,2.7,2.6),(94,34,.3,3.3,3.3),(101,32.1,.1,4.3,3.9),(108,30.6,-.2,4.7,4.0),(113,29.6,-.2,3.9,3.8),(117,28.1,0,4.1,4.2),(123,26.3,0,5.3,5),(130,24.4,-.1,6,5.7),(136,22.3,-.1,6.4,6),(141,20.1,-.1,6.7,6.3),(145,17.8,0,4.7,4.8),(147,16,0,1.5,1.5)],lambda x,z,y: -.65*ga(y,126,5)*ga(z,.94,.35)-.55*ga(y,130,6)*ga(z,-.95,.35)-.35*ga(y,103,5)*ga(z,.8,.5))
    field=smin(field,arm,2.8)
    field=smin(field,ell(side*33.6,84.8,2.0,2.0,4.3,1.75),1.3) # thumb contour
    field=smin(field,ell(side*7.2,162.8,-.1,1.5,3,1.65),.8) # ear
    # leg with quadriceps, hamstring, patella, calf, ankle
    leg=L([(4,10.7,0,3.8,3.7),(8,10.6,-.5,3.5,3.5),(15,10.3,-.8,3.8,4),(25,10,-.8,5,5.3),(34,9.6,-1,6.1,6.4),(41,9.3,-.5,5.6,5.8),(48,9.1,.0,5.0,4.9),(54,9,.6,5.5,5.4),(62,9,.1,6.9,6.5),(72,8.9,-.1,8.2,8.4),(80,8.7,-.3,9.2,9.3),(87,8.6,-.6,9,9.1),(92,8.1,-.4,6.9,6.8),(97,7.9,-.4,2,2)],lambda x,z,y: -.85*ga(y,69,11)*ga(np.abs(x),.5,.45)*ga(z,.9,.4)-.4*ga(y,34,6)*ga(z,-.9,.35)-.4*ga(y,48,3)*ga(z,1,.4))
    field=smin(field,leg,2.0)
    foot=L([(0,10.7,4.8,2.0,4.7),(1,10.7,4.8,4.5,8.2),(3,10.7,4,4.9,9.0),(5,10.7,2.6,4.4,7.4),(8,10.6,.6,3.7,4.8),(10,10.6,-.3,3,3.2)])
    field=smin(field,foot,1.9)
verts,faces,_,_=marching_cubes(field,level=0,spacing=(step,step,step),allow_degenerate=False,gradient_direction='ascent')
verts+=np.array([-57,-3,-26]); verts[:,1]-=verts[:,1].min(); verts*=175/verts[:,1].max()
# verify consistent outward winding, normalize volume sign
v=verts[faces]; volume=np.einsum('ij,ij->i',v[:,0],np.cross(v[:,1],v[:,2])).sum()/6
if volume<0:faces=faces[:,::-1]
# Store a compact original template (rounded cm) as a local classic script, offline and no fetch.
asset={'vertices':np.round(verts,3).flatten().tolist(),'triangles':faces.flatten().tolist(),'height':175,'license':'CC0-1.0','description':'Original continuous anatomical loft template, stylized, not a scanned person.'}
path=Path(__file__).resolve().parents[1]/'assets'/'body-mesh.js'
path.write_text('/* Original FitLog anatomical mesh, CC0-1.0. */\nconst FITLOG_BODY_MESH='+json.dumps(asset,separators=(',',':'))+';\nif(typeof module!=="undefined")module.exports=FITLOG_BODY_MESH;\n')
print(len(verts),'vertices',len(faces),'triangles',path.stat().st_size,'bytes')
import trimesh
m=trimesh.Trimesh(verts,faces,process=False);print('watertight',m.is_watertight,'connected',len(m.split(only_watertight=False)),'volume liters',m.volume/1000)
