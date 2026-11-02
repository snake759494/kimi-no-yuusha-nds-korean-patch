"""헤드리스 DeSmuME: python emu.py ROM 명령.json
명령: [{"keys":"a","hold":4,"wait":30,"repeat":n,"touch":[x,y],"shot":"name","save":"st","load":"st","dump":[addr,n]}]"""
import sys,json,os
from pathlib import Path
from desmume.emulator import DeSmuME
from desmume.controls import Keys,keymask
rom=sys.argv[1];cmds=json.loads(Path(sys.argv[2]).read_text(encoding='utf8')) if not sys.argv[2].startswith('[') else json.loads(sys.argv[2])
W=Path('K:/');shots=W/'shots';st=W/'states'
e=DeSmuME();e.volume_set(0);e.open(rom)
def fr(n):
  for _ in range(n):e.cycle(with_joystick=False)
for a in cmds:
  if 'load' in a:e.savestate.load_file(str(st/(a['load']+'.dst')))
  m=0
  for k in a.get('keys','').split('+'):
    if k:m|=keymask(getattr(Keys,'KEY_'+k.upper()))
  for _ in range(a.get('repeat',1)):
    if m:e.input.keypad_add_key(m)
    if 'touch' in a:e.input.touch_set_pos(*a['touch'])
    fr(a.get('hold',4 if (m or 'touch' in a) else 0))
    if m:e.input.keypad_rm_key(m)
    if 'touch' in a:e.input.touch_release()
    fr(a.get('wait',30))
  if 'shot' in a:e.screenshot().save(str(shots/(a['shot']+'.png')))
  if 'save' in a:e.savestate.save_file(str(st/(a['save']+'.dst')))
  if 'dump' in a:
    s,n=a['dump'];open(W/(a.get('dumpname','dump')+'.bin'),'wb').write(bytes(e.memory.unsigned[s:s+n]))
e.destroy();print('done')
