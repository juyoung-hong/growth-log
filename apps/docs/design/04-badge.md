# Badge

**원천 파일**: [`apps/frontend/src/shared/ui/badge/`](../../frontend/src/shared/ui/badge/) (`index.ts` + `Badge.vue`)
**전제**: [01-colors.md](./01-colors.md)의 팔레트와 접근성 원칙, [03-button.md](./03-button.md)의 변형 축 개념, [02-typography.md](./02-typography.md)의 크기 스케일을 먼저 읽는다.

## 왜 이렇게 만들었나

인터페이스(어떤 prop이 있고 각각 무슨 값을 받는지)는 [TDS Badge 문서](https://tossmini-docs.toss.im/tds-mobile/components/badge/)를 그대로 따른다. 값(색·크기)은 이 프로젝트의 팔레트와 타이포 스케일에서 새로 계산했다.

## 인터페이스

TDS 문서에 실린 `BadgeProps`는 다음 세 가지가 전부다. 다른 prop(아이콘, 클릭 핸들러 등)은 원본에 없다.

| Prop | 타입 | 필수 | 기본값 |
|---|---|---|---|
| `variant` | `"fill"` \| `"weak"` | 예 | — (호출부에서 지정. 이 구현은 `weak`) |
| `color` | 아래 "color 값" 참고 | 예 | — (호출부에서 지정. 이 구현은 `grey`) |
| `size` | `"xsmall"` \| `"small"` \| `"medium"` \| `"large"` | 예 | — (호출부에서 지정. 이 구현은 `medium`) |

TDS 문서는 세 prop 모두 "필수"로 표시하고 기본값을 명시하지 않는다. 이 구현은 셋 다 `defaultVariants`로 기본값을 지정해 뒀다 — 색을 지정하지 않고 `<Badge>상태</Badge>`처럼 최소한으로 써도 동작하게 하기 위해서다. 그 외 세 축의 **이름과 구조는 TDS와 완전히 같다.**

### `color` 값 — TDS 6색이 아니라 이 프로젝트 팔레트 13색 전부

TDS 원본은 `color`를 6개 값(`blue`/`teal`/`green`/`red`/`yellow`/`elephant`)으로 제한한다. 이 구현은 좁히지 않고 **[01-colors.md](./01-colors.md)의 팔레트 13색 전부**를 지원한다.

```
blue | red | pink | purple | violet | indigo | cyan | teal | green | lime | yellow | orange | grey
```

`elephant`(TDS의 회색조 이름)는 이 프로젝트의 이름 규칙에 따라 `grey`로 옮겼다. 그 외 12색은 `01-colors.md`에 이미 정의된 팔레트를 그대로 쓴다.

**왜 6색으로 좁히지 않았나** — 이 프로젝트의 컬러 시스템은 TDS와 달리 애초에 13색 130토큰 전부를 등록해 둔다(01-colors.md). Badge의 `color`가 그중 6개만 받는다면, 팔레트에는 있는데 Badge로는 못 쓰는 색이 생긴다. 지금 실제로 쓰는 색은 여전히 blue·green·yellow·purple 정도뿐이지만, 나머지도 컬러 팔레트와 마찬가지로 **필요할 때 바로 쓸 수 있게** 미리 구현해 둔다.

## Badge는 상태 라벨이지 액션이 아니다

Button과 가장 다른 지점이다. **`hover`나 `active` 스타일을 넣지 않는다.** Badge는 클릭할 수 있는 요소가 아니라 "이 항목은 진행중이다" 같은 상태를 눈으로 읽는 라벨이다. 눌리는 것처럼 보이면 사용자가 클릭을 시도하게 되므로 의도적으로 상호작용 신호를 전부 뺐다. TDS 문서에도 이 세 prop 외에 클릭 관련 prop이 없다 — 원본부터 액션 컴포넌트로 설계되지 않았다.

## 크기 — TDS 4단계 전부 구현

| 크기 | 높이 | 좌우 padding | 글자(02-typography.md 토큰) |
|---|---|---|---|
| `xsmall` | 18px | 4px | `text-11` (11px) |
| `small` | 20px | 6px | `text-13` (13px) |
| `medium` | 24px | 8px | `text-13` (13px) |
| `large` | 28px | 10px | `text-15` (15px) |

`xsmall`은 처음엔 구현하지 않았었다 — 당시 타이포 스케일의 최소 토큰이 13px이라 그보다 작은 크기를 만들 수 없었기 때문이다. 이후 타이포그래피 문서화 작업([02-typography.md](./02-typography.md))에서 TDS의 보조 토큰(sub 1~13)까지 전부 등록하면서 11px·12px 토큰이 생겼고, 이번에 `xsmall`도 채웠다. **배지 높이(18px)가 `text-11`의 행간(16.5px)보다 커야** 글자가 위아래로 눌리지 않는다 — 그래서 18px을 골랐다(`h-4`=16px는 부족).

**모서리 반지름은 6px을 직접 적는다.** Button과 같은 이유다 — `theme.css`의 `--radius`는 카드 기준(20px)이라, `rounded-md`(`calc(--radius - 2px)` = 18px)를 그대로 쓰면 배지가 알약처럼 보인다.

## 색 조합 — 13색 × 2variant, 실측 대비비 전부

| variant | color | 배경 | 글자 | 대비비 |
|---|---|---|---|---|
| `fill` | `blue` | blue-800 | white | 5.02 |
| `fill` | `red` | red-800 | white | 4.51 |
| `fill` | `pink` | pink-700 | white | 4.62 |
| `fill` | `purple` | purple-700 | white | 4.85 |
| `fill` | `violet` | violet-600 | white | 4.95 |
| `fill` | `indigo` | indigo-700 | white | 4.98 |
| `fill` | `cyan` | cyan-900 | white | 5.59 |
| `fill` | `teal` | teal-900 | white | 5.00 |
| `fill` | `grey` | grey-700 | white | 8.18 |
| `fill` | `green` | green-900 | white | **4.37 — AA 미달** |
| `fill` | `lime` | lime-900 | white | **3.69 — AA 미달** |
| `fill` | `yellow` | yellow-900 | white | **3.00 — AA 미달** |
| `fill` | `orange` | orange-900 | white | **4.30 — AA 미달** |
| `weak` | `blue` | blue-100 | blue-900 | 4.93 |
| `weak` | `red` | red-100 | red-900 | 4.51 |
| `weak` | `pink` | pink-100 | pink-900 | 5.80 |
| `weak` | `purple` | purple-100 | purple-900 | 5.59 |
| `weak` | `violet` | violet-100 | violet-900 | 5.39 |
| `weak` | `indigo` | indigo-100 | indigo-900 | 5.34 |
| `weak` | `cyan` | cyan-100 | cyan-900 | 4.77 |
| `weak` | `grey` | grey-100 | grey-900 | 13.87 |
| `weak` | `teal` | teal-100 | teal-900 | **4.33 — AA 미달** |
| `weak` | `green` | green-100 | green-900 | **3.81 — AA 미달** |
| `weak` | `lime` | lime-100 | lime-900 | **3.33 — AA 미달** |
| `weak` | `yellow` | yellow-100 | yellow-900 | **2.69 — AA 미달** |
| `weak` | `orange` | orange-100 | orange-900 | **3.62 — AA 미달** |

각 색은 다음 공식으로 값을 골랐다.

- **`fill`**: "흰 글자와 4.5:1을 넘기는 가장 얕은 단계 + 흰 글자"가 원칙이다. 팔레트마다 명도 분포가 달라 필요한 최소 단계가 색마다 다르다 — violet은 600에서 이미 넘기고, cyan·teal은 900까지 가야 한다.
- **`weak`**: "100단계 배경 + 같은 계열 900단계 글자"가 원칙이다. 13색 전부 예외 없이 이 공식을 쓴다.

### green·lime·yellow·orange는 왜 대비가 부족한데도 고치지 않았나

`01-colors.md`에서 이미 다룬 결정을 그대로 적용한 것이다. 이 네 색은 Open Color 팔레트에서 가장 어두운 900단계로도 흰 글자·같은 계열 진한 글자 어느 쪽과도 4.5:1을 채우지 못한다. 이 색들만 규칙을 바꿔(예: 글자를 `grey-900`으로 바꿔 대비를 억지로 맞추는) 예외를 두는 방법도 있었지만, **의도적으로 채택하지 않았다.**

이유는 하나다 — 색마다 규칙이 갈리면, Badge를 쓰는 사람도 만드는 사람도 "이 색은 왜 다르지"를 매번 다시 확인해야 한다. 그 비용이 특정 조합의 낮은 대비 수치 하나보다 크다고 판단했다. 대신 **대비가 실제로 문제가 되는 화면**(예: 저장공간 사용량 경고처럼 사용자가 놓치면 안 되는 정보)에서는 Badge의 정해진 색 중 하나를 억지로 끌어다 쓰지 않고, 그 용도에 맞는 별도 색을 새로 고른다. 저장공간 경고가 Badge를 쓰지 않고 `--color-warning-*`이라는 전용 토큰(orange, weak 공식)을 따로 만든 것이 그 예다 — 자세한 내용은 `01-colors.md`의 "접근성" 절에 있다.

## Badge는 업무 의미를 모른다

`badge/index.ts`의 `color` 축은 `blue`/`green`/`red`처럼 **색 이름 그대로**다. `progress`(진행중)나 `done`(완료) 같은 업무 상태 이름을 색 이름과 섞지 않는다.

```ts
// ❌ Badge가 업무 개념을 안다 — 이렇게 만들지 않는다
<Badge variant="progress">진행중</Badge>

// ✅ Badge는 색만 안다. "진행중 = blue"라는 매핑은 다른 레이어가 갖는다
<Badge color="blue">진행중</Badge>
```

이 프로젝트는 FSD(Feature-Sliced Design)를 쓰고, `shared/ui`(Badge가 속한 레이어)는 업무 개념을 알아서는 안 된다는 규칙이 있다. "어떤 상태가 어떤 색인가"의 매핑은 `entities` 레이어가 갖는다. 이 분리 덕분에, 다른 프로젝트에서 Badge 컴포넌트 자체(색·크기·대비 규칙)를 그대로 재사용할 수 있다 — 업무 상태 이름이 프로젝트마다 달라도 Badge 코드는 바뀔 필요가 없다.

## 다른 프로젝트에서 재사용하는 방법

1. `01-colors.md`의 팔레트, `03-button.md`의 2축 구조, `02-typography.md`의 크기 스케일을 먼저 옮긴다.
2. 원본 디자인 시스템(TDS 등)의 **인터페이스**(prop 이름·타입)는 그대로 따른다 — 재구현할 때 API가 문서와 달라지면 그 문서를 참고 자료로 쓸 수 없게 된다.
3. **값(색상 목록 등)은 원본이 정한 범위로 좁히지 않는다.** 이 프로젝트의 팔레트가 원본보다 넓으면, 컴포넌트도 그 넓은 범위를 전부 지원한다 — 지금 안 쓰는 값이라도 구현은 미리 해 둔다. 원본에 있는데 이 프로젝트 팔레트에 없는 색(TDS의 `teal`처럼)은 팔레트를 먼저 확장하고 나서 추가한다.
4. Badge에는 상호작용 스타일(`hover`/`active`)을 절대 넣지 않는다 — 상태 라벨이라는 역할을 코드로도 강제하는 것이다.
5. `fill`은 "가장 얕게 4.5:1을 넘기는 단계 + 흰 글자", `weak`는 "100단계 배경 + 같은 계열 900단계 글자"를 기본 공식으로 삼는다.
6. 색상마다 대비가 다르게 나오는 건 정상이다 — 팔레트 자체의 명도 분포가 색상마다 다르기 때문이다. 문제는 그중 일부가 4.5:1을 못 넘길 때 **그 색만 다른 규칙을 쓸지, 대비를 감수하고 원칙을 지킬지**를 정하는 것이다. 이 프로젝트는 후자를 택했지만, 어느 쪽을 택하든 판단 근거를 코드 주석에 남긴다.
7. 업무 개념(상태 이름 등)과 색 이름을 분리한다. Badge 컴포넌트는 색만 알고, 상태→색 매핑은 그 컴포넌트를 쓰는 상위 레이어가 갖는다.
