# ProgressBar

**원천 파일**: [`apps/frontend/src/shared/ui/progress/`](../../frontend/src/shared/ui/progress/) (`Progress.vue`)
**전제**: [01-colors.md](./01-colors.md)의 팔레트와 접근성 원칙, [04-badge.md](./04-badge.md)의 "우리 팔레트 전체를 지원하는 hue 기반 color 축" 개념을 먼저 읽는다.

## 왜 이렇게 만들었나

인터페이스는 [TDS ProgressBar 문서](https://tossmini-docs.toss.im/tds-mobile/components/progress-bar/)를 따른다. 값(색·두께)은 이 프로젝트의 팔레트에서 새로 계산했다.

## 인터페이스

TDS 문서에 실린 `ProgressBarProps`는 다음과 같다.

| Prop | 타입 | 필수 | 기본값 |
|---|---|---|---|
| `progress` | `number` (0.0~1.0) | 예 | — |
| `size` | `"light"` \| `"normal"` \| `"bold"` | 예 | `normal` |
| `color` | 임의의 CSS 색상 문자열 | 아니오 | `colors.blue400` |
| `animate` | `boolean` | 아니오 | `false` |
| `className` | `string` | 아니오 | — |

`size`는 이미 구현돼 있었다. 이번에 **`color`와 `animate`를 추가**했다. `progress`는 TDS와 다른 규약(`modelValue`, 0~100)을 그대로 유지한다. `className`은 Vue의 attrs 자동 전달로 이미 해결되므로 별도로 만들지 않는다 — Button의 `htmlStyle`과 같은 이유다.

### `progress`(0.0~1.0) 대신 `modelValue`(0~100)를 쓰는 이유

이 프로젝트가 기반으로 쓰는 [Reka UI](https://reka-ui.com/)의 `ProgressRoot`는 애초에 0~100 규약이다. 백엔드 API(`TaskGroupProgress.percent`)도 이미 0~100으로 내려준다. TDS의 0.0~1.0 규약을 따르려면 양쪽 다 있는 값을 굳이 한 번 더 나누고 곱해야 하는데, 그럴 이유가 없어서 Reka·백엔드와 같은 0~100을 그대로 썼다. TDS 인터페이스를 기계적으로 베끼지 않고, 이미 맞아떨어지는 규약이 있으면 그걸 따른다.

### `color`가 열린 문자열이 아니라 13개 hue로 닫힌 이유

TDS의 `color`는 아무 CSS 색상 값이나 받는 열린 `string`이다. 이 프로젝트는 컴포넌트 코드에 리터럴 hex를 쓰지 않고 팔레트 토큰으로만 색을 고른다는 원칙이 있다([01-colors.md](./01-colors.md)). 그래서 `color`를 [04-badge.md](./04-badge.md)의 `color`와 **완전히 같은 13개 hue 이름**으로 닫힌 목록을 만들었다.

```
blue | red | pink | purple | violet | indigo | cyan | teal | green | lime | yellow | orange | grey
```

Button의 `color`(primary/danger/light/dark, 역할 이름)와 달리 ProgressBar의 `color`는 Badge와 같은 **hue 이름**을 쓴다 — 진행 막대가 어떤 의미든(기본 진행률, 경고, 카테고리별 색 구분) 특정 hue를 그대로 가리켜야 하는 경우가 많아서다. 기본값은 `blue`다.

## 실제로 이 prop이 없어서 생겼던 문제

`color`가 없던 시절, 저장공간 게이지(`StorageGauge.vue`)가 임계치 초과 시 막대를 빨갛게 바꿔야 했는데 방법이 없어 이렇게 우회하고 있었다.

```vue
<!-- ❌ 이전: 컴포넌트 내부 DOM 구조에 직접 셀렉터로 침투 -->
<Progress :class="warning ? '[&>[data-slot=progress-indicator]]:bg-destructive' : undefined" />
```

`data-slot` 속성이 바뀌거나 내부 마크업이 바뀌면 조용히 깨지는 코드였다. `color`를 추가하면서 정리했다.

```vue
<!-- ✅ 지금: 컴포넌트가 제공하는 prop으로 -->
<Progress :color="warning ? 'red' : 'blue'" />
```

## 두께(`size`) — TDS 3단계 그대로

| 값 | 클래스 | 높이 |
|---|---|---|
| `light` | `h-0.5` | 2px |
| `normal`(기본) | `h-1` | 4px |
| `bold` | `h-1.5` | 6px |

## 색 조합 — 13색, 실측 대비비 전부

막대와 트랙(`bg-grey-200`)의 명도 대비를 계산했다. 텍스트가 아니라 그래픽 요소이므로 WCAG 기준은 **3.0:1**이다(텍스트의 4.5:1보다 낮다).

| color | 막대 클래스 | 대비비 |
|---|---|---|
| `blue`(기본) | `bg-blue-700` | 3.54 |
| `red` | `bg-red-700` | 3.24 |
| `pink` | `bg-pink-600` | 3.15 |
| `purple` | `bg-purple-600` | 3.39 |
| `violet` | `bg-violet-500` | 3.60 |
| `indigo` | `bg-indigo-500` | 3.10 |
| `cyan` | `bg-cyan-800` | 3.67 |
| `teal` | `bg-teal-800` | 3.33 |
| `green` | `bg-green-900` | 3.68 |
| `lime` | `bg-lime-900` | 3.11 |
| `orange` | `bg-orange-800` | 3.02 |
| `grey` | `bg-grey-700` | 6.90 |
| `yellow` | `bg-yellow-900` | **2.53 — AA 미달** |

각 색은 "트랙과 3.0:1을 넘기는 가장 얕은 단계"를 쓴다 — [04-badge.md](./04-badge.md)의 fill 공식과 같은 방식이다. 예외는 둘.

- **`blue`만 최소 통과 단계(600, 3.00)보다 한 단계 위(700)를 쓴다.** 정확히 3.00은 반올림 오차 하나로 기준 밑으로 떨어질 수 있는 경계값인 데다, `blue`가 기본값이라 다른 12색보다 훨씬 자주 쓰이므로 여유를 뒀다.
- **`yellow`는 900단계로도 3.0을 못 넘긴다(2.53).** [04-badge.md](./04-badge.md)에서 green·yellow에 적용한 것과 같은 판단이다 — 이 색만 규칙을 바꾸지 않고, 대비 부족을 감수하고 같은 공식(트랙 대비 가장 진한 단계)을 그대로 쓴다.

## animate — 값이 바뀔 때 부드럽게 움직일지

```
animate: boolean = false
```

TDS 기본값(`false`)을 그대로 따른다. 이전 구현은 `transition-all`을 조건 없이 걸어 뒀는데, 목록 화면에 진행률 막대가 여러 개 한꺼번에 그려지면 전부 애니메이션되어 산만하다. `animate="true"`를 명시한 곳에서만 부드럽게 움직인다.

## 다른 프로젝트에서 재사용하는 방법

1. `01-colors.md`의 팔레트, `04-badge.md`의 hue 기반 `color` 축 개념을 먼저 옮긴다.
2. 원본 문서의 진행률 값 규약(0.0~1.0 등)을 기계적으로 따르지 않는다. 이 프로젝트가 이미 쓰는 기반 라이브러리·백엔드 API의 규약이 있다면 그쪽에 맞춘다 — 서로 다른 두 규약을 계속 변환하는 코드를 만들 이유가 없다.
3. `color`가 열린 문자열(임의 CSS 값)이면 이 프로젝트의 팔레트 토큰으로 닫힌 목록으로 바꾼다. 그 색이 **hue를 가리키는지**(Badge·ProgressBar처럼) **역할을 가리키는지**(Button처럼)에 따라 13색 전체로 넓힐지, TDS가 정한 개수로 유지할지를 정한다.
4. 막대와 트랙의 명도 대비를 텍스트 기준(4.5:1)이 아니라 **비텍스트 기준(3.0:1)**으로 계산한다 — 다른 임계치를 텍스트와 혼동하지 않는다.
5. 기본값으로 쓰는 색은 최소 통과 단계보다 한 단계 여유를 두는 것을 고려한다 — 다른 색보다 압도적으로 자주 노출되므로, 근소하게 통과하는 값보다 안정적인 값이 낫다.
6. prop이 없어서 호출부가 컴포넌트 내부 구조(DOM 셀렉터 등)에 침투해 있는지 확인한다. 있다면 그 prop을 추가하는 이유가 이미 충분하다는 뜻이다 — 실제로 이 프로젝트의 `color`가 그런 사례였다.
