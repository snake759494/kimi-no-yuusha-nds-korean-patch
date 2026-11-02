"""NCGR/NCBR/NCLR/NSCR 간이 파서·렌더러"""
import struct
from PIL import Image
def sect(d,magic):
  p=struct.unpack_from('<H',d,12)[0]
  while p<len(d):
    m=d[p:p+4];sz=struct.unpack_from('<I',d,p+4)[0]
    if m==magic:return p
    p+=sz
def pal(d):
  p=sect(d,b'TTLP');bd,_,sz,off=struct.unpack_from('<IIII',d,p+8)
  raw=d[p+8+off:p+8+off+sz];c=[]
  for i in range(0,len(raw),2):
    v=struct.unpack_from('<H',raw,i)[0];c.append(((v&31)*255//31,(v>>5&31)*255//31,(v>>10&31)*255//31))
  return c
class Char:
  def __init__(s,d):
    s.d=bytearray(d);p=sect(d,b'RAHC');s.p=p
    s.th,s.tw,s.bpp,s.map,s.lin,s.size,s.off=struct.unpack_from('<HHIIIII',d,p+8)
    s.bd=4 if s.bpp==3 else 8;s.data=p+8+s.off
    s.ntiles=s.size*8//s.bd//64
  def tile(s,i):
    b=s.d[s.data+i*8*s.bd:s.data+(i+1)*8*s.bd]
    if s.bd==8:return list(b)
    o=[]
    for x in b:o+=[x&15,x>>4]
    return o
  def put(s,i,px):
    if s.bd==8:b=bytes(px)
    else:b=bytes(px[k]|px[k+1]<<4 for k in range(0,64,2))
    s.d[s.data+i*8*s.bd:s.data+(i+1)*8*s.bd]=b
def sheet(c,P,pb=0,cols=32):
  n=c.ntiles;rows=(n+cols-1)//cols
  im=Image.new('RGB',(cols*8,rows*8),(255,0,255))
  for i in range(n):
    t=c.tile(i)
    for k,v in enumerate(t):
      col=P[(pb*16+v)%len(P)] if c.bd==4 else P[v%len(P)]
      im.putpixel((i%cols*8+k%8,i//cols*8+k//8),col)
  return im
def bitmap(c,P,pb=0,w=None):
  w=w or c.tw*8;n=c.size*8//c.bd;h=(n+w-1)//w
  im=Image.new('RGB',(w,h),(255,0,255))
  px=[]
  for i in range(c.ntiles):px+=c.tile(i)
  for k,v in enumerate(px):
    im.putpixel((k%w,k//w),P[(pb*16+v)%len(P)] if c.bd==4 else P[v%len(P)])
  return im
SZ={(0,0):(8,8),(0,1):(16,16),(0,2):(32,32),(0,3):(64,64),(1,0):(16,8),(1,1):(32,8),(1,2):(32,16),(1,3):(64,32),(2,0):(8,16),(2,1):(8,32),(2,2):(16,32),(2,3):(32,64)}
def cells(d):
  p=sect(d,b'KBEC');n,attr,co,mp=struct.unpack_from('<HHII',d,p+8)
  base=p+8+co;es=16 if attr&1 else 8;oamb=base+n*es;out=[]
  for i in range(n):
    no,ca,oo=struct.unpack_from('<HHI',d,base+i*es);objs=[]
    for k in range(no):
      a0,a1,a2=struct.unpack_from('<HHH',d,oamb+oo+k*6)
      y=a0&255;y=y-256 if y>=128 else y;x=a1&511;x=x-512 if x>=256 else x
      w,h=SZ[(a0>>14,a1>>14)]
      objs.append(dict(x=x,y=y,w=w,h=h,t=a2&1023,pal=a2>>12,hf=a1>>12&1,vf=a1>>13&1,c8=a0>>13&1))
    out.append(objs)
  return out,mp&0xff
def objpix(c,o,shift):
  """OBJ 하나의 픽셀 배열과 (char data 내 픽셀 인덱스 목록) 반환"""
  w,h=o['w'],o['h'];start=o['t']<<shift  # 32B 타일 단위
  start_px=start*64 if c.bd==4 else start*32
  idx=[]
  for yy in range(h):
    for xx in range(w):
      if c.lin:k=start_px+yy*w+xx
      else:k=start_px+((yy//8)*(w//8)+xx//8)*64+(yy%8)*8+xx%8
      idx.append(k)
  return idx
def allpix(c):
  px=[]
  for i in range(c.ntiles):px+=c.tile(i)
  return px
def render_cell(c,objs,P,shift,px=None):
  px=px or allpix(c)
  if not objs:return None,(0,0)
  x0=min(o['x'] for o in objs);y0=min(o['y'] for o in objs)
  x1=max(o['x']+o['w'] for o in objs);y1=max(o['y']+o['h'] for o in objs)
  im=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0))
  for o in reversed(objs):
    idx=objpix(c,o,shift)
    for n,k in enumerate(idx):
      if k>=len(px):continue
      v=px[k]
      if v==0:continue
      xx=n%o['w'];yy=n//o['w']
      if o['hf']:xx=o['w']-1-xx
      if o['vf']:yy=o['h']-1-yy
      col=P[(o['pal']*16+v)%len(P)] if c.bd==4 else P[v%len(P)]
      im.putpixel((o['x']-x0+xx,o['y']-y0+yy),col+(255,))
  return im,(x0,y0)
