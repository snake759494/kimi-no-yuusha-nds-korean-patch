# 너의 용사 (키미노 유우샤, NDS) 비공식 한글패치

닌텐도 DS 일본판 **君のユウシャ** (SNK PLAYMORE) 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·일본어 원문·번역 대본은 포함하지 않습니다.

## 릴리즈 파일
| 파일 | 용도 |
| --- | --- |
| `KimiNoYuusha_NDS_KO_v1.0.xdelta` | 본편 패치 — 일본판 `.nds` 롬용 |

## 적용 방법 (에뮬레이터)
1. 아래 해시와 일치하는 **원본 롬**(128MB)을 준비합니다.
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.\Kimi no Yuusha (Japan).nds'`
2. xdeltaUI 등으로 원본에 xdelta를 적용합니다.
   - 명령줄: `xdelta3 -d -s "Kimi no Yuusha (Japan).nds" KimiNoYuusha_NDS_KO_v1.0.xdelta "Kimi no Yuusha (Korean).nds"`
3. 만들어진 `.nds`를 DeSmuME·melonDS 등 DS 에뮬레이터에서 실행합니다.

> DS 실기·플래시 카트에서는 확인하지 않았습니다.

## 해시
| 항목 | 값 |
| --- | --- |
| 원본 크기 | 134,217,728 바이트 |
| 원본 MD5 | `15af83ec4a1949a92b531db91c21b2a4` |
| 원본 SHA-256 | `d1d7122af67183528e30f399664fc85a128d5055556269b2845a501f62ce9a42` |
| 결과 NDS 크기 / SHA-256 | 94,374,408 바이트 / `e294d45c2329e4d063fab579a718996cd80862328054bcfc698f29f1d88c2500` |

릴리즈 첨부 파일의 SHA-256은 [release_manifest.json](release_manifest.json)에 있습니다.

## 한글화 내용
- 이벤트·필드·던전 대사, 길드 의뢰, 세이브 포인트·함정 안내 등 스크립트 문자열 약 18,000개
- 아이템·장비·성술·마물·지명·의뢰 등 데이터 문자열 약 3,400개, 전투 중 보스 대사
- 실행 코드(arm9) 속 메뉴·시스템 메시지 약 160개
- 그림 글자: 타이틀 로고(「너의 용사」, 영어 KIMINO YUSHA는 원본 유지), 장 번호 간판(제○화·최종화), 상태 메뉴 능력치 이름, 세이브/로드 화면, 튜토리얼 그림 37장 등
- 게임기 메뉴(배너) 제목
- 글꼴: 게임 폰트에 Galmuri11 한글 글리프 추가

## 그대로 둔 것
- 영어 제작진 크레딧, 타이틀의 영어 표기
- 게임 중 나오지 않는 디버그용 데이터
- 숨겨진 던전 구역의 짧은 대사 조각 2개 정도 (자동 탐색으로 찾지 못함)

## 검증 범위
DeSmuME에서 부팅과 타이틀 화면을 확인했습니다. 전체 플레이 검증은 하지 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
