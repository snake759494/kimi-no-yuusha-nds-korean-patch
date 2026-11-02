"""이벤트/스크립트 명령 파서: u16 개수 + [op + 인자]..."""
import json,struct
_j=json.load(open(__file__.replace('evscript.py','../ext/opsz.json')))
SIZE={int(k):v for k,v in _j['size'].items()}
SIZE[0x5d]=1;SIZE[0x9f]=1
def expr(s,q):
  n=s[q];q+=1
  if n==0:return q
  q+=n-1
  for _ in range(n):
    t=s[q];q+=1
    if t==0:q=expr(s,q)
    elif t==1:q+=7
    else:raise ValueError('expr type %d'%t)
  return q
def parse(s):
  """returns list of (op, raw_bytes_after_op, strings) ; strings = list of (rel_off,len)"""
  n=struct.unpack_from('<H',s,0)[0];p=2;out=[]
  for _ in range(n):
    op=s[p];q=p+1
    if op==0x03:
      q+=5;l=s[q];strs=[(q+1-p,l)];q+=1+l
    elif op==0x2c:
      k=s[q];q+=1;strs=[]
      for _ in range(k):
        q+=1;l=s[q];strs.append((q+1-p,l));q+=1+l
    elif op==0xa9:
      l=s[q];strs=[(q+1-p,l)];q+=1+l+4
    elif op==0x02:q=expr(s,q+3);strs=[]
    elif op==0x38:q+=3+2*s[q+2]+2;strs=[]
    elif op==0x10:q=expr(s,q+1);strs=[]
    elif op in SIZE:q+=SIZE[op];strs=[]
    else:raise ValueError('op %02x at %x'%(op,p))
    out.append((op,s[p:q],strs));p=q
  return out,p
