"""python gridview.py out.png scale file1 [file2..] : BG를 격자와 함께 확대 렌더"""
import sys,os;sys.path.insert(0,os.path.dirname(__file__))
import ndspy.rom,gfxpatch as G
from PIL import Image,ImageDraw
r=ndspy.rom.NintendoDSRom.fromFile(os.environ.get('ROM','../Kimi no Yuusha (Japan).nds'))
out,s=sys.argv[1],int(sys.argv[2]);ims=[]
for n in sys.argv[3:]:
  im=G.BG(r,n).rgba();S=Image.new('RGB',im.size,(0,0,0));S.paste(im,(0,0),im)
  S=S.resize((im.width*s,im.height*s),0);d=ImageDraw.Draw(S)
  for x in range(0,im.width,16):d.line([(x*s,0),(x*s,S.height)],fill=(255,0,0) if x%64==0 else (255,160,160))
  for y in range(0,im.height,16):d.line([(0,y*s),(S.width,y*s)],fill=(255,0,0) if y%64==0 else (255,160,160))
  for x in range(0,im.width,32):d.text((x*s+1,0),str(x),fill=(255,255,0))
  for y in range(0,im.height,32):d.text((0,y*s+1),str(y),fill=(255,255,0))
  ims.append(S)
W=Image.new('RGB',(sum(i.width for i in ims),max(i.height for i in ims)));x=0
for i in ims:W.paste(i,(x,0));x+=i.width
W.save(out)
