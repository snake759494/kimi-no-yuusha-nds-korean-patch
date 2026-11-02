import sys,json
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
e=DeSmuME();e.volume_set(0);e.open("L:/Kimi no Yuusha (Japan).nds")
def fr(n):
  for _ in range(n):e.cycle(with_joystick=False)
def press(k,w):
  e.input.keypad_add_key(keymask(k));fr(4);e.input.keypad_rm_key(keymask(k));fr(w)
seq=[];cur=[None]
def onop(addr,size):
  r=e.memory.register_arm9;cur[0]=[r.r1,0];seq.append(cur[0])
def onread(addr,size):
  r=e.memory.register_arm9
  if cur[0] is not None:cur[0][1]+=r.r2
e.memory.register_exec(0x202611c,onop)
e.memory.register_exec(0x20237f4,onread)
fr(10);e.savestate.load_file('K:/states/%s.dst'%sys.argv[1])
for act in sys.argv[3].split(','):
  if act.startswith('t'):
    x,y=map(int,act[1:].split(':'));e.input.touch_set_pos(x,y);fr(4);e.input.touch_release();fr(60)
  elif act.startswith('w'):fr(int(act[1:]))
  else:
    k,n=act.split('*') if '*' in act else (act,1)
    for _ in range(int(n)):press(getattr(Keys,'KEY_'+k.upper()),40)
fr(10);e.savestate.save_file('K:/states/%s.dst'%sys.argv[2]);e.screenshot().save('K:/shots/%s.png'%sys.argv[2])
sizes={}
for op,n in seq:sizes.setdefault(op,set()).add(n)
json.dump(seq,open('K:/ext/seq_%s.json'%sys.argv[2],'w'));print(json.dumps({hex(k):sorted(v) for k,v in sorted(sizes.items())}))
e.destroy()
