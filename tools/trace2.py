from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
e=DeSmuME();e.volume_set(0);e.open("L:/Kimi no Yuusha (Japan).nds")
def fr(n):
  for _ in range(n):e.cycle(with_joystick=False)
def press(k,w):
  e.input.keypad_add_key(keymask(k));fr(4);e.input.keypad_rm_key(keymask(k));fr(w)

hits=[]
def cb(addr,size):
  r=e.memory.register_arm9
  if e.memory.unsigned[0x23df81c]==0x90 or True:
    hits.append((hex(r.pc),hex(r.lr),hex(addr)))
e.memory.register_write(0x23df81c,cb,4)
fr(600);press(Keys.KEY_START,60)
for _ in range(30):
  press(Keys.KEY_A,90)
  if hits:break
for h in hits[:20]:print(h)
e.destroy()
