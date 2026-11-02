"""한글 ROM 빌드"""
import sys,json,re,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import ndspy.rom,pack,evscript
ROOT=W.parent
SRC=ROOT/'Kimi no Yuusha (Japan).nds';OUT=ROOT/'Kimi no Yuusha (Korean).nds'
rom=ndspy.rom.NintendoDSRom.fromFile(str(SRC))
# ---- 번역 사전 로드
def loadd(p):
  p=W/'trans'/p
  return json.load(open(p,encoding='utf8')) if p.exists() else {}
SCRIPT={}
for p in sorted((W/'trans/script').glob('*.json')) if (W/'trans/script').exists() else []:
  for k,v in json.load(open(p,encoding='utf8')).items():
    if v:SCRIPT[k]=v
SCRIPT.update(loadd('script_test.json'))
ND=loadd('names_data.json')
PP=[('을','를'),('이','가'),('은','는'),('과','와'),('으로','로'),('이랑','랑'),('아','야')]
def josa(t):
  def fix(m):
    w,j=m.group(1),m.group(2)
    c=w[-1];bat=0xac00<=ord(c)<=0xd7a3 and (ord(c)-0xac00)%28
    for a,b in PP:
      if j in(a,b):
        if a=='으로':return w+'{01}'+(b if not bat or (ord(c)-0xac00)%28==8 else a)
        return w+'{01}'+(a if bat else b)
    return m.group(0)
  return re.sub(r'([^{}]+?)\{01\}(으로|이랑|을|를|이|가|은|는|과|와|로|랑|아|야)(?![가-힣])',fix,t)
def unify(ja,ko):
  J=re.findall(r'\{03\}(.*?)\{01\}',ja);K=list(re.finditer(r'\{03\}(.*?)\{01\}',ko))
  if len(J)!=len(K):return ko
  for y,m in reversed(list(zip(J,K))):
    if y in ND:ko=ko[:m.start(1)]+ND[y]+ko[m.end(1):]
  return josa(ko)
for p in sorted((W/'trans/ko').glob('s[0-9][0-9].json')):
  S=json.load(open(W/'trans/src'/p.name,encoding='utf8'));K=json.load(open(p,encoding='utf8'))
  assert len(S)==len(K),p
  for a,b in zip(S,K):
    if b:SCRIPT[a['ja']]=unify(a['ja'],b)
EXTRA=loadd('extra_ko.json')
ENEMY=EXTRA.get('enemy',{})
for _k,_v in EXTRA.get('script_extra',{}).items():SCRIPT.setdefault(_k,_v)
texts=list(SCRIPT.values())+list(ENEMY.values())
# 다른 모듈(데이터/arm9)도 여기에 문자열 제공
import data_patch,arm9_patch
texts+=data_patch.texts()+arm9_patch.texts()
syl=set()
for t in texts:syl|=hangul(t)
E=Enc(syl)
print('syllables',len(syl))
# ---- 폰트
G=bdf(W/'fonts/Galmuri11.bdf')
font=NFTR(rom.getFileByName('_Data/Font/Font.NFTR'))
for ch,code in E.code.items():
  (w,h,xo,yo),rows,dw=G[ord(ch)]
  px=[[0]*font.cw for _ in range(font.ch)]
  top=font.ch-h-yo
  for r,row in enumerate(rows):
    v=int(row,16);nb=len(row)*4
    for x in range(w):
      if v>>(nb-1-x)&1:
        X=x+xo;Y=top+r
        if 0<=X<font.cw and 0<=Y<font.ch:px[Y][X]=1
  i=font.map[code];font.set_glyph(i,px);font.set_width(i,0,11,12)
rom.setFileByName('_Data/Font/Font.NFTR',bytes(font.d))
# ---- 스크립트
warn=[]
def dec_ja(b):
  import extract_dec
  return extract_dec.dec(b)
from extract_dec import dec
nrep=0
for i,f in enumerate(rom.files):
  n=rom.filenames.filenameOf(i)
  if not re.search(r'_Data/(Event|Script)/.*\.dat$',n):continue
  single=False
  try:names,subs=pack.unpack(f)
  except:
    try:
      _c,_p=evscript.parse(f);assert _p==len(f)
      names,subs=['_'],[bytes(f)];single=True
    except:continue
  changed=False;newsubs=[]
  for nm,s in zip(names,subs):
    try:
      cmds,p=evscript.parse(s);assert p==len(s)
    except:
      import rescue
      t=bytearray(s);ch=False
      for o,l,ja in reversed(rescue.find(s)):
        if ja in SCRIPT:
          b=E.enc(SCRIPT[ja])
          if len(b)>255:warn.append(('len>255',n,nm,ja[:20]));continue
          t[o:o+1+l]=bytes([len(b)])+b;ch=True;nrep+=1
      newsubs.append(bytes(t) if ch else s);changed|=ch;continue
    out=bytearray(s[:2]);ch=False
    for op,raw,strs in cmds:
      if not strs:out+=raw;continue
      raw=bytearray(raw);
      # 뒤에서부터 교체(오프셋 유지)
      for (o,l) in reversed(strs):
        ja=dec(bytes(raw[o:o+l]))
        if ja in SCRIPT:
          b=E.enc(SCRIPT[ja])
          if len(b)>255:warn.append(('len>255',n,nm,ja[:20]));continue
          raw[o-1:o+l]=bytes([len(b)])+b;ch=True;nrep+=1
      out+=raw
    newsubs.append(bytes(out) if ch else s);changed|=ch
  if changed:rom.files[i]=newsubs[0] if single else pack.repack(names,newsubs)
print('script strings replaced',nrep)
data_patch.apply(rom,E,warn)
_f='_Data/Town/Dat/DataInfo.dat';_d=bytearray(rom.getFileByName(_f))
for _ja,_ko in EXTRA.get('datainfo',{}).items():
  _ja=_ja.encode('cp932');_p=_d.find(_ja)
  if _p>=0:
    _b=E.enc(_ko);assert len(_b)<=len(_ja)
    _d[_p:_p+len(_ja)]=_b+bytes(len(_ja)-len(_b))
rom.setFileByName(_f,bytes(_d))
for f in ('_Data/Battle/Enemy/Enemy_59_00.dat','_Data/Battle/Enemy/Enemy_66_00.dat'):
  d=bytearray(rom.getFileByName(f))
  for ja,ko in ENEMY.items():
    jb=ja.encode('cp932');p=d.find(jb)
    while p>=0:
      b=E.enc(ko);assert len(b)<=19,ko
      d[p:p+20]=b+bytes(20-len(b));p=d.find(jb,p+1)
  rom.setFileByName(f,bytes(d))
arm9_patch.apply(rom,E,warn)
import gfx_build;gfx_build.apply(rom)
for x in warn[:50]:print('WARN',x)
print('warnings',len(warn))
rom.saveToFile(str(OUT))
print('saved',OUT)
# ---- 배너(게임기 메뉴 제목)
def _crc16(d):
  c=0xFFFF
  for x in d:
    c^=x
    for _ in range(8):c=(c>>1)^0xA001 if c&1 else c>>1
  return c
rom=ndspy.rom.NintendoDSRom.fromFile(str(OUT))
b=bytearray(rom.iconBanner);t='너의 용사\n©SNK PLAYMORE'.encode('utf-16le')
for i in range(6):b[0x240+i*256:0x340+i*256]=t+bytes(256-len(t))
struct.pack_into('<H',b,2,_crc16(b[0x20:0x840]));rom.iconBanner=bytes(b)
rom.saveToFile(str(OUT));print('banner patched')
