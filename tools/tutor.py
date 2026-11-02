"""튜토리얼 상단 그림(EventSubBG_xx) 일본어 → 한국어 교체
spec: trans/tutor_ko.json  {"01":[[x0,y0,x1,y1,"텍스트","스타일",옵션{}],...]}
스타일
  w  : 밝은 글자(흰/노랑 등)+검은 그림자, 갈무리11, 왼쪽 정렬
  d  : 어두운 글자(밝은 바탕), 갈무리11, 왼쪽 정렬
  D  : 어두운 큰 글자, 나눔스퀘어 cBd, 가운데 정렬 (opt size)
  T  : 큰 제목(파랑/보라 테두리), 나눔스퀘어 eHv
"""
import json,os,sys
import numpy as np,cv2
from PIL import Image
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import gfxpatch as G
from pathlib import Path
W=Path(__file__).resolve().parents[1];ROOT=W.parent
GAL=str(W/'fonts/Galmuri11.bdf');GAL9=str(W/'fonts/Galmuri9.bdf')
HV='NanumSquareNeo-eHv.ttf';BD='NanumSquareNeo-cBd.ttf'
def lum(a):return a[...,0]*0.3+a[...,1]*0.59+a[...,2]*0.11
def inpaint(a,m,r=3):
  a[...,:3]=cv2.inpaint(np.ascontiguousarray(a[...,:3]),m.astype(np.uint8),r,cv2.INPAINT_TELEA);return a
def fitfont(t,fname,size,maxw,maxh):
  for s in range(size,7,-1):
    f=G.font(fname,s);b=f.getbbox(t)
    if b[2]-b[0]<=maxw and b[3]-b[1]<=maxh:return f
  return G.font(fname,8)
def paste(a,img,x,y):
  b=np.array(img);h,w=b.shape[:2]
  x0,y0=max(x,0),max(y,0);x1,y1=min(x+w,a.shape[1]),min(y+h,a.shape[0])
  if x1<=x0 or y1<=y0:return
  s=b[y0-y:y1-y,x0-x:x1-x];m=s[...,3]>100
  a[y0:y1,x0:x1][m]=s[m]
def bdf(t,fill,shadow,small=False,maxw=999):
  im=G.bdftext(t,GAL,fill,shadow,'shadow' if shadow else 'shadow')
  if im.width>maxw or small:im=G.bdftext(t,GAL9,fill,shadow,'shadow')
  if im.width>maxw:
    im=im.resize((maxw,im.height),Image.NEAREST)
  return im
