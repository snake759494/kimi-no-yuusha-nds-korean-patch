import sys;sys.path.insert(0,'tools')
import ndspy.rom,pack,evscript,struct
r=ndspy.rom.NintendoDSRom.fromFile('L:/Kimi no Yuusha (Japan).nds')
f=r.getFileByName(sys.argv[1]);names,subs=pack.unpack(f);s=subs[names.index(sys.argv[2])]
n=struct.unpack_from('<H',s,0)[0];p=2;hist=[]
import types
for k in range(n):
  if p>=len(s):print('eof',k);break
  try:
    c,_=evscript.parse(bytes([1,0])+s[p:])
    q=p+len(c[0][1])
  except Exception as e:print('ERR',e,hex(p));break
  hist.append((p,s[p:q]));p=q
N=int(sys.argv[3]) if len(sys.argv)>3 else 12
for p0,b in hist[-N:]:print(hex(p0),b[:30].hex(' '))
print('next',hex(p),s[p:p+48].hex(' '),'len',hex(len(s)),k,n)
