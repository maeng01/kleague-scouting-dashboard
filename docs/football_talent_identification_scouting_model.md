# Football Talent Identification & Scouting Model
## 데이터 기반 축구 선수 발굴·잠재력 평가 시스템 종합 기획서

---

## 0. 프로젝트 한눈에 보기

### 프로젝트 가칭

**Football Scouting Intelligence System**

또는

**Football Talent Identification & Scouting Model**

### 핵심 아이디어

축구 선수를 단순히 "현재 잘하는 선수"로 평가하는 것이 아니라,

> **현재 경기력 + 성장 가능성 + 기술·전술·신체 능력 + 일관성 + 시장성 + 브랜드 적합성 등을 종합하여 향후 높은 수준의 프로 선수로 성장할 가능성이 높은 선수를 발굴하는 데이터 기반 스카우팅 시스템**

을 구축한다.

특히 유소년 및 초기 프로 선수 데이터를 대상으로 모델을 만들고, 과거에 성공한 선수와 그렇지 못한 선수의 초기 커리어 데이터를 활용해 모델을 **백테스팅(backtesting)**한다.

최종적으로는 현재 유소년 선수에게 적용할 수 있는 **선수 랭킹 및 스카우팅 추천 대시보드**까지 구현한다.

---

# 1. 왜 이 프로젝트를 만드는가?

## 1.1 기존의 선수 스카우팅

축구 선수 스카우팅은 전통적으로 다음 요소들을 종합적으로 판단한다.

- 경기력
- 기술
- 전술 이해도
- 신체 능력
- 성장 가능성
- 경기 영상
- 코치 및 스카우터의 평가
- 성격 및 훈련 태도
- 부상 이력
- 팀 및 리그 수준
- 선수의 시장성

즉, 단순한 통계 하나만으로 선수를 평가하지 않는다.

특히 에이전시는 구단 스카우팅과 달리 다음 질문까지 고려할 수 있다.

> "이 선수가 현재 잘하는가?"

뿐만 아니라,

> **"앞으로 얼마나 성장할 수 있는가?"**

> **"우리가 이 선수의 가치를 얼마나 키울 수 있는가?"**

> **"시장성이 있는가?"**

> **"어떤 브랜드와 연결할 수 있는가?"**

까지 고려할 수 있다.

---

# 2. 에이전시와 구단 스카우팅의 차이

## 구단 스카우팅

주요 질문:

> **"우리 팀에 필요한 선수인가?"**

평가 요소:

- 전술 적합성
- 포지션 적합성
- 현재 경기력
- 신체 능력
- 상대적인 선수 가치
- 이적료 및 연봉
- 팀 전술과의 궁합

## 스포츠 에이전시

주요 질문:

> **"이 선수를 영입/관리했을 때 장기적으로 어떤 가치가 발생하는가?"**

평가 요소:

- 경기력
- 성장 가능성
- 프로의식
- 시장성
- 팬덤
- SNS
- 콘텐츠 가능성
- 브랜드 적합성
- 스폰서십 가능성
- 선수 이미지
- 향후 이적 가능성

따라서 에이전시 모델은 **Performance만 보는 모델이 아니라 Athlete Value를 평가하는 모델**로 확장할 수 있다.

---

# 3. 프로젝트의 핵심 질문

이 프로젝트의 가장 중요한 연구 질문은 다음과 같이 정의한다.

> **"유소년 및 초기 프로 선수의 당시 경기력 데이터를 기반으로 향후 높은 수준의 프로 선수로 성장할 가능성을 얼마나 효과적으로 식별할 수 있는가?"**

이를 다시 세부 질문으로 나눈다.

### Research Question 1

현재 경기력이 좋은 선수를 효과적으로 식별할 수 있는가?

### Research Question 2

현재 경기력과 별개로 성장 가능성이 높은 선수를 식별할 수 있는가?

### Research Question 3

과거에 성공한 선수들의 유소년/초기 프로 시절 데이터를 현재의 모델에 적용했을 때 높은 잠재력 점수를 부여하는가?

### Research Question 4

성공한 선수와 그렇지 못한 선수를 모델이 어느 정도 구분할 수 있는가?

### Research Question 5

검증된 모델을 현재 유소년 선수에게 적용했을 때 스카우팅 우선순위를 제시할 수 있는가?

---

# 4. 전체 시스템 구조

```text
                    선수 데이터
                        ↓
                데이터 수집 / 정제
                        ↓
              Feature Engineering
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
  Performance Model              Potential Model
        ↓                               ↓
  현재 경기력 평가                  성장 가능성 평가
        │                               │
        └───────────────┬───────────────┘
                        ↓
             Position-specific Model
                        ↓
               Scouting Score
                        ↓
              Historical Backtest
                        ↓
       성공 선수 / 비성공 선수 비교
                        ↓
             모델 성능 평가
                        ↓
                 모델 개선
                        ↓
             현재 유소년 선수
                        ↓
             Potential Ranking
                        ↓
             Scouting Recommendation
                        ↓
              Streamlit Dashboard
```

---

# 5. 선수 평가를 구성하는 주요 영역