DONE={}
def entry(a,e):
  x0,y0,x1,y1,t,st=e[:6];o=e[6] if len(e)>6 else {}
  if st=='copy':
    a[y0:y1,x0:x1]=DONE[t][y0:y1,x0:x1];return
  sub=a[y0:y1,x0:x1].astype(float);L=lum(sub[...,:3])
  bgL=np.median(L)
  if st in('w','d'):
    if st=='w':m=(L>o.get('thr',175))
    else:m=(L<bgL-o.get('thr',60))
    ys,xs=np.where(m)
    if len(xs)==0:print('  no text',e);return
    tx,ty=xs.min(),ys.min();th=ys.max()-ys.min()+1
    fill=tuple(int(v) for v in np.median(sub[m][:,:3],0))+(255,)
    if 'fill' in o:fill=tuple(o['fill'])+(255,)
    mm=cv2.dilate(m.astype(np.uint8),np.ones((3,3),np.uint8),iterations=o.get('dil',1))
    if o.get('solid'):
      reg=a[y0:y1,x0:x1].copy();bgc=np.median(reg[mm==0][:,:3],0) if (mm==0).any() else reg[0,0,:3]
      for yy in range(reg.shape[0]):
        row=reg[yy];rm=mm[yy]==0
        c=np.median(row[rm][:,:3],0) if rm.sum()>3 else bgc
        row[mm[yy]>0,:3]=c
      a[y0:y1,x0:x1]=reg
    else:
      reg=a[y0:y1,x0:x1].copy();inpaint(reg,mm);a[y0:y1,x0:x1]=reg
    if t and chr(10) in t:
      sh=(0,0,0,255) if st=='w' and not o.get('nosh') else None
      if 'sh' in o:sh=tuple(o['sh'])+(255,)
      for i,l in enumerate(t.split(chr(10))):
        im=bdf(l,fill,sh,o.get('small',False),maxw=x1-x0-tx)
        paste(a,im,x0+tx,y0+ty+i*o.get('lh',16)+o.get('dy',0))
    elif t:
      sh=(0,0,0,255) if st=='w' and not o.get('nosh') else None
      if 'sh' in o:sh=tuple(o['sh'])+(255,)
      im=bdf(t,fill,sh,o.get('small',False),maxw=o.get('maxw',x1-x0-(tx if o.get('al','l')=='l' else 0)))
      if o.get('al','l')=='c':px=x0+(x1-x0-im.width)//2
      elif o.get('al')=='r':px=x0+xs.max()+2-im.width
      else:px=x0+tx-o.get('dx',0)
      py=y0+ty+(th-im.height)//2+o.get('dy',0)
      paste(a,im,px,py)
  elif st=='D':
    m=(L<bgL-o.get('thr',50))
    fill=tuple(int(v) for v in np.median(sub[m][:,:3],0))+(255,) if m.any() else (90,60,30,255)
    if 'fill' in o:fill=tuple(o['fill'])+(255,)
    mm=cv2.dilate(m.astype(np.uint8),np.ones((3,3),np.uint8),iterations=o.get('dil',1))
    reg=a[y0:y1,x0:x1].copy();inpaint(reg,mm);a[y0:y1,x0:x1]=reg
    f=fitfont(t,o.get('font',BD),o.get('size',14),x1-x0-2,y1-y0)
    cy=(y1-y0)/2
    if m.any() and not o.get('boxc'):
      ys,xs=np.where(m);cy=(ys.min()+ys.max())/2
    im=G.text_img((x1-x0+8,y1-y0+8),t,f,fill,tuple(o['ol'])+(255,) if 'ol' in o else None,o.get('ow',1))
    q=np.array(im);q[...,3]=np.where(q[...,3]>110,255,0)
    al=q[...,3].max(1);yy=np.where(al>0)[0];tcy=(yy.min()+yy.max())/2 if len(yy) else (y1-y0+8)/2
    paste(a,Image.fromarray(q),x0-4+o.get('dx',0),int(round(y0+cy-tcy))+o.get('dy',0))
  elif st=='T':
    # 제목 글자: 파랑/보라/흰 강조 픽셀
    r,g,b=sub[...,0],sub[...,1],sub[...,2]
    blue=((b>r+25)&(b>g+10)) if o.get('col')!='pink' else ((r>b+20)&(r>g+40))
    near=cv2.dilate(blue.astype(np.uint8),np.ones((5,5),np.uint8))>0
    m=blue|((L>225)&near)
    if 'mask' in o and o['mask']=='all':m=np.ones_like(m)
    if 'base' not in o:
      mm=cv2.dilate(m.astype(np.uint8),np.ones((3,3),np.uint8),iterations=o.get('dil',2))
      reg=a[y0:y1,x0:x1].copy();inpaint(reg,mm,5);a[y0:y1,x0:x1]=reg
    f=fitfont(t,HV,o.get('size',24),x1-x0-10,y1-y0-2)
    w,h=x1-x0+12,y1-y0+12
    im=G.text_img((w,h),t,f,(250,250,255,255),(88,60,220,255) if o.get('col')!='pink' else (220,40,110,255),2)
    im2=G.text_img((w,h),t,f,(0,0,0,0),(255,255,255,255),3)
    base=Image.new('RGBA',(w,h));base.alpha_composite(im2);base.alpha_composite(im)
    q0=np.array(base)[...,3].max(0);xs0=np.where(q0>0)[0]
    if len(xs0) and not o.get('center'):base=Image.fromarray(np.roll(np.array(base),-(xs0[0]-4),1))
    base=base.transform(base.size,Image.AFFINE,(1,0.22,-0.22*h/2,0,1,0),Image.BICUBIC)
    q=np.array(base);q[...,3]=np.where(q[...,3]>110,255,0)
    paste(a,Image.fromarray(q),x0-6+o.get('dx',0),y0-6+o.get('dy',0))
def apply(rom,only=None):
  S=json.load(open(W/'trans/tutor_ko.json',encoding='utf8'))
  for k,es in S.items():
    if only and k not in only:continue
    n='_Data/Event/SubBg/EventSubBG_%s.NCGR'%k
    bg=G.BG(rom,n);a=np.array(bg.rgba())
    for e in es:entry(a,e)
    DONE[k]=a.copy()
    bg.put(Image.fromarray(a),(0,0,256,192));bg.save()
if __name__=='__main__':
  import ndspy.rom
  r=ndspy.rom.NintendoDSRom.fromFile(str(ROOT/'Kimi no Yuusha (Japan).nds'))
  ks=sys.argv[1:];apply(r)
  ims=[]
  for k in ks:
    o=G.BG(ndspy.rom.NintendoDSRom.fromFile(str(ROOT/'Kimi no Yuusha (Japan).nds')),'_Data/Event/SubBg/EventSubBG_%s.NCGR'%k).rgba()
    n=G.BG(r,'_Data/Event/SubBg/EventSubBG_%s.NCGR'%k).rgba()
    ims+=[o,n]
  S=Image.new('RGB',(512,192*len(ks)))
  for i,im in enumerate(ims):S.paste(im,((i%2)*256,(i//2)*192),im)
  S.resize((S.width*2,S.height*2),0).save(str(W/'gview/tut.png'))
