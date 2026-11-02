"""그래픽 텍스트 한글화"""
import json,sys,os
import numpy as np,cv2
from PIL import Image,ImageFilter
from pathlib import Path
import gfxpatch as G
W=Path(__file__).resolve().parents[1]
KO=json.load(open(W/'trans/gfx_ko.json',encoding='utf8'))
HV='NanumSquareNeo-eHv.ttf';EB='NanumSquareNeo-dEb.ttf'
def fit(text,maxw,maxh,fname,start,ow):
  for s in range(start,7,-1):
    f=G.font(fname,s);im=G.text_img((400,200),text,f,(0,0,0,255),(0,0,0,255),ow)
    bb=im.getbbox()
    if bb[2]-bb[0]<=maxw and bb[3]-bb[1]<=maxh:return f
  return f
def chapter(rom):
  A=[G.Asset(rom,'_Data/Chapter/ChapterTitleObj_%02d.NCBR'%i) for i in range(25)]
  arr=np.stack([np.array(a.rgba(0)) for a in A]).astype(float)
  lum=0.3*arr[...,0]+0.59*arr[...,1]+0.11*arr[...,2]
  txt=(lum<110)|((arr[...,0]>235)&(arr[...,1]>200))
  a2=arr.copy();a2[txt]=np.nan
  with np.errstate(all='ignore'):med=np.nanmedian(a2,0)
  med=np.where(np.isnan(med),np.median(arr,0),med).astype(np.uint8)
  bg=Image.fromarray(med,'RGBA')
  # 가운데 글자띠 잔여 얼룩 제거
  rgb=bg.convert('RGB');flt=rgb.filter(ImageFilter.MedianFilter(7))
  a=np.array(rgb).astype(int);b=np.array(flt).astype(int)
  m=np.zeros(a.shape[:2],bool);m[22:78,22:178]=True
  m&=np.abs(a-b).sum(-1)>40;a[m]=b[m]
  bg=Image.merge('RGBA',(*Image.fromarray(a.astype(np.uint8)).split(),bg.split()[3]))
  for i,(asset,t) in enumerate(zip(A,KO['chapter'])):
    two='\n' in t
    f=fit(t,158,58 if two else 32,HV,24 if not two else 20,2)
    tx=G.text_img((220,110),t,f,(74,41,24,255),(255,244,214,255),2,lsp=3)
    tx=tx.rotate(9,resample=Image.BICUBIC,center=(110,55))
    al=np.array(tx)[...,3];arr2=np.array(tx);arr2[...,3]=np.where(al>100,255,0);tx=Image.fromarray(arr2)
    out=bg.copy();out.alpha_composite(tx,(-10,-6))
    asset.put(0,out);asset.save()
def subname(rom):
  for i,t in enumerate(KO['subname']):
    a=G.Asset(rom,'_Data/Event/SubNameObj/EventSubOBJ_%02d.NCGR'%i)
    x0,y0,x1,y1=a.bbox(0);w,h=x1-x0,y1-y0;two=chr(10) in t
    im=G.squeeze_text((w,h),t,HV,21 if not two else 20,(255,255,255,255),(90,57,24,255),3,lsp=1)
    a.put(0,im);a.save()
def erase_rows(im,box,sx,ref=None):
  a=np.array(im);x0,y0,x1,y1=box;rf=np.array(ref) if ref is not None else a
  for y in range(y0,y1):a[y,x0:x1]=rf[y,sx]
  return Image.fromarray(a)
def button(rom,name,texts,box,sx,fill,outline,fs,ow=1,fname=HV,cells=None,dx=0,dy=0,ebox=None,ref=None):
  a=G.Asset(rom,name)
  for i,t in zip(cells or range(len(texts)),texts):
    if t is None:continue
    im=erase_rows(a.rgba(i),ebox or box,sx,a.rgba(ref) if ref is not None else None);x0,y0,x1,y1=box
    sub=im.crop((x0,y0,x1,y1))
    sub=G.squeeze_text((x1-x0,y1-y0),t,fname,fs,fill,outline,ow,bg=sub)
    im.paste(sub,(x0+dx,y0+dy));a.put(i,im)
  a.save()
