"""OBJ(셀) 그래픽 편집: 셀을 인덱스 캔버스로 렌더 → 수정 → 되쓰기"""
import struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import gfx
ROOT=__import__('pathlib').Path(__file__).resolve().parents[2]
def font(name,size):return ImageFont.truetype(str(ROOT/name),size)
class Asset:
  def __init__(s,rom,char,cer=None,pal=None):
    s.rom=rom;s.cn=char;base=char.rsplit('.',1)[0]
    s.c=gfx.Char(rom.getFileByName(char))
    s.cl,s.sh=gfx.cells(rom.getFileByName(cer or base+'.NCER'))
    names=s._names()
    if pal is None:
      pal=base+'.NCLR' if base+'.NCLR' in names else sorted(x for x in names if x.endswith('.NCLR') and x.rsplit('/',1)[0]==base.rsplit('/',1)[0])[0]
    s.P=np.array(gfx.pal(rom.getFileByName(pal)),dtype=int)
    s.px=np.array(gfx.allpix(s.c),dtype=np.int32)
  def _names(s):return set(s.rom.filenames.filenameOf(i) for i in range(len(s.rom.files)))
  def bbox(s,i):
    o=s.cl[i];return (min(a['x'] for a in o),min(a['y'] for a in o),max(a['x']+a['w'] for a in o),max(a['y']+a['h'] for a in o))
  def rgba(s,i):
    x0,y0,x1,y1=s.bbox(i);im=np.zeros((y1-y0,x1-x0,4),np.uint8)
    for o in reversed(s.cl[i]):
      idx=np.array(gfx.objpix(s.c,o,s.sh)).reshape(o['h'],o['w'])
      v=s.px[np.clip(idx,0,len(s.px)-1)]
      if o['hf']:v=v[:,::-1]
      if o['vf']:v=v[::-1]
      bank=o['pal']*16 if s.c.bd==4 else 0
      col=s.P[(bank+v)%len(s.P)]
      m=v!=0;sub=im[o['y']-y0:o['y']-y0+o['h'],o['x']-x0:o['x']-x0+o['w']]
      sub[m,:3]=col[m];sub[m,3]=255
    return Image.fromarray(im,'RGBA')
  def put(s,i,img):
    """RGBA 이미지를 셀 i 위치에 되씀(각 OBJ 팔레트로 양자화; 알파<128=투명)"""
    a=np.array(img.convert('RGBA')).astype(int);x0,y0,_,_=s.bbox(i)
    for o in s.cl[i]:
      idx=np.array(gfx.objpix(s.c,o,s.sh)).reshape(o['h'],o['w'])
      sub=a[o['y']-y0:o['y']-y0+o['h'],o['x']-x0:o['x']-x0+o['w']]
      if o['hf']:sub=sub[:,::-1]
      if o['vf']:sub=sub[::-1]
      if s.c.bd==4:cand=s.P[o['pal']*16+1:o['pal']*16+16];off=1
      else:cand=s.P[1:256];off=1
      d=((sub[:,:,None,:3]-cand[None,None])**2).sum(-1);v=d.argmin(-1)+off
      v[sub[:,:,3]<128]=0
      s.px[idx.ravel()]=v.ravel()
  def save(s):
    c=s.c
    for t in range(c.ntiles):c.put(t,list(s.px[t*64:(t+1)*64]))
    s.rom.setFileByName(s.cn,bytes(c.d))
