import sys,ndspy.rom
r=ndspy.rom.NintendoDSRom.fromFile('L:/Kimi no Yuusha (Japan).nds')
d=r.getFileByName(sys.argv[1]);o=int(sys.argv[2],0) if len(sys.argv)>2 else 0;n=int(sys.argv[3],0) if len(sys.argv)>3 else 256
print(len(d))
for i in range(o,min(o+n,len(d)),32):
  b=d[i:i+32]
  t=''
  j=0
  while j<len(b):
    c=b[j]
    if (0x81<=c<=0x9f or 0xe0<=c<=0xea) and j+1<len(b):
      try:t+=b[j:j+2].decode('cp932');j+=2;continue
      except:pass
    t+=chr(c) if 0x20<=c<0x7f else '.';j+=1
  print('%05x'%i,b.hex(' '),t)
