"""이벤트/스크립트 텍스트 추출 -> ext/script_strings.json"""
import sys,json,re,collections
sys.path.insert(0,'tools')
import ndspy.rom,pack,evscript
r=ndspy.rom.NintendoDSRom.fromFile('L:/Kimi no Yuusha (Japan).nds')
def dec(b):
  out=[];i=0
  while i<len(b):
    c=b[i]
    if c==0x1b:out.append('{%02x}'%b[i+1]);i+=2
    elif c==0x0a:out.append('\n');i+=1
    elif c<0x20:out.append('{c%02x}'%c);i+=1
    elif c<0x80 or 0xa1<=c<=0xdf:out.append(bytes([c]).decode('cp932'));i+=1
    else:out.append(b[i:i+2].decode('cp932'));i+=2
  return ''.join(out)
ents=[];bad=[]
for i,f in enumerate(r.files):
  n=r.filenames.filenameOf(i)
  if not re.search(r'_Data/(Event|Script)/.*\.dat$',n):continue
  try:names,subs=pack.unpack(f)
  except:continue
  for si,(nm,s) in enumerate(zip(names,subs)):
    try:
      cmds,p=evscript.parse(s)
      assert p==len(s)
    except:bad.append((n,nm));continue
    for ci,(op,raw,strs) in enumerate(cmds):
      for k,(o,l) in enumerate(strs):
        ents.append({'f':n,'s':si,'c':ci,'k':k,'op':op,'ja':dec(raw[o:o+l])})
json.dump(ents,open('ext/script_strings.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
json.dump(bad,open('ext/script_bad.json','w',encoding='utf8'),indent=0)
u=collections.Counter(e['ja'] for e in ents)
print(len(ents),'unique',len(u),'chars',sum(len(k) for k in u))
cc=collections.Counter(m for k in u for m in re.findall(r'\{\w+\}',k))
print(cc.most_common(40))
