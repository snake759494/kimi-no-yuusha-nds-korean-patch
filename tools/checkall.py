import sys;sys.path.insert(0,'tools')
import ndspy.rom,pack,evscript,collections,re
r=ndspy.rom.NintendoDSRom.fromFile('L:/Kimi no Yuusha (Japan).nds')
ok=bad=0;errs=collections.Counter();ex={}
pat=sys.argv[1] if len(sys.argv)>1 else r'_Data/Event/.*\.dat$'
for i,f in enumerate(r.files):
  n=r.filenames.filenameOf(i)
  if not re.search(pat,n):continue
  try:names,subs=pack.unpack(f)
  except Exception as e:errs['pack:'+re.sub(r'\d+','#',n)]+=1;continue
  for nm,s in zip(names,subs):
    try:
      cmds,p=evscript.parse(s)
      if p!=len(s):raise ValueError('end %x/%x'%(p,len(s)))
      ok+=1
    except Exception as e:
      bad+=1;k=re.sub(r'\d+','#',n)+' '+str(e)[:6];errs[k]+=1;ex.setdefault(k,(n,nm,str(e)))
print(ok,bad)
for k,v in errs.most_common(30):print(v,k,ex.get(k))
