import ndspy.rom,re,collections,sys
r=ndspy.rom.NintendoDSRom.fromFile('Kimi no Yuusha (Japan).nds')
pat=re.compile(rb'(?:[\x81-\x9f\xe0-\xea][\x40-\xfc]|[\x20-\x7e]){4,}')
agg=collections.Counter()
for i,f in enumerate(r.files):
  n=r.filenames.filenameOf(i)
  if n.split('.')[-1] in('NCLR','NCER','NCBR','NANR','NCGR','NSCR','sdat','NFTR') or n.endswith(('nsbmd','nsbtx','nsbca','nsbta','nsbtp')):continue
  c=0
  for m in pat.finditer(f):
    s=m.group()
    try:t=s.decode('cp932')
    except:continue
    j=sum(1 for ch in t if ord(ch)>0x3000)
    if j>=2:c+=j
  if c:agg[n]=c
tot=sum(agg.values());print('total jp chars',tot)
g=collections.Counter()
for n,c in agg.items():g[re.sub(r'\d+','#',n)]+=c
for k,v in g.most_common(60):print(v,k)
a=bytes(r.arm9);print(len(a),a[-16:].hex())