선수 평가를 단순한 하나의 점수로 시작하기보다는 여러 평가 축으로 분리한다.

## 5.1 Performance

> **"지금 얼마나 잘하는가?"**

예시:

- Goals
- Assists
- xG
- xA
- Shots
- Key Passes
- Progressive Passes
- Progressive Carries
- Successful Dribbles
- Tackles
- Interceptions
- Aerial Duels
- Pressures
- Turnovers
- Minutes Played

---

## 5.2 Technical

> **"축구 기술적으로 얼마나 뛰어난가?"**

포지션에 따라 달라지지만 예시는 다음과 같다.

- 패스
- 드리블
- 퍼스트 터치
- 슈팅
- 결정력
- 크로스
- 볼 컨트롤
- 1v1
- 공중볼
- 볼 운반

---

## 5.3 Tactical

> **"경기를 얼마나 잘 이해하고 있는가?"**

예시:

- 공간 이해
- 포지셔닝
- 의사결정
- 전술 이해
- 압박 위치
- 오프 더 볼 움직임
- 빌드업 이해
- 수비 전환
- 공격 전환
- 포지션 수행 능력

---

## 5.4 Physical

예시:

- Height
- Weight
- Sprint
- Acceleration
- Agility
- Jump
- Endurance
- Strength
- Repeated Sprint Ability

유소년의 경우 절대적인 신체 능력만 보는 것이 아니라 **연령 대비 신체 능력**과 성장 추세를 고려하는 것이 중요하다.

---

## 5.5 Consistency

한 경기에서 잘하는 것과 시즌 전체에서 꾸준하게 잘하는 것은 다르다.

예시:

- 경기별 퍼포먼스 변동성
- 출전 경기 수
- 선발 출전 비율
- 연속적인 경기력
- 시즌별 성장 추세

---

## 5.6 Potential

> **"얼마나 성장할 수 있는가?"**

예시:

- 나이
- 최근 1~2년 경기력 상승률
- 출전시간 증가
- 기술 지표 상승률
- 팀 내 역할 변화
- 상위 연령대 적응
- 신체 성장 가능성
- 리그 수준 상승에 대한 적응

Potential은 현재 능력(Current Ability)과 반드시 분리해서 평가한다.

---

## 5.7 Professionalism / Mental

예시:

- 훈련 태도
- 코칭 수용성
- 자기관리
- 집중력
- 경쟁심
- 실수 후 반응
- 경기 외 행동
- 팀 적응

다만 이 영역은 정량화가 어려우므로 객관적 데이터와 주관적 평가를 분리하고, 실제 모델에서는 별도의 데이터가 있을 경우에만 제한적으로 활용한다.

---

# 6. 포지션별 평가가 필요한 이유

축구에서는 모든 선수에게 동일한 지표와 가중치를 적용하면 안 된다.

예를 들어 스트라이커에게 태클 성공률을 높은 비중으로 평가하거나, 센터백에게 득점 수를 높은 비중으로 평가하면 모델의 타당성이 떨어진다.

따라서 최소한 다음과 같이 포지션을 구분하는 것을 권장한다.

- GK
- CB
- FB/WB
- DM
- CM
- AM/Winger
- ST

프로젝트가 확장되면 세부 포지션을 추가한다.

---

# 7. 포지션별 핵심 지표 예시

## 7.1 Striker

- Goals / 90
- xG / 90
- Shots / 90
- Goals over/under xG
- xA
- Assists
- Progressive Carries
- Successful Dribbles
- Pressures / 90
- Pass completion
- Touches in penalty area

핵심 평가:

- 득점력
- 결정력
- 슈팅 생산성
- 박스 내 영향력
- 연계
- 압박

---

## 7.2 Winger / Attacking Midfielder

- Goals / 90
- Assists / 90
- xG / 90
- xA / 90
- Progressive Carries
- Successful Dribbles
- Key Passes
- Shot-Creating Actions
- Crosses
- Pressures

핵심 평가:

- 1v1
- 전진 능력
- 찬스 창출
- 득점 기여
- 공격 전개

---

## 7.3 Central Midfielder

- Pass completion
- Progressive Passes
- Progressive Carries
- Key Passes
- xA
- Tackles
- Interceptions
- Pressures
- Ball recoveries
- Turnovers

핵심 평가:

- 전진 패스
- 경기 조율
- 압박
- 볼 회수
- 공격·수비 전환

---

## 7.4 Defensive Midfielder

- Tackles
- Interceptions
- Ball Recoveries
- Pressures
- Defensive Duels
- Progressive Passes
- Pass completion
- Progressive Carries
- Turnovers

핵심 평가:

- 수비 기여
- 볼 회수
- 압박
- 빌드업

---

## 7.5 Centre Back

- Defensive Duels
- Tackles
- Interceptions
- Blocks
- Aerial Duels
- Errors
- Progressive Passes
- Progressive Carries
- Pass completion

핵심 평가:

- 대인 수비
- 위치 선정
- 공중볼
- 빌드업
- 전진 패스

---

# 8. 90분당 지표가 중요한 이유

단순 누적 기록만 사용하면 출전시간이 다른 선수를 공정하게 비교하기 어렵다.

