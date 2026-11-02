"""파서 실패 하위스크립트: 길이접두 SJIS 문자열 휴리스틱 탐지"""
import re
from extract_dec import dec
JP=re.compile(r'[\u3040-\u30ff\u4e00-\u9fff]')
def valid(b):
  i=0
  while i<len(b):
    c=b[i]
    if c in(0x0a,):i+=1;continue
    if c==0x1b:i+=2;continue
    if 0x20<=c<0x7f or 0xa1<=c<=0xdf:i+=1;continue
    if 0x81<=c<=0x9f or 0xe0<=c<=0xfc:
      if i+1>=len(b) or not(0x40<=b[i+1]<=0xfc and b[i+1]!=0x7f):return False
      i+=2;continue
    return False
  return True
def find(s):
  out=[];i=1
  while i<len(s):
    L=s[i]
    if L>=2 and i>=6 and i+1+L<=len(s) and (s[i-6] in(0x03,0x2b) or s[i-5]==0x2b or (s[i-4]==0x03 and s[i-3]==0)):
      b=bytes(s[i+1:i+1+L])
      if valid(b):
        try:t=dec(b)
        except Exception:t=''
        if JP.search(t):out.append((i,L,t));i+=1+L;continue
    i+=1
  return out
