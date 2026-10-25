# 시드 마이어의 문명 레볼루션 NDS 한글패치 1.0.1

일본판 『シドマイヤーズ シヴィライゼーション レボリューション』(NDS, 사이버프론트)의 한국어 패치입니다. 대사·메뉴·도움말·시민 의견·외교 대사와 문명·지도자·도시·기술·유닛·불가사의 이름을 외부 기계 번역 없이 직접 번역했습니다.

## 파일과 적용
릴리즈의 `CivRev_KR.xdelta`를 원본 ROM에 적용합니다. 원본은 일본판 YS6J이며 SHA-256은 다음과 같습니다.

`66df29768e91ec8bd433dcd336807a0fee25e7abf756499009946decd5e7b4f2`

```powershell
.\xdelta.exe -d -s "Sid Meier's Civilization Revolution (Japan).nds" CivRev_KR.xdelta "문명레볼루션_한국어.nds"
```

결과 ROM SHA-256: `66bca340a9664802f13bacd39f808127ac147f88dfab746e2abc7aff6792865a`. 패치는 `-0 -S none`으로 생성했고 복원 결과의 해시 일치를 확인했습니다. ROM은 배포하지 않습니다.

## 번역 범위
- 문자열 표(`Localization/str_JPN.STR`) 8,873개 슬롯 중 일본어가 있는 8,802개 슬롯 전부(고유 문장 8,683개)와 영문 `OK` 단독 슬롯 3개. 나머지 68개는 변수·기호만 있는 슬롯입니다. 미번역 0.
- 이름 파일 8종: 문명 17, 지도자 17, 도시 257, 기술 48, 유닛 128, 불가사의 42, 위인 46, 지형지물 128.
- NDS 배너 제목, ARM9 서수 서식(`第%d` → `제%d`).
- 변수 토큰(`@CIVNAME__MALE_PLURAL0` 등)은 모두 보존했습니다. 변수 뒤 조사는 받침을 알 수 없어 `을(를)`, `이(가)` 형식을 씁니다.

## 폰트
[갈무리 v2.40.4](https://github.com/quiple/galmuri/releases/tag/v2.40.4)의 갈무리11을 사용했습니다. 원본 폰트(`Arial14.nftr` 2종)는 12×12 셀의 1bpp 도트 폰트이고 한자가 11×11 자획이라, 갈무리11의 네이티브 11×11 자획을 늘이거나 줄이지 않고 같은 위치에 넣었습니다. 작업 폴더의 나눔스퀘어 네오·서울한강보다 원본 도트 자획과 크기가 가장 가깝습니다. 사용한 한글 828자는 원본 폰트의 한자 코드 칸(0x889F~)에 배정하며 가나·기호·영문 글리프는 보존합니다.

## 구조 메모
- STR(`STBL`): 0x10 항목 수, 0x14 `0x1d4`·표 크기, 0x1c부터 (해시 u32, 절대 오프셋 u32) 항목, 각 문자열은 길이 u32 + Shift-JIS(종단 문자 없음). 해시와 순서는 보존하고 문자열 블록만 다시 배치합니다.
- NFTR: CMAP이 Shift-JIS 코드를 직접 글리프에 매핑합니다. 게임은 공백 단위로 자동 줄바꿈합니다.

## 검증과 한계
- 빌드 ROM에서 STR·이름 파일·배너·ARM9 서수 서식을 다시 읽어 일본어 잔존 0을 확인했습니다(`tools/verify.py`).
- 그래픽 869개(인터페이스·지도자·유닛·건물·도시·불가사의·크레딧)를 모두 렌더링해 검사했습니다. 일본어 그림 글자는 없습니다. 전투 결과 배너는 원본도 영어 이미지(VICTORY! 등)이며, 크레딧 사진 속 한자는 중국 개발진 이름이라 그대로 둡니다. 3D 지형 텍스처는 렌더링하지 않았습니다.
- 창 없는 DeSmuME 코어를 내부 입력 API로 조작해 콜드 부팅, 메인 메뉴, 게임 종류·난이도·문명 선택, 고문 튜토리얼 대사, 조작 도움말, 시스템 메뉴, 지도 위 도시 이름을 확인했습니다. 전체 플레이·실기·통신 검증은 하지 않았습니다.
- 실기 DS 본체 메뉴의 시스템 폰트에는 한글이 없어 배너 제목이 제대로 보이지 않을 수 있습니다.
- `dwc/utility.bin`(닌텐도 공용 Wi-Fi 커넥션 설정 프로그램)은 범위에서 제외했습니다.

## 재현
Python 3.13과 `requirements.txt`. 이 저장소를 원본 ROM이 있는 폴더의 하위 폴더(예: `_work`)로 두고, 갈무리 v2.40.4의 `Galmuri11.bdf`를 `fonts/`에 넣습니다.

```powershell
python -X utf8 tools/txt_src.py translation/txt_names.json   # 이름 파일 원고 재생성(선택)
python -X utf8 tools/build.py                                # 상위 폴더에 (Korean).nds 생성
python -X utf8 tools/verify.py                               # 일본어 잔존 검사
```

번역 원고는 `translation/str_main.json`(문자열 번호 → 한국어), `translation/txt_names.json`(이름 파일), 용어집은 `translation/glossary.md`입니다. `tools/check.py`는 묶음 번역 검증기, `tools/render_gfx.py`는 그래픽 검사용 렌더러, `tools/emu_server.py`·`tools/emu.py`는 헤드리스 검증 에뮬레이터입니다.
