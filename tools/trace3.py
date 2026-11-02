from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
e=DeSmuME();e.volume_set(0);e.open("L:/Kimi no Yuusha (Japan).nds")
def fr(n):
  for _ in range(n):e.cycle(with_joystick=False)
def press(k,w):
  e.input.keypad_add_key(keymask(k));fr(4);e.input.keypad_rm_key(keymask(k));fr(w)
log=[]
def cb(addr,size):
  r=e.memory.register_arm9
  log.append(r.r1)
e.memory.register_exec(0x202611c,cb)
fr(600);press(Keys.KEY_START,60);press(Keys.KEY_A,60)
print(len(log),' '.join('%02x'%x for x in log[:120]))
e.destroy()
