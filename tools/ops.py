from capstone import *
import struct,re
a=open('ext/arm9.bin','rb').read()
md=Cs(CS_ARCH_ARM,CS_MODE_ARM)
def w(x):return struct.unpack_from('<I',a,x-0x2000000)[0]
def dis(s,n=0x400):
  o=s-0x2000000;out=[]
  for ins in md.disasm(a[o:o+n],s):
    out.append(ins)
    if ins.mnemonic in('pop','bx') and ('pc' in ins.op_str or ins.op_str=='lr'):break
    if ins.mnemonic=='b' :break
  return out
res={}
for op in range(0xcb):
  br=next(md.disasm(a[0x23f18+op*4:0x23f1c+op*4],0x2023f18+op*4))
  case=int(br.op_str[1:],16)
  ins=dis(case,0x40)
  vt=None
  for i in ins:
    m=re.match(r'r\d, \[pc, #(0x[0-9a-f]+)\]',i.op_str)
    if i.mnemonic=='ldr' and m:
      v=w(i.address+8+int(m[1],16))
      if 0x20e0000<=v<0x20fb000:vt=v
  if vt is None:
    for i in ins:
      if i.mnemonic=='bl' and int(i.op_str[1:],16) not in(0x201853c,0x202376c):
        for j in dis(int(i.op_str[1:],16),0x80):
          m=re.match(r'r\d, \[pc, #(0x[0-9a-f]+)\]',j.op_str)
          if j.mnemonic=='ldr' and m:
            v=w(j.address+8+int(m[1],16))
            if 0x20e0000<=v<0x20fb000:vt=v
  if vt is None:res[op]=None;continue
  rd=w(vt+8)
  res[op]=(vt,rd)
with open('ext/ops.txt','w') as f:
  for op,v in res.items():
    if not v:f.write('op %02x none\n'%op);continue
    f.write('op %02x vt %x read %x\n'%(op,v[0],v[1]))
    for i in dis(v[1],0x300):f.write('   %x %s %s\n'%(i.address,i.mnemonic,i.op_str))
