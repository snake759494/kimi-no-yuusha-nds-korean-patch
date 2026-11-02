"""데이터 파일(아이템·적·지명·의뢰 등) 문자열 교체"""
import json,struct
from pathlib import Path
import datafmt
from extract_dec import dec
W=Path(__file__).resolve().parents[1]
def _pairs(name):
  s=W/'trans/src'/(name+'.json');k=W/'trans/ko'/(name+'.json')
  if not k.exists():return {}
  S=json.load(open(s,encoding='utf8'));K=json.load(open(k,encoding='utf8'))
  if len(S)!=len(K):print('WARN 개수 불일치',name);return {}
  return {a['ja']:b for a,b in zip(S,K) if b}
D={}
D.update(_pairs('data_names'));D.update(_pairs('data_descs'))
D.update(json.load(open(W/'trans/extra_ko.json',encoding='utf8')).get('datainfo',{}))
CN=json.load(open(W/'trans/names.json',encoding='utf8'))
def lookup(f,ja):
  if f.endswith('CharaName.dat'):return CN.get(ja)
  return D.get(ja) or CN.get(ja)
def texts():return list(D.values())+list(CN.values())
def apply(rom,E,warn):
  n_rep=0
  for f in datafmt.SEQ16+datafmt.SEQ8+list(datafmt.FIXED):
    d=bytearray(rom.getFileByName(f))
    strs=datafmt.strings(f,d)
    if f in datafmt.FIXED:
      for p,l,pre in strs:
        ko=lookup(f,dec(bytes(d[p:p+l])))
        if ko is None:continue
        b=E.enc(ko);cap=-pre
        if len(b)>cap-1:warn.append(('data cap',f,ko));b=b[:cap-1]
        d[p:p+cap]=b+bytes(cap-len(b));n_rep+=1
      rom.setFileByName(f,bytes(d))
    else:
      out=bytearray();last=0
      for p,l,pre in strs:
        off=p+pre;ja=dec(bytes(d[off:off+l]));ko=lookup(f,ja)
        out+=d[last:p]
        if ko is None:out+=d[p:off+l]
        else:
          b=E.enc(ko)
          if pre==1:
            if len(b)>255:warn.append(('u8 len',f,ko));b=b[:255]
            out+=bytes([len(b)])+b
          else:out+=struct.pack('<H',len(b))+b
          n_rep+=1
        last=off+l
      out+=d[last:]
      rom.setFileByName(f,bytes(out))
  print('data strings replaced',n_rep)
