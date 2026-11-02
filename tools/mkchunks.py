import sys,json,re,collections;sys.path.insert(0,'tools')
import ndspy.rom,pack,evscript
from extract_dec import dec
r=ndspy.rom.NintendoDSRom.fromFile('L:/Kimi no Yuusha (Japan).nds')
cn=json.load(open('ext/charaname.json',encoding='utf8'));kn=json.load(open('trans/names.json',encoding='utf8'))
def spk(i):
  n=cn[i] if i<len(cn) else ''
  return kn.get(n,n)
order=[]
def key(n):
  m=re.search(r'_Data/(\w+)/(\w+)',n)
  pri={'Event/Chapter':0,'Event/Town':1,'Event/Quest':2,'Event/Dungeon':3,'Event/Epilogue':4,'Event/Help':5,'Script':6}
  for k,v in pri.items():
    if k in n:return (v,n)
  return (9,n)
files=[]
for i,f in enumerate(r.files):
  n=r.filenames.filenameOf(i)
  if re.search(r'_Data/(Event|Script)/.*\.dat$',n):files.append((key(n),i,n))
files.sort()
seen=set();ents=[]
for _,i,n in files:
  try:names,subs=pack.unpack(r.files[i])
  except:continue
  for nm,s in zip(names,subs):
    try:cmds,p=evscript.parse(s);assert p==len(s)
    except:continue
    for op,raw,strs in cmds:
      for o,l in strs:
        ja=dec(bytes(raw[o:o+l]))
        if ja in seen or not ja.strip():continue
        seen.add(ja)
        e={'ja':ja,'src':n.split('_Data/')[1]+':'+nm}
        if op==3:e['spk']=spk(raw[4]|raw[5]<<8);e['w']=216;e['L']=3
        elif op==0x2c:e['w']=156;e['L']=1;e['spk']='(선택지)'
        else:e['w']=132;e['L']=3;e['spk']='(시스템 알림)'
        ents.append(e)
tot=sum(len(e['ja']) for e in ents);print(len(ents),tot)
# 청크 분할 ~ 16000자, 파일 경계 우선
chunks=[];cur=[];cs=0;TARGET=16000
for e in ents:
  cur.append(e);cs+=len(e['ja'])
  if cs>=TARGET:chunks.append(cur);cur=[];cs=0
if cur:chunks.append(cur)
for k,c in enumerate(chunks):
  json.dump(c,open('trans/src/s%02d.json'%k,'w',encoding='utf8'),ensure_ascii=False,indent=0)
  print('s%02d'%k,len(c),sum(len(e['ja']) for e in c),c[0]['src'],'->',c[-1]['src'])
