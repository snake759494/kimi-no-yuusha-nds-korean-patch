"""공통: 한글 인코딩 테이블, 문자열 인코딩, 폭 계산"""
import re,json,sys
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'tools'))
from nftr import NFTR
FONT0=NFTR(open(W/'ext/Font.NFTR','rb').read())
SLOTS=sorted(c for c in FONT0.map if c>=0x889F)
TOK=re.compile(r'\{(c?)([0-9a-f]{2})\}|\n|.',re.S)
class Enc:
  def __init__(s,syllables):
    syl=sorted(syllables)
    assert len(syl)<=len(SLOTS),(len(syl),len(SLOTS))
    s.code={ch:SLOTS[i] for i,ch in enumerate(syl)}
  def enc(s,t):
    out=bytearray()
    for m in TOK.finditer(t):
      g=m.group()
      if m.group(2):
        if m.group(1):out.append(int(m.group(2),16))
        else:out+=bytes([0x1b,int(m.group(2),16)])
      elif g=='\n':out.append(0x0a)
      elif g in s.code:out+=s.code[g].to_bytes(2,'big')
      else:out+=g.encode('cp932')
    return bytes(out)
def hangul(t):return {c for c in t if '\uac00'<=c<='\ud7a3'}
def width(line,enc=None):
  w=0
  for m in TOK.finditer(line):
    g=m.group()
    if m.group(2) or g=='\n':continue
    if '\uac00'<=g<='\ud7a3':w+=12;continue
    c=int.from_bytes(g.encode('cp932'),'big');w+=FONT0.width(FONT0.map.get(c,0))[2]
  return w
def bdf(path):
  g={};cur=None;lines=open(path,encoding='utf8').read().splitlines();i=0
  while i<len(lines):
    l=lines[i]
    if l.startswith('ENCODING'):cur=int(l.split()[1])
    elif l.startswith('BBX'):bbx=list(map(int,l.split()[1:]))
    elif l.startswith('DWIDTH'):dw=int(l.split()[1])
    elif l=='BITMAP':
      rows=[];i+=1
      while lines[i]!='ENDCHAR':rows.append(lines[i]);i+=1
      g[cur]=(bbx,rows,dw)
    i+=1
  return g
