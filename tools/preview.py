import sys;sys.path.insert(0,'tools')
import ndspy.rom,gfxpatch as G,gfx
from PIL import Image,ImageDraw
import os;r=ndspy.rom.NintendoDSRom.fromFile(os.environ.get('ROM','../Kimi no Yuusha (Japan).nds'))
names=[r.filenames.filenameOf(i) for i in range(len(r.files))];N=set(names)
def pal_for(n):
  b=n.rsplit('.',1)[0]
  if b+'.NCLR' in N:return b+'.NCLR'
  c=sorted(x for x in N if x.endswith('.NCLR') and x.rsplit('/',1)[0]==b.rsplit('/',1)[0])
  return c[0] if c else None
def render(n):
  b=n.rsplit('.',1)[0];p=pal_for(n)
  try:
    if b+'.NSCR' in N:return G.BG(r,n,pal=p).rgba()
    if b+'.NCER' in N:
      a=G.Asset(r,n,pal=p);ims=[a.rgba(i) for i in range(len(a.cl))]
      W=max(i.width for i in ims);S=Image.new('RGBA',(W,sum(i.height for i in ims)));y=0
      for i in ims:S.paste(i,(0,y));y+=i.height
      return S
    c=gfx.Char(r.getFileByName(n));P=gfx.pal(r.getFileByName(p))
    return (gfx.bitmap(c,P) if c.lin and c.tw!=65535 else gfx.sheet(c,P)).convert('RGBA')
  except Exception as e:print('ERR',n,e);return None
if __name__=='__main__':
  out=sys.argv[1];sel=sys.argv[2:]
  ims=[(n,render(n)) for n in sel];ims=[(n,i) for n,i in ims if i]
  for n,i in ims:i.thumbnail((256,384))
  cols=4;W=cols*260;H=sum(max(i.height for _,i in ims[k:k+cols])+14 for k in range(0,len(ims),cols))
  S=Image.new('RGB',(W,H),(0,90,0));d=ImageDraw.Draw(S);y=0
  for k in range(0,len(ims),cols):
    row=ims[k:k+cols]
    for j,(n,i) in enumerate(row):S.paste(i,(j*260,y+14),i);d.text((j*260,y),n.split('/')[-1],fill=(255,255,0))
    y+=max(i.height for _,i in row)+14
  S.save(out)
