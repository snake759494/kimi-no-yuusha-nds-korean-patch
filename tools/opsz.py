import re,json
t=('\n'+open('ext/ops.txt').read()).split('\nop ')[1:]
size={};dyn={}
for blk in t:
  ls=blk.splitlines();op=int(ls[0][:2],16)
  if 'none' in ls[0]:continue
  body=ls[1:]
  if 'bx lr' in body[0]:size[op]=0;continue
  tot=0;r2=None;ok=True;calls=0
  for l in body:
    m=re.search(r'mov r2, #(\w+)$',l)
    if m:r2=int(m[1],0)
    elif re.search(r'\br2\b,',l.split(' ',4)[-1] if 0 else l) and 'mov r2' not in l and ('ldr' in l or 'add' in l or 'mov' in l) and re.search(r' (ldr\w*|add|mov|sub|lsl|and) r2,',l):r2=None
    if 'bl #0x20237f4' in l or ('bx ip' in l and 'ldr ip' in body[0]):
      calls+=1
      if r2 is None:ok=False
      else:tot+=r2
    if re.search(r' (bx ip|bx lr|pop \{[^}]*pc\})$',l):break
  if ok:size[op]=tot
  else:dyn[op]=tot
json.dump({'size':size,'dyn':list(dyn)},open('ext/opsz.json','w'))
print({hex(k):v for k,v in sorted(size.items())});print('dyn',[hex(x) for x in dyn])