def label(rom,name,cells,texts,fill,outline,fs,ow=1,fname=HV):
  a=G.Asset(rom,name)
  for i,t in zip(cells,texts):
    x0,y0,x1,y1=a.bbox(i)
    a.put(i,G.squeeze_text((x1-x0,y1-y0),t,fname,fs,fill,outline,ow))
  a.save()
def ui(rom):
  for ext in ('NCBR','NCGR'):
    button(rom,'_Data/Title/Obj/TitleObjM.'+ext,KO['title'],(32,7,112,25),30,(255,255,255,255),(0,98,90,255),14,1)
  button(rom,'_Data/Menu/Sprite/SysMenuPartsObject.NCBR',KO['menu'],(44,4,112,20),44,(255,255,255,255),(180,65,0,255),12,1,ebox=(39,4,116,20),ref=1)
  for T in ('_Data/Town/Obj/TownObjCommon.NCBR','_Data/Town/Obj/TownObjCommon.NCGR'):
   WH=(255,255,255,255)
   button(rom,T,KO['town_big'],(46,6,112,26),48,WH,(164,65,0,255),13,1,ref=0,ebox=(42,6,113,26))
   button(rom,T,KO['town_small'],(8,4,72,19),6,WH,(164,65,0,255),12,1,cells=range(7,14),ref=7)
   label(rom,T,[22,23,24],KO['town_label'],(172,57,0,255),WH,13)
  button(rom,'_Data/Town/Obj/TownObjM_Talk.NCBR',[KO['talk']],(38,5,146,20),34,WH,(172,65,0,255),12,1)
