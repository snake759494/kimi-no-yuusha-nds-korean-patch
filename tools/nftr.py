"""NFTR(1bpp) 읽기/쓰기: 글리프 비트맵·폭 교체, CMAP은 그대로 유지"""
import struct
class NFTR:
  def __init__(s,d):
    s.d=bytearray(d)
    fi=0x10;s.cglp=struct.unpack_from('<I',d,fi+0x10)[0]-8;s.cwdh=struct.unpack_from('<I',d,fi+0x14)[0]-8;s.cmap=struct.unpack_from('<I',d,fi+0x18)[0]-8
    c=s.cglp;s.cw,s.ch=d[c+8],d[c+9];s.gsz=struct.unpack_from('<H',d,c+10)[0];s.bpp=d[c+14]
    s.gbase=c+0x10
    w=s.cwdh;s.first,s.last=struct.unpack_from('<HH',d,w+8);s.wbase=w+0x10
    s.map={};p=s.cmap
    while p:
      lo,hi,typ=struct.unpack_from('<HHH',d,p+8);nxt=struct.unpack_from('<I',d,p+0x10)[0]
      if typ==0:
        o=struct.unpack_from('<H',d,p+0x14)[0]
        for c_ in range(lo,hi+1):s.map[c_]=o+c_-lo
      elif typ==1:
        for k,c_ in enumerate(range(lo,hi+1)):
          v=struct.unpack_from('<H',d,p+0x14+2*k)[0]
          if v!=0xffff:s.map[c_]=v
      else:
        n=struct.unpack_from('<H',d,p+0x14)[0]
        for k in range(n):
          c_,v=struct.unpack_from('<HH',d,p+0x16+4*k);s.map[c_]=v
      p=nxt-8 if nxt else 0
    s.n=(s.wbase-s.gbase)//s.gsz if 0 else s.last+1
  def glyph(s,i):
    b=s.d[s.gbase+i*s.gsz:s.gbase+(i+1)*s.gsz];bits=int.from_bytes(b,'big');tot=s.gsz*8
    return [[(bits>>(tot-1-(y*s.cw+x)))&1 for x in range(s.cw)] for y in range(s.ch)]
  def set_glyph(s,i,px):
    bits=0;tot=s.gsz*8
    for y in range(s.ch):
      for x in range(s.cw):
        if px[y][x]:bits|=1<<(tot-1-(y*s.cw+x))
    s.d[s.gbase+i*s.gsz:s.gbase+(i+1)*s.gsz]=bits.to_bytes(s.gsz,'big')
  def width(s,i):return tuple(s.d[s.wbase+3*i:s.wbase+3*i+3])
  def set_width(s,i,l,w,a):s.d[s.wbase+3*i:s.wbase+3*i+3]=bytes([l&0xff,w,a])