예:

Player A

- 2,700분
- 15골

Player B

- 900분
- 8골

누적 골만 보면 A가 앞서지만, 90분당 생산성은 다를 수 있다.

따라서 가능한 지표는

> **per 90**

으로 변환한다.

예:

- Goals / 90
- xG / 90
- Assists / 90
- Progressive Passes / 90
- Progressive Carries / 90
- Tackles / 90
- Interceptions / 90
- Pressures / 90

---

# 9. Percentile을 활용한 선수 비교

단순히 원시 숫자를 비교하는 것보다 동일 리그·동일 포지션 집단에서 백분위를 계산하는 방식이 효과적이다.

예:

```text
Progressive Carries / 90

선수 A → 95 percentile
선수 B → 63 percentile
선수 C → 28 percentile
```

이는

> 해당 리그·포지션 선수 중 어느 정도 수준인가?

를 보여준다.

따라서 서로 단위가 다른 지표들을 하나의 평가 모델에 넣기가 쉬워진다.

---

# 10. 1차 모델: 사람이 설계한 Scouting Score

초기에는 머신러닝보다 **도메인 지식 기반 가중치 모델**을 먼저 만든다.

예시:

| 영역 | 가중치 |
|---|---:|
| Performance | 30% |
| Technical | 20% |
| Physical | 15% |
| Tactical | 15% |
| Potential | 15% |
| Mental/Professionalism | 5% |
| **합계** | **100%** |

다만 이 가중치는 절대적인 정답이 아니라 **초기 가설**이다.

포지션별로 가중치를 다르게 설정한다.

예:

### Striker

- Performance 35%
- Technical 20%
- Tactical 15%
- Physical 10%
- Potential 15%
- Professionalism 5%

### Centre Back

- Performance 25%
- Technical 15%
- Tactical 25%
- Physical 15%
- Potential 15%
- Professionalism 5%

---

# 11. 최종 Scouting Score

예:

```python
athlete_score = (
    performance_score * 0.30
    + technical_score * 0.20
    + physical_score * 0.15
    + tactical_score * 0.15
    + potential_score * 0.15
    + professionalism_score * 0.05
)
```

결과:

| 선수 | Performance | Technical | Physical | Tactical | Potential | 종합 |
|---|---:|---:|---:|---:|---:|---:|
| A | 87 | 84 | 81 | 88 | 94 | 87.4 |
| B | 91 | 86 | 85 | 78 | 76 | 84.7 |
| C | 79 | 88 | 88 | 83 | 96 | 86.0 |

이렇게 하면 "현재 경기력은 A가 가장 좋지만, 성장 가능성은 C가 가장 높다"는 분석이 가능해진다.

---

# 12. Current Ability와 Potential을 분리

이 프로젝트에서 가장 중요한 설계 중 하나다.

## Current Ability

> 지금 얼마나 잘하는가?

## Potential

> 향후 얼마나 성장할 가능성이 있는가?

예:

### Player A

Current Ability = 89

Potential = 74

→ 현재는 매우 뛰어나지만 성장 여지가 상대적으로 낮을 수 있음.

### Player B

Current Ability = 78

Potential = 94

→ 현재는 A보다 부족하지만 높은 성장 가능성을 가진 유망주.

에이전시나 유소년 스카우팅에서는 B 같은 선수가 중요한 타깃이 될 수 있다.

---

# 13. 2차 모델: 머신러닝 기반 Potential Prediction

1차 모델 이후 머신러닝 모델을 구축한다.

목표:

> **현재 시점의 정보만으로 향후 높은 수준의 프로 선수로 성장할 가능성을 추정한다.**

입력 변수 예시:

```text
Age
Position
Minutes
Goals/90
xG/90
xA/90
Progressive Passes
Progressive Carries
Successful Dribbles
Pressures
Tackles
Interceptions
Physical metrics
Recent performance growth
Team level
League level
```

출력:

```text
Potential Probability

Player A → 87%
Player B → 74%
Player C → 31%
```

이 값은 미래를 정확하게 예측하는 확률이 아니라,

> **과거 학습 데이터에서 관찰된 패턴을 기반으로 산출한 잠재력 추정치**

로 정의한다.

---

# 14. 어떤 머신러닝을 사용할 것인가?

처음부터 복잡한 딥러닝을 사용할 필요는 없다.

추천 순서:

### Baseline

- Logistic Regression
- Linear Regression

### Tree-based

- Decision Tree
- Random Forest
- Gradient Boosting
- XGBoost

### 이후 확장

- Neural Network
- Ensemble Model

유소년 선수의 "상위 수준 프로선수로 성장 여부" 같은 이진 문제라면 Logistic Regression이나 Tree-based classifier로 시작할 수 있다.

---

# 15. 가장 중요한 검증 방법: Historical Backtesting

사용자가 제안한 핵심 아이디어.

> **"이미 성공한 선수의 유소년 시절 데이터를 모델에 넣어보고, 모델이 과거의 성공 선수를 높은 점수로 평가하는지 확인한다."**

이 접근은 매우 좋은 검증 방법이다.

다만 성공한 선수만 넣어서는 안 된다.

