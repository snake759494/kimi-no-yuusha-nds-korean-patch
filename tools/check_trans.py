"""번역 검사: python tools/check_trans.py <원문 src json> <번역 ko json>
원문: [{"ja":..., "w":최대줄폭px, "L":최대줄수, "cap":바이트상한(선택)}...]
번역: 같은 길이의 문자열 리스트. 오류가 없으면 OK 출력."""
import json,sys,re,collections,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import width
TOKRE=re.compile(r'\{c?[0-9a-f]{2}\}')
src=json.load(open(sys.argv[1],encoding='utf8'));ko=json.load(open(sys.argv[2],encoding='utf8'))
err=[]
if len(src)!=len(ko):print('개수 불일치',len(src),len(ko));sys.exit(1)
for i,(s,k) in enumerate(zip(src,ko)):
  if not isinstance(k,str) or not k.strip():err.append((i,'빈 번역'));continue
  if collections.Counter(TOKRE.findall(s['ja']))!=collections.Counter(TOKRE.findall(k)):err.append((i,'제어코드 불일치 '+str(TOKRE.findall(s['ja']))+' vs '+str(TOKRE.findall(k))))
  bad=[c for c in TOKRE.sub('',k) if not ('\uac00'<=c<='\ud7a3' or c=='\n')]
  bb=[]
  for c in bad:
    try:c.encode('cp932')
    except:bb.append(c)
  if bb:err.append((i,'표시 불가 문자 '+''.join(sorted(set(bb)))))
  if re.search('[ぁ-んァ-ヶ]',k):err.append((i,'일본어 가나 남음'))
  lines=k.split('\n')
  if len(lines)>s.get('L',3):err.append((i,'줄 수 초과 %d>%d'%(len(lines),s.get('L',3))))
  for l in lines:
    w=width(l)
    if w>s.get('w',216):err.append((i,'줄 폭 초과 %dpx>%d: %s'%(w,s.get('w',216),l)))
  if 'cap' in s:
    n=sum(2 if '\uac00'<=c<='\ud7a3' else len(c.encode('cp932')) for c in TOKRE.sub('',k).replace('\n','\x0a'))+2*len(TOKRE.findall(k))
    if n>s['cap']-1:err.append((i,'바이트 초과 %d>%d'%(n,s['cap']-1)))
  if 'cap' not in s:
    n=sum(2 if '\uac00'<=c<='\ud7a3' else len(c.encode('cp932',errors='replace')) for c in TOKRE.sub('',k))+2*len(TOKRE.findall(k))
    if n>255:err.append((i,'바이트 255 초과'))
for i,m in err[:80]:print(i,m)
print('오류',len(err)) if err else print('OK')
