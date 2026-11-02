import struct
def unpack(d):
  n=struct.unpack_from('<I',d,0)[0]
  offs=list(struct.unpack_from('<%dI'%n,d,4))+[len(d)]
  p=4+4*n;names=[]
  for i in range(n):
    l=d[p];names.append(d[p+1:p+1+l].decode());p+=1+l
  return names,[d[offs[i]:offs[i+1]] for i in range(n)]
def repack(names,subs):
  n=len(names);hdr=bytearray(struct.pack('<I',n));nm=bytearray()
  for x in names:b=x.encode();nm+=bytes([len(b)])+b
  p=4+4*n+len(nm);offs=[]
  for s in subs:offs.append(p);p+=len(s)
  hdr+=struct.pack('<%dI'%n,*offs)
  return bytes(hdr+nm+b''.join(subs))