---

# 16. 성공한 선수만 사용하면 안 되는 이유

예를 들어 성공한 선수 10명을 모델에 넣었더니 모두 85점 이상이라고 하자.

이것만으로는 모델이 좋은 모델이라고 할 수 없다.

왜냐하면 이미 성공한 선수만 선택했기 때문이다.

이는 다음과 같은 문제가 발생한다.

- Selection Bias
- Survivorship Bias

따라서 반드시

### 성공한 선수

+

### 평균적인 커리어를 가진 선수

+

### 기대만큼 성장하지 못한 선수

를 함께 넣어야 한다.

---

# 17. 역사적 선수 데이터를 이용한 Backtesting

예:

| 선수 | 평가 시점 | 당시 모델 점수 | 실제 커리어 |
|---|---|---:|---|
| 선수 A | 18세 | 93 | 월드클래스 |
| 선수 B | 19세 | 87 | 상위 프로 |
| 선수 C | 18세 | 61 | 2부/하위 수준 |
| 선수 D | 19세 | 48 | 프로 진출 실패 |
| 선수 E | 20세 | 90 | 국가대표 |

핵심 질문:

> **"모델은 당시에는 미래를 몰랐던 상태에서 성공 선수와 비성공 선수를 구분할 수 있었는가?"**

---

# 18. 유명 선수의 유소년 시절 데이터를 역으로 추적

예:

**18세 손흥민**

당시 이용 가능한 데이터만 사용

↓

Scouting Model

↓

Potential Score = 91

↓

실제 커리어:

함부르크 → 레버쿠젠 → 토트넘 → 세계 정상급 선수

이런 식으로 모델을 테스트한다.

단, 실제 프로젝트에서는 손흥민 같은 유명 선수만 사용하는 것이 아니라 충분한 표본의 선수 집단을 구성해야 한다.

---

# 19. "미래 정보"를 절대로 입력하면 안 된다

가장 중요한 통계적 원칙 중 하나다.

예를 들어 18세 선수의 잠재력을 평가하면서

> 25세 때의 경기 기록

을 입력하면 안 된다.

그러면 모델이 미래를 이미 알고 있는 것이 된다.

이를 **Data Leakage**라고 한다.

따라서 각 선수의 평가 시점에서

> **그 당시 실제로 알 수 있었던 정보만**

사용해야 한다.

예:

### 2015년 18세 선수

사용 가능:

- 2014/15 시즌 기록
- 당시 나이
- 당시 출전시간
- 당시 신체 데이터
- 당시 소속팀
- 당시 리그 수준

사용 불가:

- 2017년 기록
- 2020년 이적료
- 2024년 국가대표 기록

---

# 20. 시간순 검증(Out-of-Time Validation)

랜덤하게 데이터를 train/test로 나누는 것보다 축구 선수의 성장 예측에서는 시간 순서가 중요하다.

예:

```text
2010~2016
Training Data

2017~2019
Validation Data

2020~2022
Test Data
```

이렇게 하면 실제 스카우팅 상황과 유사해진다.

> 과거 데이터를 이용해 모델을 만들고, 이후 시점의 선수들에게 적용한다.

---

# 21. 모델의 성공을 어떻게 측정할 것인가?

단순히 Accuracy만 보면 안 된다.

예를 들어 모델이

> "성공 가능성 높은 선수"

라고 판단한 선수 중 실제 성공한 비율을 확인할 수 있다.

## Precision

High Potential로 분류된 선수 중 실제로 높은 수준까지 성장한 비율.

예:

```text
High Potential 선수 = 100명

실제 성공 = 68명

Precision = 68%
```

---

## Recall

실제로 성공한 선수 중 모델이 High Potential로 잡아낸 비율.

예:

```text
실제 성공 선수 = 100명

모델이 찾아낸 선수 = 82명

Recall = 82%
```

---

## F1 Score

Precision과 Recall을 종합해서 평가한다.

---

## ROC-AUC

성공/비성공 선수를 모델이 얼마나 잘 구분하는지 평가하는 지표로 사용할 수 있다.

---

# 22. False Positive / False Negative 분석

모델의 정확도만 보여주는 것보다 **틀린 사례를 분석하는 것이 훨씬 중요하다.**

## False Positive

모델:

> Potential 91

실제:

> 크게 성장하지 못함

가능한 이유:

- 부상
- 출전시간 부족
- 팀 환경
- 포지션 변경
- 심리적 요인
- 코칭 환경
- 데이터에 포함되지 않은 요소

---

## False Negative

모델:

> Potential 62

실제:

> 월드클래스 선수로 성장

가능한 이유:

- 당시 데이터에 나타나지 않은 성장 요인
- 이후 신체적 성장
- 환경 변화
- 전술 변화
- 새로운 포지션 적응
- 예상보다 빠른 기술 발전

이러한 실패 사례 분석을 통해 모델의 한계와 개선 방향을 찾을 수 있다.

---

# 23. 에이전시 관점에서 Marketability 추가

이 프로젝트를 단순한 축구 데이터 분석에서 **스포츠 에이전시 프로젝트**로 확장하는 핵심이다.