G7=str(W/'fonts/Galmuri7.bdf')
def small_put(bm,x0,y,x1,t,fill,outline,mode='side',h=8,left=False):
  n=len(t.replace(' ',''));ex=1 if 9*n+1<=x1-x0 else 0
  im=G.bdftext(t,G7,fill,outline,mode,ex)
  if im.width>x1-x0:im=im.resize((x1-x0,im.height),Image.NEAREST)
  im=im.crop((0,0,im.width,min(im.height,h)))
  out=Image.new('RGBA',(x1-x0,h),(0,0,0,0));out.alpha_composite(im,(0 if left else (x1-x0-im.width)//2,(h-im.height)//2))
  bm.put((x0,y,x1,y+h),out)
def sprites(rom):
  b=G.Bitmap(rom,'_Data/Battle/Sprite/BattleSystemSprite.NCBR')
  for x0,y,x1,t,h in KO['battle_small']:small_put(b,x0,y,x1,t,(255,255,255,255),(82,32,172,255),'full',h)
  b.save()
  m=G.Bitmap(rom,'_Data/Menu/Sprite/SysMenuSprite.NCBR')
  for k,t in enumerate(KO['menu_names']):small_put(m,0,48+8*k,34,t,(255,255,255,255),(49,49,49,255),left=True)
  for k,t in enumerate(KO['menu_labels']):
    m.put((64,48+16*k,96,64+16*k),G.squeeze_text((32,16),t,HV,13,(255,255,255,255),(139,57,8,255),1))
  m.save()
G11=str(W/'fonts/Galmuri11.bdf')
def misc(rom):
  # 필드 상단 캐릭터 이름(작은 글자: 갈무리11)
  a=G.Asset(rom,'_Data/Field/UpScreen/Obj/FieldSymbol.NCGR')
  for i,t in zip(range(14,24),KO['field_names']):
    x0,y0,x1,y1=a.bbox(i);im=G.bdftext(t,G11,(255,255,255,255),(0,0,0,255),'shadow')
    if im.width>x1-x0:im=im.resize((x1-x0,im.height),Image.NEAREST)
    out=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0));out.alpha_composite(im,(0,(y1-y0-im.height)//2));a.put(i,out)
  a.save()
  label(rom,'_Data/HeroDiaryMenu/HeroDiaryTEX.NCBR',[11,12,13,14],KO['diary'],(255,255,255,255),(148,65,0,255),13)
  # 에필로그 이름 띠: 배경은 10개 셀의 중앙값
  a=G.Asset(rom,'_Data/EpilogueList/Obj/CharaName.NCGR')
  bg=np.array(a.rgba(4));bg[:,:31,:3]=(189,98,82);bg=Image.fromarray(bg)
  for i,t in enumerate(KO['epi_names']):
    out=bg.copy();tx=G.squeeze_text((100,24),t,HV,16,(16,16,16,255),(205,164,115,255),1)
    bb=tx.getbbox();out.alpha_composite(tx.crop(bb),(2,(24-(bb[3]-bb[1]))//2));a.put(i,out)
  a.save()
  # 의뢰 상태 마크
  a=G.Asset(rom,'_Data/QuestList/QuestMainTex.NCBR')
  for i,t in zip((8,9,10),KO['quest_mark']):
    im=a.rgba(i);ar=np.array(im);cols=[tuple(int(v) for v in k[:3]) for k,n in __import__('collections').Counter(map(tuple,ar.reshape(-1,4))).most_common(6) if k[3]]
    inner=cols[1]+(255,);light=max(cols,key=sum)+(255,)
    yy,xx=np.mgrid[:24,:24];ar[((yy-11.5)**2+(xx-11.5)**2)<=64]=inner;im=Image.fromarray(ar)
    g=G.bdftext(t,G11,light,None);im.alpha_composite(g,((24-g.width)//2,(24-g.height)//2));a.put(i,im)
  a.save()
  # 메뉴 탭
  a=G.Asset(rom,'_Data/Menu/Obj/WindowObject.NCGR',pal='_Data/Menu/Sprite/SysMenuSprite.NCLR')
  for i,t in enumerate(KO['tabs']):
    im=a.rgba(i);ar=np.array(im)
    dark=__import__('collections').Counter(map(tuple,ar[3:21,18:64].reshape(-1,4))).most_common(1)[0][0]
    im=erase_rows(im,(18,3,66,21),70)
    sub=G.squeeze_text((46,18),t,HV,13,(255,255,255,255),tuple(int(v) for v in dark),1,bg=im.crop((18,3,64,21)))
    im.paste(sub,(18,3));a.put(i,im)
  a.save()
def result(rom):
  b=G.BG(rom,'_Data/BattleResult/Bg/BattleResultBgM.NCGR');im=b.rgba();a=np.array(im)
  for x0,y0,x1,y1,t in KO['result']:
    sub=a[y0:y1,x0:x1];m=((sub[...,0]>235)&(sub[...,1]>235))|(sub[...,0]<20);sub[m]=(90,65,32,255)
  im=Image.fromarray(a)
  for x0,y0,x1,y1,t in KO['result']:
    g=G.bdftext(t,G11,(255,255,255,255),(8,8,8,255));im.alpha_composite(g,(x0-1,y0-3))
  b.put(im,(8,24,112,112));b.save()
BD='NanumSquareNeo-cBd.ttf'
def inpaint(im,mask):
  import cv2
  a=np.array(im);rgb=cv2.inpaint(np.ascontiguousarray(a[...,:3]),mask.astype(np.uint8)*255,3,cv2.INPAINT_TELEA)
  a[...,:3]=rgb;return Image.fromarray(a)
def bgs(rom):
  b=G.BG(rom,'_Data/Town/Bg/TownBgWindowS_Guild.NCGR');im=b.rgba()
  for (box,t) in zip([(24,38,92,50),(24,135,66,148)],KO['guild']):
    im=erase_rows(im,box,18);x0,y0,x1,y1=box
    sub=G.squeeze_text((x1-x0,y1-y0+2),t,HV,12,(255,255,255,255),(148,57,0,255),1,bg=im.crop((x0,y0-1,x1,y1+1)))
    im.paste(sub,(x0,y0-1))
  b.put(im,(0,32,104,152));b.save()
  b=G.BG(rom,'_Data/ChapterEnd/Bg/ChapterEndBgM.NCGR');im=b.rgba();a=np.array(im)
  import cv2
  m=np.zeros(a.shape[:2],np.uint8);m[100:118,78:178]=a[100:118,78:178,:3].sum(-1)<470
  m=cv2.dilate(m,np.ones((3,3),np.uint8))>0
  im=inpaint(im,m)
  tx=G.text_img((100,16),KO['chend_item'],G.font(BD,13),(74,41,16,255));a2=np.array(tx);a2[...,3]=np.where(a2[...,3]>100,255,0)
  im.alpha_composite(Image.fromarray(a2),(78,101))
  b.put(im,(80,96,176,120));b.save()
def chend(rom):
  import cv2
  names=sorted(n for n in (rom.filenames.filenameOf(i) for i in range(len(rom.files))) if n.startswith('_Data/ChapterEnd/Bg/ChapterEndBgS_') and n.endswith('.NCGR'))
  for n in names:
    xx=int(n.split('_')[-2]);t=KO['chapter_end'][xx] if 'chapter_end' in KO else KO['chapter'][min(xx,23)]
    b=G.BG(rom,n);im=b.rgba();a=np.array(im)
    lum=a[...,:3].astype(int).sum(-1)
    wm=np.zeros(lum.shape,np.uint8);wm[76:190]=(lum[76:190]>705)&(a[76:190,:,2]>215)
    # 작은 하이라이트 제거: 글자 덩어리만
    base=wm.copy();thr=480 if any(k in n for k in ('01_01','03_01','05_01','19_02')) else 330
    dark=(lum<thr).astype(np.uint8);wm=base&cv2.dilate(dark,np.ones((5,5),np.uint8))
    nb,lab,st,_=cv2.connectedComponentsWithStats(cv2.dilate(wm,np.ones((3,9),np.uint8)))
    keep=np.zeros_like(wm);band=[]
    for k in range(1,nb):
      if st[k,2]>=40 and st[k,3]<=40:keep[lab==k]=1;band.append((st[k,1],st[k,1]+st[k,3]))
    for k in range(1,nb):
      if band and st[k,3]<=40 and any(st[k,1]>=a-4 and st[k,1]+st[k,3]<=b+4 for a,b in band):keep[lab==k]=1
    wm&=keep
    MAN={'03_01':(40,104,220,164),'01_01':(8,86,252,176),'05_01':(34,116,226,162),'19_02':(40,84,242,180)}
    for k,(x0,y0,x1,y1) in MAN.items():
      if k in n:wm=np.zeros_like(base);wm[y0:y1,x0:x1]=lum[y0:y1,x0:x1]>690
    ys,xs=np.where(wm)
    if len(ys)<30:print('no text?',n);continue
    y0,y1=ys.min(),ys.max()
    m=cv2.dilate(wm,np.ones((7,7),np.uint8))>0
    im=inpaint(im,m)
    one=t.replace(chr(10),' ');f=G.font(HV,21)
    tw=im.getbbox() and G.text_img((600,40),one,f,(0,0,0,255)).getbbox()
    txt=one if tw[2]-tw[0]<=236 else t
    two=chr(10) in txt;H=(y1-y0+10)
    tx=G.text_img((256,max(H,50 if two else 30)),txt,f,(255,255,255,255),(120,60,20,255),2,lsp=6)
    bb=tx.getbbox();tx=tx.crop(bb)
    if tx.width>244:tx=tx.resize((244,tx.height),Image.LANCZOS)
    ar=np.array(tx);ar[...,3]=np.where(ar[...,3]>110,255,0);tx=Image.fromarray(ar)
    cy=max((y0+y1)//2,150) if not two else (y0+y1)//2;im.alpha_composite(tx,((256-tx.width)//2,max(0,min(191-tx.height,cy-tx.height//2))))
    b.put(im,(0,72,256,192));b.save()
def wrap(t,fontf,maxw):
  out=[]
  for para in t.split(chr(10)):
    line=''
    for w in para.split(' '):
      cand=(line+' '+w) if line else w
      if G.bdftext(cand,fontf,(0,0,0,255),None).width-2<=maxw:line=cand;continue
      if line:out.append(line);line=''
      while G.bdftext(w,fontf,(0,0,0,255),None).width-2>maxw:
        k=len(w)
        while G.bdftext(w[:k],fontf,(0,0,0,255),None).width-2>maxw:k-=1
        out.append(w[:k]);w=w[k:]
      line=w
    out.append(line)
  return out
def diary(rom):
  import glob
  D={}
  for f in glob.glob(str(W/'trans/diary/*.json')):D.update({k:v['ko'] for k,v in json.load(open(f,encoding='utf8')).items()})
  CREAM=(255,222,156,255);LINE=(172,115,74,255);INK=(106,41,16,255)
  for k,t in sorted(D.items()):
    a=G.Asset(rom,'_Data/StoryPiece/Diary/StoryPieceDiary_%s.NCBR'%k);im=a.rgba(0);ar=np.array(im)
    ar[14:148,11:197]=CREAM;im=Image.fromarray(ar)
    for fontf,pitch,top,nl in ((G11,13,15,10),(str(W/'fonts/Galmuri9.bdf'),11,15,12)):
      lines=wrap(t,fontf,182)
      if len(lines)<=nl:break
    else:print('diary overflow',k,len(lines))
    d=__import__('PIL.ImageDraw',fromlist=['x']).Draw(im)
    for i in range(nl):d.line([(12,top+i*pitch+pitch-1),(195,top+i*pitch+pitch-1)],fill=LINE)
    for i,l in enumerate(lines[:nl]):
      if l:g=G.bdftext(l,fontf,INK,None,crop=False);im.alpha_composite(g,(11,top+i*pitch-3))
    a.put(0,im);a.save()
def apply(rom):
  chapnum(rom)
  backup(rom)
  statlabels(rom)
  logo(rom)
  import tutor;tutor.apply(rom)
  diary(rom)
  chend(rom)
  bgs(rom)
  result(rom)
  misc(rom)
  sprites(rom)
  chapter(rom);subname(rom);ui(rom)
  print('gfx patched')
if __name__=='__main__':
  import ndspy.rom
  r=ndspy.rom.NintendoDSRom.fromFile(str(W.parent/'Kimi no Yuusha (Japan).nds'))
  diary(r);import glob
  ks=sorted(os.path.basename(f)[:-4] for f in glob.glob(str(W/'diary_img/*.png')))
  S=Image.new('RGB',(208*6,160*11))
  for i,k in enumerate(ks):im=G.Asset(r,'_Data/StoryPiece/Diary/StoryPieceDiary_%s.NCBR'%k).rgba(0);S.paste(im,(i%6*208,i//6*160),im)
  S.save(W/'gcell/_diaall.png');sys.exit()
  chend(r)
  import preview
  ns=sorted(n for n in (r.filenames.filenameOf(i) for i in range(len(r.files))) if n.startswith('_Data/ChapterEnd/Bg/ChapterEndBgS_') and n.endswith('.NCGR'))
  ims=[G.BG(r,n).rgba() for n in ns];S=Image.new('RGB',(256*5,192*8))
  for k,i in enumerate(ims):S.paste(i,(k%5*256,k//5*192))
  S.save(W/'gcell/_cebs.png');sys.exit()
  bgs(r);G.BG(r,'_Data/Town/Bg/TownBgWindowS_Guild.NCGR').rgba().resize((512,384),0).save(W/'gcell/_guko.png');G.BG(r,'_Data/ChapterEnd/Bg/ChapterEndBgM.NCGR').rgba().resize((512,384),0).save(W/'gcell/_ceko.png');sys.exit()
  result(r);G.BG(r,'_Data/BattleResult/Bg/BattleResultBgM.NCGR').rgba().resize((512,384),0).save(W/'gcell/_resko.png')
  misc(r)
  for n,c,fn in [('_Data/Field/UpScreen/Obj/FieldSymbol.NCGR',range(14,24),'_fsko.png'),('_Data/HeroDiaryMenu/HeroDiaryTEX.NCBR',range(11,15),'_hdko.png'),('_Data/EpilogueList/Obj/CharaName.NCGR',range(10),'_epko.png'),('_Data/QuestList/QuestMainTex.NCBR',range(8,11),'_qko.png')]:
    a=G.Asset(r,n);ims=[a.rgba(i) for i in c];S=Image.new('RGB',(max(i.width for i in ims),sum(i.height+2 for i in ims)),(0,90,0));y=0
    for i in ims:S.paste(i,(0,y),i);y+=i.height+2
    S.resize((S.width*3,S.height*3),0).save(W/'gcell'/fn)
  a=G.Asset(r,'_Data/Menu/Obj/WindowObject.NCGR',pal='_Data/Menu/Sprite/SysMenuSprite.NCLR');ims=[a.rgba(i) for i in range(5)];S=Image.new('RGB',(112,130),(0,90,0))
  for k,i in enumerate(ims):S.paste(i,(0,k*26),i)
  S.resize((336,390),0).save(W/'gcell/_woko.png')
  sys.exit()
  sprites(r)
  for n,o in [('_Data/Battle/Sprite/BattleSystemSprite','_bs'),('_Data/Menu/Sprite/SysMenuSprite','_ms')]:
    b=G.Bitmap(r,n+'.NCBR');b.rgba((0,0,256,176)).resize((1536,1056),0).save(W/'gcell'/(o+'.png'))
  sys.exit()
  ui(r)
  for n,c,fn in [('_Data/Title/Obj/TitleObjM.NCBR',4,'_tko.png'),('_Data/Menu/Sprite/SysMenuPartsObject.NCBR',9,'_mko.png'),('_Data/Town/Obj/TownObjCommon.NCBR',30,'_townko.png'),('_Data/Town/Obj/TownObjM_Talk.NCBR',1,'_talkko.png')]:
    a=G.Asset(r,n);ims=[a.rgba(i) for i in range(c)];S=Image.new("RGB",(max(i.width for i in ims),sum(i.height+2 for i in ims)),(0,90,0));y=0
    for i in ims:S.paste(i,(0,y),i);y+=i.height+2
    S.resize((S.width*3,S.height*3),0).save(W/'gcell'/fn)
  sys.exit()
  from PIL import Image
  ims=[G.Asset(r,'_Data/Chapter/ChapterTitleObj_%02d.NCBR'%i).rgba(0) for i in range(25)]
  S=Image.new('RGB',(800,700),(0,90,0))
  for k,i in enumerate(ims):S.paste(i,(k%4*200,k//4*100),i)
  S.save(W/'gcell/_chko.png')
  ims=[G.Asset(r,'_Data/Event/SubNameObj/EventSubOBJ_%02d.NCGR'%i).rgba(0) for i in range(55)]
  S=Image.new('RGB',(960,1120),(0,90,0))
  for k,i in enumerate(ims):S.paste(i,(k%4*240,k//4*80),i)
  S.save(W/'gcell/_subko.png')
def _retext(im,box,t,size,fill=(84,44,20,255),outline=(255,236,200,255),ow=2,thr=None):
  """box 안 글자(진한 갈색+밝은 테두리)를 지우고 t를 다시 그린다"""
  a=np.array(im);x0,y0,x1,y1=box
  sub=a[y0:y1,x0:x1,:3].astype(int);al=a[y0:y1,x0:x1,3]
  lum=sub@[0.3,0.59,0.11]
  m=((lum<120)|(lum>215))&(al>0)
  m=cv2.dilate(m.astype(np.uint8),np.ones((3,3),np.uint8))
  rgb=cv2.inpaint(np.ascontiguousarray(a[y0:y1,x0:x1,:3]),m,3,cv2.INPAINT_TELEA)
  a[y0:y1,x0:x1,:3]=rgb;out=Image.fromarray(a)
  f=fit(t,x1-x0-2,y1-y0-2,HV,size,1)
  tx=G.text_img((x1-x0+8,y1-y0+8),t,f,fill,outline,ow)
  al2=np.array(tx);al2[...,3]=np.where(al2[...,3]>100,255,0);tx=Image.fromarray(al2)
  lay=Image.new('RGBA',out.size);lay.alpha_composite(tx,(x0-4,y0-4))
  la=np.array(lay);oa=np.array(out);msk=(la[...,3]>0)&(oa[...,3]>0)
  oa[msk]=la[msk];return Image.fromarray(oa)
def chapnum(rom):
  a=G.Asset(rom,'_Data/Chapter/ChapterMainObj.NCGR')
  for i,t,sz in((18,'제',17),(19,'최종',20)):
    im=a.rgba(i);w,h=im.size
    f=fit(t,w-2,h-2,HV,sz,1)
    tx=G.text_img((w,h),t,f,(84,44,20,255),(255,236,200,255),2)
    q=np.array(tx);q[...,3]=np.where(q[...,3]>100,255,0);a.put(i,Image.fromarray(q))
  a.put(7,_retext(a.rgba(7),(141,15,163,39),'화',20))
  a.save()
def _plate(im,t,fill,outline,sz,ow=2,align_left=True):
  w,h=im.size;f=fit(t,w-2,h,HV,sz,ow)
  tx=G.text_img((w,h),t,f,fill,outline,ow)
  q=np.array(tx);al=q[...,3]
  if align_left:
    xs=np.where(al.max(0)>100)[0]
    if len(xs):q=np.roll(q,-xs[0],1)
  q[...,3]=np.where(q[...,3]>100,255,0);return Image.fromarray(q)
def backup(rom):
  a=G.Asset(rom,'_Data/Backup/Sprite/BackupBgDown.NCBR')
  for i,t in((1,'세이브'),(2,'로드')):a.put(i,_plate(a.rgba(i),t,(255,255,255,255),(110,52,18,255),13))
  a.save()
def _tilewrite(c,x0,y0,w,h,im,cmap,cols=32):
  """4/8bpp 타일 시트(2D) 영역을 지우고 im(RGBA)을 cmap{rgb:index}로 기록"""
  a=np.array(im)
  for y in range(y0,y0+h):
    for x in range(x0,x0+w):
      t=(y//8)*cols+x//8;px=c.tile(t);k=(y%8)*8+x%8
      yy,xx=y-y0,x-x0;v=0
      if yy<a.shape[0] and xx<a.shape[1] and a[yy,xx,3]>0:v=cmap[tuple(a[yy,xx,:3])]
      px[k]=v;c.put(t,px)
def statlabels(rom):
  n='_Data/Menu/Bg/SysMenuBgStr.NCGR';c=G.gfx.Char(rom.getFileByName(n)) if hasattr(G,'gfx') else None
  import gfx;c=gfx.Char(rom.getFileByName(n))
  for k,t in enumerate(['힘','지혜','수비','마음','민첩','재주','운']):
    im=G.bdftext(t,str(W/'fonts/Galmuri11.bdf'),(255,255,255,255),(0,0,0,255),'shadow',crop=False)
    _tilewrite(c,208,32+16*k,48,16,im.crop((0,0,48,16)) if im.height>=16 else im,{(255,255,255):15,(0,0,0):9})
  rom.setFileByName(n,bytes(c.d))
def logo(rom):
  RED=(238,48,90,255);NV=(28,48,108,255);WH=(255,255,255,255)
  def neo():
    f=G.font(HV,64);im=G.text_img((90,110),'너',f,RED,NV,3)
    q=np.array(im);q[...,3]=np.where(q[...,3]>110,255,0);return Image.fromarray(q)
  for ext in('NCBR','NCGR'):
    a=G.Asset(rom,'_Data/Title/Obj/TitleObjS_Logo.'+ext)
    im=np.array(a.rgba(0));im[0:96,0:48]=0;im[14:72,46:196]=0
    out=Image.fromarray(im)
    f=G.font(HV,42);tx=G.text_img((170,64),'의용사',f,WH,NV,3)
    q=np.array(tx);q[...,3]=np.where(q[...,3]>110,255,0);tx=Image.fromarray(q)
    bb=tx.getbbox();tx=tx.crop(bb)
    out.alpha_composite(tx,(48+(146-tx.width)//2,max(12,71-tx.height)))
    n=neo();nb=n.getbbox();n=n.crop(nb)
    out.alpha_composite(n,(max(0,(50-n.width)//2),(96-n.height)//2))
    a.put(0,out)
    c1=Image.new('RGBA',a.rgba(1).size);c1.alpha_composite(n,(max(0,(50-n.width)//2),(96-n.height)//2));a.put(1,c1)
    a.save()
