# bio.csv 채우는 법 (Transfermarkt)

경기 스탯 아님 — **선수 신상·계약·시장가치**. 소스는 Transfermarkt 한 곳.
채우고 `python rebuild.py` 하면 자동 반영됨.

---

## STEP 1 — 선수 Transfermarkt 페이지 열기

구글에 **`{영어이름} transfermarkt`** 검색 → 첫 결과 (주소가 `transfermarkt.com/.../profil/spieler/숫자`) 클릭.
또는 transfermarkt.com 접속 → 상단 돋보기 검색.

22명 검색어 (bio.csv 순서):

| # | bio.csv Player | 검색어 |
|---|---|---|
| 1 | Marcão | `Marcao Ulsan transfermarkt` |
| 2 | Abdallah Hleihil | `Abdallah Hleihel transfermarkt` (철자 Hlei**hel**) |
| 3 | Yago Cariello | `Yago Cariello transfermarkt` |
| 4 | Stefan Mugoša | `Stefan Mugosa transfermarkt` |
| 5 | Tiago Orobó | `Tiago Orobo transfermarkt` |
| 6 | Diogo | `Diogo Oliveira Daejeon transfermarkt` |
| 7 | Patryk Klimala | `Patryk Klimala transfermarkt` |
| 8 | Breno Herculano | `Breno Herculano transfermarkt` |
| 9 | Vitor Gabriel | `Vitor Gabriel Bucheon transfermarkt` |
| 10 | Morgan Ferrier | `Morgan Ferrier transfermarkt` |
| 11 | Jhon Montaño | `Jhon Montano Bucheon transfermarkt` |
| 12 | Joo Min-kyu | `Joo Min-kyu transfermarkt` |
| 13 | Lee Hojae | `Lee Ho-jae Pohang transfermarkt` |
| 14 | Kim Sinjin | `Kim Sin-jin Jeju transfermarkt` |
| 15 | Jeong Jaemin | `Jeong Jae-min Gimcheon transfermarkt` |
| 16 | Lee Kunhee | `Lee Kun-hee footballer transfermarkt` |
| 17 | Kong Minhyu | `Kong Min-hyeon transfermarkt` |
| 18 | Bruno Mota | `Bruno Mota Jeonbuk transfermarkt` |
| 19 | Hólmbert Friðjónsson | `Holmbert Fridjonsson transfermarkt` |
| 20 | Choe Byeongchan | `Choi Byeong-chan Gangwon transfermarkt` |
| 21 | Kim Gun-hee | `Kim Gun-hee Gangwon transfermarkt` (강원 소속, 동명이인 주의) |
| 22 | Lee Sang-heon | `Lee Sang-heon Gimcheon transfermarkt` |

---

## STEP 2 — 페이지에서 값 읽기

Transfermarkt 선수 페이지 구조:

```
┌───────────────────────────────────────────────┐
│ [사진]  Marcos Vinícius Amaral Alves            │
│         "Marcão"                                │
│                                                │
│   Market value:  €800k       ← market_value_eur │
│   Last update: Jun 20, 2025  ← market_value_asof │
├───────────────────────────────────────────────┤
│ PLAYER DATA                                     │
│   Date of birth:   Jun 17, 1994  ← dob         │
│   Age:             31                           │
│   Height:          1,96 m        ← height_cm=196 │
│   Citizenship:     Brazil        ← nationality  │
│   Position:        Centre-Forward               │
│   Foot:            right         ← preferred_foot│
│   Current club:    Ulsan HD                     │
│   Joined:          Jul 19, 2025                 │
│   Contract expires: Dec 31, 2026 ← contract_until│
├───────────────────────────────────────────────┤
│ ... 아래로 스크롤 ...                           │
│ NATIONAL TEAM  (섹션 없으면 대표팀 경력 X → 0) │
│   Korea, South:  Matches 12  Goals 3            │
│                    ↑ nt_caps      ↑ nt_goals    │
└───────────────────────────────────────────────┘
```

값 변환:
- **시장가치**: `€1.50m` → `1500000` / `€900k` → `900000` / `€800Th.` → `800000` / `€250Th.` → `250000`
- **날짜**: `Jun 17, 1994` → `1994-06-17` (YYYY-MM-DD)
- **키**: `1,96 m` → `196`
- **Contract expires 가 "-"** (비공개) → 빈칸
- **weight_kg**: Transfermarkt엔 없음 → 빈칸 (또는 나무위키)
- **boot_sponsor**: Transfermarkt엔 없음 → 선수 인스타/기사 확인, 없으면 빈칸

---

## STEP 3 — bio.csv 해당 줄에 입력

컬럼 순서:
`Player,dob,height_cm,weight_kg,preferred_foot,nationality,nt_caps,nt_goals,market_value_eur,market_value_asof,contract_until,boot_sponsor,transfermarkt_url,source,collected_date`

예 (Marcão):
```
Marcão,1994-06-17,196,,right,Brazil,0,0,800000,2025-06-20,2026-12-31,,https://www.transfermarkt.com/marcao/profil/spieler/238224,transfermarkt,2026-08-29
```
- 못 찾은 값은 **빈칸** (쉼표만). 추정치 넣지 말 것.
- `Player` 열(맨 앞)은 절대 수정 금지 — 발음기호 포함 그대로.
- 숫자만 (쉼표·단위·% 제외).

---

## STEP 4 — 저장 후

```
python rebuild.py
```

`_build_report.md` 에 "bio.csv 채워진 선수: N/22" 로 확인.

**3~4명만 먼저 채워서 보내줘** — 반영 확인하고 나머지 진행.
