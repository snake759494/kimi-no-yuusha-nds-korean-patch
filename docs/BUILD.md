# 빌드 방법

번역 대본·원문·그림 편집 명세는 저장소에 없으므로, 아래는 자신이 가진 원본과 번역 파일로 다시 빌드하는 절차입니다.

## 준비물
- 원본 `Kimi no Yuusha (Japan).nds` (MD5 `15af83ec4a1949a92b531db91c21b2a4`)
- Python 3.12+ : `pip install ndspy pillow numpy opencv-python-headless`
- 글꼴 `NanumSquareNeo-*.ttf`, `Galmuri11.bdf`, `Galmuri9.bdf`

## 폴더 구성
```
<작업 폴더>/                    원본 .nds, NanumSquareNeo-*.ttf
  <이 저장소>/
    tools/
    fonts/                      Galmuri*.bdf
    ext/                        추출물 (arm9, 폰트, 문자열 목록)
    trans/src/sNN.json          스크립트 원문 목록 [{ja, ...}]
    trans/ko/sNN.json           번역 (원문과 같은 순서의 한국어 배열)
    trans/src|ko/data_*.json    데이터 문자열 원문/번역
    trans/names.json            캐릭터·마물 이름 {일본어: 한국어}
    trans/names_data.json       대사 속 이름 치환 표
    trans/arm9_ko.json          실행 코드 문자열 {오프셋: 한국어}
    trans/extra_ko.json         보스 대사 등 추가 {enemy, script_extra, datainfo}
    trans/gfx_ko.json           그림 글자 명세
    trans/tutor_ko.json         튜토리얼 그림 명세
```

## 순서
1. 추출: `python tools/extract.py` → 스크립트·데이터·arm9 문자열 목록. 번역을 `trans/ko`에 작성하고 `python tools/check_trans.py`로 검사
2. 그림 글자: `python tools/preview.py`, `tools/gridview.py`로 좌표 확인 후 `gfx_ko.json`·`tutor_ko.json` 작성
3. 빌드: `python tools/build.py` → `Kimi no Yuusha (Korean).nds`
4. 차분: `xdelta3 -e -0 -S none -s 원본.nds 한글.nds 패치.xdelta` (압축 옵션 없이)
