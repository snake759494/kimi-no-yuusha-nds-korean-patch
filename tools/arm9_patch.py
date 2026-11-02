"""ARM9 내 UI 문자열 제자리 교체(원래 슬롯 크기 이내)"""
import json
from pathlib import Path
from extract_dec import dec
W=Path(__file__).resolve().parents[1]
KO={int(k,16):v for k,v in json.load(open(W/'trans/arm9_ko.json',encoding='utf8')).items()}
SRC={e['off']:e for e in json.load(open(W/'ext/arm9_strings.json',encoding='utf8'))}
def texts():return list(KO.values())
def apply(rom,E,warn):
  a=bytearray(rom.arm9);n=0
  for off,ko in KO.items():
    e=SRC[off];old=a[off:off+e['cap']]
    assert dec(bytes(old).split(b'\0')[0])==e['ja'],hex(off)
    b=E.enc(ko)
    if len(b)>e['cap']-1:warn.append(('arm9 cap',hex(off),ko,len(b),e['cap']));continue
    a[off:off+e['cap']]=b+bytes(e['cap']-len(b));n+=1
  rom.arm9=bytes(a)
  print('arm9 strings replaced',n)
