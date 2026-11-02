import sys
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
import ndspy.rom
e=DeSmuME();e.volume_set(0);e.open("L:/Kimi no Yuusha (Japan).nds")
def fr(n):
  for _ in range(n):e.cycle(with_joystick=False)
fr(10);e.savestate.load_file('K:/states/p3.dst');fr(2)
ram=bytes(e.memory.unsigned[0x2000000:0x2400000])
r=ndspy.rom.NintendoDSRom.fromFile('L:/Kimi no Yuusha (Japan).nds')
ch=r.getFileByName('_Data/Event/Chapter/Chapter.dat')
key='人々が平和'.encode('cp932')
i=ram.find(key);print('ram',hex(0x2000000+i))
j=ch.find(key)
# align: find file start in RAM
seg=ch[j-600:j+800]
k=ram.find(ch[j+300:j+340]);print('next seg in ram',hex(0x2000000+k) if k>=0 else None)
pcs={}
def cb(addr,size):
  pc=e.memory.register_arm9.pc
  pcs.setdefault(pc,set()).add(addr)
base=0x2000000+i
for a in range(base-0x80,base+0x300):e.memory.register_read(a,cb,1)
for _ in range(3):
  e.input.keypad_add_key(keymask(Keys.KEY_A));fr(4);e.input.keypad_rm_key(keymask(Keys.KEY_A));fr(100)
for pc,s in sorted(pcs.items()):print(hex(pc),len(s),hex(min(s)),hex(max(s)))
print(ram[i-0x80:i+0x40].hex(' '))
e.destroy()