def text_img(size,text,fnt,fill,outline=None,ow=1,spacing=0,align='center',anchor_box=None,lsp=2):
  """투명 배경에 외곽선 텍스트 그리기(가운데 정렬, 여러 줄)"""
  W,H=size;im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
  lines=text.split('\n');hs=[];ws=[]
  for l in lines:
    b=d.textbbox((0,0),l,font=fnt);ws.append(b[2]-b[0]);hs.append(b[3]-b[1])
  lh=max(fnt.getbbox('가')[3]-fnt.getbbox('가')[1],1);tot=lh*len(lines)+lsp*(len(lines)-1)
  y=(H-tot)//2
  for l,w in zip(lines,ws):
    b=d.textbbox((0,0),l,font=fnt);x=(W-w)//2-b[0] if align=='center' else ow-b[0]
    yy=y-fnt.getbbox('가')[1]
    if outline:
      for dx in range(-ow,ow+1):
        for dy in range(-ow,ow+1):
          if dx*dx+dy*dy<=ow*ow+1:d.text((x+dx,yy+dy),l,font=fnt,fill=outline)
    d.text((x,yy),l,font=fnt,fill=fill);y+=lh+lsp
  return im
def squeeze_text(size,text,fname,fs,fill,outline,ow,lsp=2,minscale=0.6,bg=None):
  """fs 크기로 그리고 넘치면 가로 압축(최소 minscale), 그래도 넘치면 글자 크기 축소"""
  W,H=size
  while True:
    f=font(fname,fs);im=text_img((W*3,H*2),text,f,fill,outline,ow,lsp=lsp);bb=im.getbbox()
    tw,th=bb[2]-bb[0],bb[3]-bb[1]
    if th<=H and tw*minscale<=W or fs<=8:break
    fs-=1
  crop=im.crop(bb)
  if tw>W:crop=crop.resize((W,th),Image.LANCZOS)
  a=np.array(crop);a[...,3]=np.where(a[...,3]>110,255,0);crop=Image.fromarray(a)
  out=bg.copy() if bg else Image.new('RGBA',(W,H),(0,0,0,0))
  out.alpha_composite(crop,((W-crop.width)//2,(H-crop.height)//2))
  return out
class Bitmap:
  """2D 비트맵 NCBR(lin) 직접 편집, 팔레트 뱅크 고정"""
  def __init__(s,rom,char,pal=None,bank=0):
    s.rom=rom;s.cn=char;s.c=gfx.Char(rom.getFileByName(char));s.bank=bank
    s.P=np.array(gfx.pal(rom.getFileByName(pal or char.rsplit('.',1)[0]+'.NCLR')),dtype=int)
    s.w=s.c.tw*8;s.px=np.array(gfx.allpix(s.c),dtype=np.int32).reshape(-1,s.w)
  def rgba(s,box):
    x0,y0,x1,y1=box;v=s.px[y0:y1,x0:x1];col=s.P[(s.bank*16+v)%len(s.P)]
    a=np.zeros(v.shape+(4,),np.uint8);a[...,:3]=col;a[...,3]=np.where(v>0,255,0);return Image.fromarray(a,'RGBA')
  def put(s,box,img):
    x0,y0,x1,y1=box;a=np.array(img.convert('RGBA')).astype(int)
    cand=s.P[s.bank*16+1:s.bank*16+16]
    d=((a[:,:,None,:3]-cand[None,None])**2).sum(-1);v=d.argmin(-1)+1;v[a[:,:,3]<128]=0
    s.px[y0:y1,x0:x1]=v
  def save(s):
    f=s.px.ravel()
    for t in range(s.c.ntiles):s.c.put(t,list(f[t*64:(t+1)*64]))
    s.rom.setFileByName(s.cn,bytes(s.c.d))
_BDF={}
def bdftext(text,fontfile,fill,outline,mode='shadow',extra=0,crop=True):
  """BDF 비트맵 폰트로 텍스트 렌더(안티앨리어싱 없음)"""
  from common import bdf
  if fontfile not in _BDF:_BDF[fontfile]=bdf(fontfile)
  G=_BDF[fontfile];pts=[];x=0;H=0
  (_,hg,_,yg),_,_=G[ord('가')];A=hg+yg
  for ch in text:
    if ch==' ':x+=3;continue
    (w,h,xo,yo),rows,dw=G[ord(ch)]
    for ry,row in enumerate(rows):
      v=int(row,16);nb=len(row)*4
      for cx in range(w):
        if v>>(nb-1-cx)&1:pts.append((x+xo+cx,ry+A-h-yo))
    x+=dw+extra
  W=x+2;H=max([p[1] for p in pts]+[A])+4;im=Image.new('RGBA',(W,H),(0,0,0,0))
  S=set(pts)
  if outline:
    for (px_,py) in pts:
      for dx,dy in {'full':((1,0),(0,1),(1,1),(-1,0),(0,-1),(-1,-1),(1,-1),(-1,1)),'side':((1,0),(-1,0),(0,1),(1,1),(-1,1))}.get(mode,((1,0),(0,1),(1,1))):
        q=(px_+dx+1,py+dy+1)
        if (q[0]-1,q[1]-1) not in S and 0<=q[0]<W and 0<=q[1]<H:im.putpixel(q,outline)
  for (px_,py) in pts:im.putpixel((px_+1,py+1),fill)
  return im.crop(im.getbbox()) if crop else im
class BG:
  """NCGR+NSCR 배경: 화면 단위 렌더/되쓰기"""
  def __init__(s,rom,char,scr=None,pal=None):
    s.rom=rom;s.cn=char;b=char.rsplit('.',1)[0]
    s.c=gfx.Char(rom.getFileByName(char))
    s.P=np.array(gfx.pal(rom.getFileByName(pal or b+'.NCLR')),dtype=int)
    d=rom.getFileByName(scr or b+'.NSCR');p=gfx.sect(d,b'NRCS')
    s.sw,s.sh=struct.unpack_from('<HH',d,p+8);n=struct.unpack_from('<I',d,p+16)[0]
    s.map=np.frombuffer(d[p+20:p+20+n],dtype='<u2').reshape(s.sh//8,s.sw//8)
    s.px=np.array(gfx.allpix(s.c),dtype=np.int32).reshape(-1,8,8)
  def _t(s,e):
    t=s.px[e&1023]
    if e>>10&1:t=t[:,::-1]
    if e>>11&1:t=t[::-1]
    return t
  def rgba(s):
    H,Wd=s.map.shape;a=np.zeros((H*8,Wd*8,4),np.uint8)
    for y in range(H):
      for x in range(Wd):
        e=int(s.map[y,x]);t=s._t(e);bank=(e>>12)*16 if s.c.bd==4 else 0
        a[y*8:y*8+8,x*8:x*8+8,:3]=s.P[(bank+t)%len(s.P)];a[y*8:y*8+8,x*8:x*8+8,3]=np.where(t>0,255,0)
    return Image.fromarray(a,'RGBA')
  def put(s,img,box):
    """box 영역(8정렬)을 되씀. 공유 타일 사용 수 반환"""
    a=np.array(img.convert('RGBA')).astype(int);x0,y0,x1,y1=[v//8 for v in box];cnt={}
    for y in range(s.map.shape[0]):
      for x in range(s.map.shape[1]):cnt[int(s.map[y,x])&1023]=cnt.get(int(s.map[y,x])&1023,0)+1
    shared=0
    for y in range(y0,y1):
      for x in range(x0,x1):
        e=int(s.map[y,x]);i=e&1023;shared+=cnt[i]>1
        sub=a[y*8:y*8+8,x*8:x*8+8];bank=(e>>12)*16 if s.c.bd==4 else 0
        cand=s.P[bank+1:bank+16] if s.c.bd==4 else s.P[1:256]
        v=((sub[:,:,None,:3]-cand[None,None])**2).sum(-1).argmin(-1)+1;v[sub[:,:,3]<128]=0
        if e>>10&1:v=v[:,::-1]
        if e>>11&1:v=v[::-1]
        s.px[i]=v
    return shared
  def save(s):
    f=s.px.reshape(-1)
    for t in range(s.c.ntiles):s.c.put(t,list(f[t*64:(t+1)*64]))
    s.rom.setFileByName(s.cn,bytes(s.c.d))
