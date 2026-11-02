"""데이터 파일 문자열 위치 정의"""
import struct,sys
import os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import dscan
SEQ16=['_Data/System/ItemData/%s.dat'%x for x in ['ItemParam','ItemInfo','WeaponParam','WeaponInfo','ArmorParam','ArmorInfo','AccessoryParam','AccessoryInfo','SkillBookParam','SkillBookInfo','StarDustParam','StarDustInfo']]+\
  ['_Data/System/BaseName/%s.dat'%x for x in ['TownName','DungeonName','AreaName']]+['_Data/EpilogueList/EpilogueList.dat','_Data/HelpList/HelpList.dat']
SEQ8=['_Data/Event/CharaName/CharaName.dat','_Data/StoryPiece/ChapterName.dat']
# (hdr, R, [(off,cap)])  cap = NUL 포함 최대 바이트
FIXED={
 '_Data/Battle/Enemy/EnemyData.dat':(2,496,[(0,19)]+[(96+24*k,20) for k in range(15)]),
 '_Data/Battle/Help/BattleHelpData.dat':(1,18,[(0,18)]),
 '_Data/System/ComboData/ComboData.dat':(2,76,[(56,20)]),
 '_Data/System/MagicData/MagicData.dat':(2,44,[(0,19)]),
 '_Data/System/MagicData/MagicInfoData.dat':(2,67,[(0,67)]),
 '_Data/System/SkillData/SkillData.dat':(2,60,[(0,19)]),
 '_Data/System/SkillData/SkillInfoData.dat':(2,67,[(0,67)]),
 '_Data/Town/Dat/DataMessage.dat':(2,256,[(0,256)]),
 '_Data/Town/Dat/DataQuest.dat':(2,824,[(0,256),(298,256),(554,256)]),
 '_Data/Town/Dat/DataInfo.dat':(4,266,[(10,256)]),
}
def strings(name,d):
  """[(pos, length, prefix_size)]  prefix 0 = 고정필드"""
  if name in SEQ16:return [(p,l,2) for p,l in dscan.scan16(d)]
  if name in SEQ8:return [(p,l,1) for p,l in dscan.scan8(d)]
  hdr,R,fields=FIXED[name];out=[]
  n=(len(d)-hdr)//R
  for i in range(n):
    for off,cap in fields:
      s=hdr+i*R+off;e=s
      while e<s+cap and d[e]!=0:e+=1
      if e>s and dscan.valid(d[s:e]):out.append((s,e-s,-cap))
  return out