선수의 가치는 경기력만으로 결정되지 않는다.

예:

### Player A

Performance = 90

Marketability = 60

### Player B

Performance = 82

Marketability = 94

에이전시 입장에서는 두 선수의 전략이 다르다.

---

# 24. Marketability Score

예시:

- SNS 팔로워
- SNS 성장률
- Engagement Rate
- 콘텐츠 조회수
- 팬덤 규모
- 팬덤 성장률
- 국가/지역별 팬덤
- 미디어 노출
- 선수 스토리
- 이미지

---

# 25. Brand Fit

어떤 브랜드와 연결하기 좋은지를 평가한다.

예:

- 스포츠웨어
- 자동차
- 금융
- 식음료
- 게임
- 테크
- 여행
- 라이프스타일

선수별로 브랜드 적합도를 별도로 산출할 수 있다.

예:

```text
Sportswear Fit       93
Automotive Fit       72
Gaming Fit           86
Finance Fit          58
Technology Fit       81
```

---

# 26. Contentability

선수가 콘텐츠 자산으로 얼마나 활용될 수 있는지 평가한다.

예:

- 영상 콘텐츠 반응
- 인터뷰 매력도
- 팬과의 소통
- SNS 참여율
- 캐릭터성
- 스토리텔링 요소
- 콘텐츠 제작 빈도

---

# 27. 최종 Athlete Value Score

에이전시 버전에서는 다음처럼 확장할 수 있다.

```text
Performance
+
Potential
+
Marketability
+
Professionalism
+
Brand Fit
+
Contentability
+
Fan Value
```

예:

| 영역 | 점수 |
|---|---:|
| Performance | 84 |
| Potential | 92 |
| Technical | 86 |
| Tactical | 81 |
| Physical | 79 |
| Consistency | 88 |
| Marketability | 74 |
| Brand Fit | 91 |
| Contentability | 82 |
| **Athlete Value Score** | **87.2** |

---

# 28. 스카우팅 추천 시스템

최종적으로 프로그램이 단순히 점수를 출력하는 것이 아니라 **의사결정까지 지원**하도록 만든다.

예:

```text
Player A

Performance      84
Potential        92
Marketability    74
Brand Fit        91
Contentability   82

Scouting Score   87.2

Recommendation:
★★★★★

LONG-TERM SIGNING

추천 이유:
✓ 높은 성장 가능성
✓ 포지션 대비 높은 공격 기여
✓ 최근 경기력 상승세
✓ 스포츠웨어 브랜드 적합성 높음
✓ 콘텐츠 확장 가능성 높음

주의:
⚠ 신체 능력 개선 필요
⚠ 수비 기여도 평균 이하
```

---

# 29. Dashboard 구성

Streamlit 등을 활용하여 실제 웹앱 형태로 만든다.

## 첫 화면

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       FOOTBALL SCOUTING AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Search Player
[ Player Name ]

Position
[ Winger ▼ ]

League
[ League ▼ ]

