"""데이터 파일 문자열 스캐너: u16길이 문자열 / u8길이 / NUL 고정필드"""
import re,struct
def valid(b,allow_nl=True):
  if not b:return False
  i=0;dbl=0
  while i<len(b):
    c=b[i]
    if c==0x0a and allow_nl:i+=1;continue
    if c==0x1b and i+1<len(b):i+=2;continue
    if 0x20<=c<0x7f:i+=1;continue
    if 0x81<=c<=0x9f or 0xe0<=c<=0xfc:
      if i+1>=len(b):return False
      try:b[i:i+2].decode('cp932')
      except:return False
      dbl+=1;i+=2;continue
    return False
  return dbl>0
def scan16(d,start=0):
  """greedy: u16 len + text"""
  out=[];p=start
  while p<len(d)-2:
    l=struct.unpack_from('<H',d,p)[0]
    if 2<=l<=600 and p+2+l<=len(d) and valid(d[p+2:p+2+l]):
      out.append((p,l));p+=2+l
    else:p+=1
  return out
def scan8(d,start=0):
  out=[];p=start
  while p<len(d)-1:
    l=d[p]
    if 2<=l and p+1+l<=len(d) and valid(d[p+1:p+1+l]):out.append((p,l));p+=1+l
    else:p+=1
  return out
def scanz(d):
  """NUL 종료 문자열(앞이 0 또는 시작)"""
  out=[]
  for m in re.finditer(rb'(?:[\x81-\x9f\xe0-\xea][\x40-\xfc]|[\x20-\x7e\x0a]|\x1b[\x00-\x7f])+',d):
    s=m.group()
    if valid(s) and m.end()<len(d) and d[m.end()]==0:out.append((m.start(),len(s)))
  return out