Age
[ 18 - 23 ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 선수 상세 페이지

```text
Player A

Age: 19
Position: Winger
League: ...

Current Ability       84
Potential             92
Technical             86
Tactical              81
Physical              79
Consistency           88
Marketability         74

━━━━━━━━━━━━━━━━━━━━

SCOUTING SCORE
87.2

━━━━━━━━━━━━━━━━━━━━
```

---

## 시각화

- Radar Chart
- Percentile Chart
- Position Comparison
- League Average Comparison
- Age Comparison
- Development Trend
- Potential Probability
- Scouting Ranking

---

# 30. 기술 스택

처음부터 너무 어렵게 만들 필요는 없다.

## 데이터 처리

- Python
- Pandas
- NumPy

## 시각화

- Matplotlib
- Plotly

## 머신러닝

- Scikit-learn
- XGBoost

## 웹 대시보드

- Streamlit

## 데이터 저장

초기:

- CSV
- Excel

확장:

- SQLite
- PostgreSQL

---

# 31. 전체 개발 Pipeline

```text
                 DATA SOURCE
                     ↓
            Data Collection
                     ↓
             Data Cleaning
                     ↓
          Missing Value 처리
                     ↓
          Position Classification
                     ↓
             Per 90 계산
                     ↓
            Percentile 계산
                     ↓
          Feature Engineering
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
  Scouting Index            ML Potential Model
        ↓                         ↓
        └────────────┬────────────┘
                     ↓
             Athlete Score
                     ↓
          Historical Backtest
                     ↓
       Success / Failure Analysis
                     ↓
           Model Evaluation
                     ↓
            Model Improvement
                     ↓
             Current Players
                     ↓
             Ranking System
                     ↓
          Scouting Recommendation
                     ↓
          Streamlit Dashboard
```

---

# 32. 프로젝트 개발 순서

## STEP 1 — 축구 데이터 확보

선수 데이터 확보.

필요한 기본 데이터:

- 선수 이름
- 나이
- 포지션
- 출전시간
- 득점
- 도움
- xG
- xA
- 패스
- 전진 패스
- 전진 운반
- 드리블
- 태클
- 인터셉트
- 압박
- 공중볼
- 팀
- 리그

---

## STEP 2 — 데이터 전처리

- 결측치 처리
- 중복 데이터 처리
- 포지션 정리
- 리그 정리
- 출전시간 필터링
- Per 90 계산
- Percentile 계산

---

## STEP 3 — 포지션별 모델

처음에는 모든 포지션을 다 하지 말고 하나로 시작한다.

추천:

> **Winger / Attacking Midfielder**

또는

> **Striker**

이후:

- Midfielder
- Defender
- Goalkeeper

순으로 확장한다.

---

# 33. 왜 공격수/윙어부터 시작하는가?

공격 포지션은 비교적 정량화하기 쉽다.

예:

- Goals
- xG
- Assists
- xA
- Shots
- Dribbles
- Progressive Carries
- Key Passes

등 데이터가 풍부하다.

반면 수비수의 위치 선정이나 공간 통제 같은 요소는 단순한 박스스코어 데이터로 평가하기 어렵다.

따라서 **첫 번째 MVP는 공격수/윙어**가 적합하다.

---

# 34. STEP 4 — Scouting Index 만들기

초기에는 직접 설계한 가중치 모델을 만든다.

예:

```text
Performance      35%
Technical        20%
Tactical         15%
Physical         10%
Potential        15%
Consistency       5%
```

이후 백테스팅 결과에 따라 가중치를 조정한다.

---

# 35. STEP 5 — Historical Backtest

과거 선수 데이터를 사용한다.

대상:

### 성공 선수

- 세계 정상급
- 국가대표
- 상위 리그 주전

### 중간 선수

- 상위/중위권 프로
- 2부리그
- 제한적 출전

### 저성장 선수

- 프로 진출 실패
- 낮은 수준에서 커리어 종료
- 기대 이하 성장

가능한 한 균형 있게 구성한다.

---

# 36. STEP 6 — ML Potential Model

목표 변수를 정의한다.

예:

```text
Target = 1

향후 5년 내
특정 수준 이상의 프로 선수로 성장
```

또는 여러 등급으로 나눌 수도 있다.

```text
0 = 프로 수준 미달
1 = 하위 프로
2 = 중상위 프로
3 = 상위 리그 주전
4 = 엘리트
```

프로젝트의 데이터가 충분하다면 다중 분류로 확장한다.

---

# 37. STEP 7 — 검증

평가:

- Precision
- Recall
- F1
- ROC-AUC
- Confusion Matrix
- Calibration
- Top-K Hit Rate

특히 스카우팅에서는

> **Top 10 / Top 20 중 실제 성공 선수 몇 명을 찾아냈는가?**

를 별도로 보여주는 것이 좋다.

---

# 38. Top-K Scouting Evaluation

예:

모델이 18~20세 선수 중

### Top 10

을 추천했다고 하자.

그중

- 실제 상위 프로 진출 = 7명

이면

> **Top-10 Hit Rate = 70%**

이런 방식으로 스카우팅 관점의 성능을 평가할 수 있다.

---

# 39. STEP 8 — 현재 유소년 선수에게 적용

모델이 어느 정도 검증된 후 현재 선수들에게 적용한다.

예:

```text
U18 Winger Ranking

1. Player A — 91.4
2. Player B — 89.7
3. Player C — 87.8
4. Player D — 84.1
5. Player E — 82.9
```

그리고 각 선수에 대해

- 강점
- 약점
- 잠재력
- 추천 이유
- 리스크

를 제공한다.

---

# 40. STEP 9 — 에이전시 기능 추가

스카우팅 점수만으로 끝내지 않는다.

### Agent Recommendation

예:

```text
Player A

Sporting Value       91
Potential             94
Marketability         72
Brand Fit             88

Agency Recommendation:

HIGH PRIORITY

Recommended Strategy:
1. 장기 계약 검토
2. 개인 브랜드 구축
3. 스포츠웨어 스폰서 연결
4. SNS 콘텐츠 강화
5. 해외 진출 모니터링
```

이렇게 하면 **스포츠 에이전시의 실제 의사결정 지원 시스템**이라는 성격이 강해진다.

---

# 41. 모델의 한계도 반드시 명시한다

이 프로젝트에서 신뢰도를 높이는 방법은 모델을 과장하지 않는 것이다.

## 한계 1

축구선수의 모든 능력이 데이터로 측정되지는 않는다.

특히:

- 공간 이해
- 의사결정
- 리더십
- 정신력
- 훈련 태도

등은 정량화하기 어렵다.

---

## 한계 2

부상은 정확하게 예측하기 어렵다.

---

## 한계 3

팀 전술의 영향을 받는다.

같은 선수라도 팀 전술에 따라 통계가 크게 달라질 수 있다.

---

## 한계 4

리그 수준의 차이가 존재한다.

K리그와 EPL의 동일한 통계를 그대로 비교할 수 없다.

따라서 리그 강도 보정이 필요할 수 있다.

---

## 한계 5

유소년 데이터는 표본이 작을 수 있다.

---

## 한계 6

미래는 모델이 완벽하게 예측할 수 없다.

따라서 결과를

> "미래를 예측하는 AI"

가 아니라

> **"과거 데이터에서 관찰된 패턴을 기반으로 잠재력을 추정하고 스카우팅 의사결정을 지원하는 시스템"**

으로 정의한다.

---

# 42. 데이터의 신뢰성

모델보다 중요한 것이 데이터다.

가능하다면:

- 공식 경기 기록
- 신뢰할 수 있는 통계 제공업체
- 공식 리그/클럽 데이터
- 신뢰할 수 있는 스카우팅 데이터

를 사용한다.

특히 과거 유소년 선수의 데이터는 확보가 어려울 수 있으므로, 실제 프로젝트에서는 **데이터 확보 가능성 자체가 프로젝트 범위를 결정하는 핵심 요소**가 된다.

---

# 43. 기존 스카우팅 플랫폼과의 관계

이미 시장에는 선수 스카우팅 및 영상·데이터 분석 플랫폼이 존재한다.

예를 들어:

- Hudl
- Wyscout
- StatsBomb
- FastModel/FastRecruit
- 기타 전문 데이터 플랫폼

이러한 시스템이 존재한다는 것은 오히려 프로젝트의 당위성을 높여준다.

다만 이 프로젝트의 목표는 기존 플랫폼을 그대로 복제하는 것이 아니라,

> **공개 또는 합법적으로 확보 가능한 데이터를 활용하여 개인 수준에서 재현 가능한 '선수 발굴 모델'을 구축하는 것**

이다.

---

# 44. 이 프로젝트가 포트폴리오에서 보여주는 것

이 프로젝트 하나로 다음 능력을 보여줄 수 있다.

## 스포츠 도메인 지식

- 포지션별 평가
- 축구 통계 해석
- 선수 발굴 논리

## 데이터 분석

- 데이터 수집
- 전처리
- 정규화
- Percentile
- Feature Engineering

## 프로그래밍

- Python
- Pandas
- NumPy

## 머신러닝

- Classification
- Prediction
- Model Evaluation

## 시각화

- Radar Chart
- Ranking
- Percentile
- Trend

## 서비스 개발

- Streamlit Dashboard

## 스포츠 비즈니스

- 에이전시
- 선수 가치
- 시장성
- 브랜드 적합성
- 스폰서십

---

# 45. 포트폴리오에서 강조할 핵심 스토리

단순히

> "Python으로 축구선수 점수를 계산했습니다."

라고 설명하지 않는다.

다음과 같이 설명한다.

> **"축구 선수 스카우팅 과정에서 발생하는 주관적 판단을 데이터 기반으로 보조할 수 있는 모델을 설계했습니다. 포지션별 경기력 지표를 표준화하고, Current Ability와 Potential을 분리하여 선수의 현재 경기력과 성장 가능성을 평가했습니다. 또한 과거 선수들의 초기 커리어 데이터를 활용한 Historical Backtesting을 통해 모델의 실제 선수 발굴 가능성을 검증하고, 이후 머신러닝 기반 잠재력 예측 모델과 스카우팅 대시보드로 확장했습니다."**

이게 프로젝트의 핵심 스토리다.

---

# 46. 최종 프로젝트 구조

```text
Football Talent Identification
        │
        ├── 01. Problem Definition
        │
        ├── 02. Literature / Industry Research
        │
        ├── 03. Data Collection
        │
        ├── 04. Data Cleaning
        │
        ├── 05. Position Classification
        │
        ├── 06. Per 90 / Percentile
        │
        ├── 07. Scouting Index
        │
        ├── 08. Potential Model
        │
        ├── 09. Historical Backtesting
        │
        ├── 10. ML Model
        │
        ├── 11. Model Evaluation
        │
        ├── 12. Error Analysis
        │
        ├── 13. Athlete Value
        │
        ├── 14. Marketability
        │
        ├── 15. Current Youth Ranking
        │
        ├── 16. Scouting Recommendation
        │
        └── 17. Streamlit Dashboard
```

---

# 47. MVP(Minimum Viable Product)

처음부터 모든 기능을 만들지 않는다.

## MVP Version 1

**대상:**

> 유럽 축구 18~23세 Winger / Striker

### 기능

1. 선수 데이터 입력
2. 데이터 정제
3. Per 90
4. Percentile
5. 포지션별 Scouting Score
6. 선수 Ranking
7. Radar Chart
8. 기본 Streamlit Dashboard

---

# 48. Version 2

추가:

1. Historical Backtesting
2. 성공/비성공 선수 비교
3. Precision
4. Recall
5. F1
6. ROC-AUC
7. Confusion Matrix
8. Top-K Hit Rate

---

# 49. Version 3

추가:

1. ML Potential Model
2. 성장 가능성 Probability
3. Future Outcome Prediction
4. Feature Importance
5. False Positive 분석
6. False Negative 분석

---

# 50. Version 4

에이전시 모델로 확장:

1. Marketability
2. SNS
3. Brand Fit
4. Contentability
5. Fan Value
6. Athlete Value Score
7. Sponsorship Recommendation
8. Agency Recruitment Recommendation

---

# 51. 최종 결과물 예시

최종적으로 사용자가 웹사이트에 들어가서:

```text
[Position]
Winger

[Age]
18-21

[League]
Select

[Minimum Minutes]
500
```

를 선택하면,

```text
━━━━━━━━━━━━━━━━━━━━━━
TOP PROSPECTS
━━━━━━━━━━━━━━━━━━━━━━

1. Player A
Scouting Score 92.1
Potential 96

2. Player B
Scouting Score 89.7
Potential 91

3. Player C
Scouting Score 87.4
Potential 94
```

가 나오고,

선수를 클릭하면:

```text
PLAYER A

Current Ability      86
Potential             96
Technical             89
Tactical              82
Physical              84
Consistency           81

Performance           88
Marketability         74
Brand Fit             91

━━━━━━━━━━━━━━━━━━━━

SCOUTING RECOMMENDATION

★★★★★
HIGH PRIORITY

Strengths
• 1v1
• Progressive carrying
• Chance creation
• High development trajectory

Risks
• Defensive contribution
• Limited senior minutes

Agency Strategy
• Long-term monitoring
• Individual branding
• Sportswear partnership potential
```

처럼 나타나는 것이다.

---

# 52. 프로젝트의 최종 가치

이 프로젝트의 가장 큰 장점은 하나의 분야에만 걸쳐 있지 않다는 것이다.

```text
               FOOTBALL
                  │
      ┌───────────┼───────────┐
      ↓           ↓           ↓
   Scouting    Data       Marketing
      │           │           │
      ↓           ↓           ↓
  선수발굴     Python      브랜드
  잠재력       ML          SNS
  포지션       통계        스폰서십
      │           │           │
      └───────────┼───────────┘
                  ↓
        Athlete Intelligence
                  ↓
        Agency Decision Support
```

따라서 스포츠산업 취업에서

- 스포츠 마케팅
- 스포츠 에이전시
- 선수 매니지먼트
- 스포츠 데이터 분석
- 스포츠테크
- 프로구단
- 스포츠 대행사

등 여러 방향으로 연결할 수 있다.

---

# 53. 가장 중요한 개발 철학

이 프로젝트는 **"AI를 사용하기 위한 프로젝트"가 아니다.**

핵심은:

> **축구에 대한 도메인 지식을 데이터로 구조화하고, 그 데이터가 실제 선수 발굴에 유용한지를 검증하는 것**

이다.

따라서 순서는 반드시:

```text
축구 지식
   ↓
평가 기준 설계
   ↓
데이터
   ↓
통계 모델
   ↓
과거 검증
   ↓
머신러닝
   ↓
실제 스카우팅
```

이어야 한다.

AI는 그 이후의 도구다.

---

# 54. 최종 프로젝트 한 문장

> **"유소년 및 초기 프로 축구 선수의 경기력 데이터를 포지션별로 표준화하고, Current Ability와 Potential을 분리하여 선수의 미래 성장 가능성을 평가한 뒤, 과거 선수 데이터를 활용한 Historical Backtesting과 머신러닝을 통해 모델의 유효성을 검증하고, 최종적으로 유망주 발굴과 선수 영입 의사결정을 지원하는 데이터 기반 Football Scouting Intelligence System을 구축한다."**

---

# 55. 앞으로 실제로 진행할 순서

다음 작업은 코딩부터 시작하지 않는다.

### 1단계
**실제로 확보할 수 있는 축구 선수 데이터를 조사한다.**

### 2단계
**데이터가 충분히 존재하는 포지션을 선정한다.**

### 3단계
**평가 대상 리그와 연령대를 결정한다.**

### 4단계
**성공/비성공 선수의 Historical Dataset을 구성할 수 있는지 확인한다.**

### 5단계
**Scouting Score의 초기 지표와 가중치를 설계한다.**

### 6단계
**Python으로 MVP를 제작한다.**

### 7단계
**과거 선수 데이터로 Backtesting한다.**

### 8단계
**모델의 Precision / Recall / F1 / ROC-AUC / Top-K 성능을 평가한다.**

### 9단계
**False Positive / False Negative를 분석한다.**

### 10단계
**머신러닝 Potential Model을 추가한다.**

### 11단계
**현재 유소년 선수에게 모델을 적용한다.**

### 12단계
**Streamlit Dashboard를 완성한다.**

### 13단계
**Marketability / Brand Fit / Agency Recommendation 기능을 추가한다.**

---

# 56. 프로젝트의 최종 목표

최종 목표는 단순한 선수 평가 프로그램이 아니다.

> **"스카우터의 경험과 축구 도메인 지식을 데이터로 구조화하고, 과거 데이터를 통해 검증한 뒤, 미래의 유망주 발굴과 선수 관리·마케팅 의사결정을 지원하는 개인 수준의 스포츠 인텔리전스 시스템"**

을 만드는 것이다.

이 프로젝트가 완성되면 단순한 코딩 결과물이 아니라,

**① 축구 전문성**

**② 데이터 분석 능력**

**③ Python/ML 역량**

**④ 스포츠 비즈니스 이해**

**⑤ 스포츠 에이전시 업무 이해**

를 하나의 결과물로 증명하는 포트폴리오 프로젝트가 된다.
