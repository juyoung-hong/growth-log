# Button

**원천 파일**: [`apps/frontend/src/shared/ui/button/`](../../frontend/src/shared/ui/button/) (`index.ts` + `Button.vue`)
**전제**: [01-colors.md](./01-colors.md)의 팔레트와 접근성 원칙을 먼저 읽는다.

## 왜 이렇게 만들었나

인터페이스(어떤 prop이 있고 각각 무슨 값을 받는지)는 [TDS Button 문서](https://tossmini-docs.toss.im/tds-mobile/components/button/)를 따른다. 값(색·크기·모서리 반지름)은 이 프로젝트의 팔레트와 타이포 스케일에서 새로 계산했다 — TDS의 실제 수치를 그대로 베낀 것이 아니다.

기반 구현은 [shadcn-vue](https://www.shadcn-vue.com/)가 생성한 컴포넌트(Reka UI 위에 얹은 `Primitive` 래퍼)이고, 이 프로젝트에서 변형 체계와 색·크기·상태를 전부 다시 짰다.

## 인터페이스

TDS 문서에 실린 `ButtonProps`는 다음과 같다.

| Prop | 타입 | 기본값 |
|---|---|---|
| `variant` | `"fill"` \| `"weak"` | `fill` |
| `color` | `"primary"` \| `"danger"` \| `"light"` \| `"dark"` | `primary` |
| `display` | `"inline"` \| `"block"` \| `"full"` | `inline` |
| `size` | `"small"` \| `"medium"` \| `"large"` \| `"xlarge"` | `xlarge`(이 구현은 `medium` — 아래 "크기" 절 참고) |
| `loading` | `boolean` | `false` |
| `disabled` | `boolean` | `false` |
| `type` | `"button"` \| `"submit"` \| `"reset"` | (TDS는 명시 안 함, 이 구현은 `button` — 아래 "상태" 절 참고) |
| `as` | `"button"` \| `"a"` | `button` |
| `htmlStyle` | `CSSProperties` | — |

이 중 `variant`/`color`/`size`/`loading`/`disabled`는 원래부터 구현돼 있었고, 이번에 **`display`와 `type`을 추가**했다. `as`와 `htmlStyle`은 별도로 만들지 않았다 — 이유는 아래 "TDS에서 가져오지 않은 것"에 있다.

## 변형 축 — 2축 구조

TDS는 "채도"와 "의미"를 별개 축으로 둔다. 하나로 합친 목록(`primary`/`secondary`/`ghost`/`danger`…)을 만들면 TDS에 없는 조합이 생기거나, 있어야 할 조합이 빠지기 쉽다.

```
variant : fill | weak      — 채도. 강조할지, 보조로 둘지
color   : primary | danger | light | dark   — 의미
display : inline | block | full   — 레이아웃
size    : small | medium | large | xlarge | icon
```

`variant`와 `color`를 조합해 실제 스타일을 정하는 자리는 `compoundVariants`에 있다 — `variant`/`color`가 각각 빈 문자열(`''`)만 갖는 것도 이 때문이다. 두 축의 값 자체는 클래스를 만들지 않고, 조합표(아래 5절)만 클래스를 만든다. `display`는 `variant`/`color`와 무관하게 독립적으로 동작해 `compoundVariants`가 필요 없다.

### `color`는 TDS와 같은 4개 — 의미 역할이라 palette hue를 그대로 붙이지 않는다

Badge의 `color`는 팔레트의 hue 이름(`blue`/`red`/`green`…) 그대로라 이 프로젝트 팔레트 13색 전부로 넓혔다. Button의 `color`는 다르다 — `primary`/`danger`/`light`/`dark`는 hue 이름이 아니라 **UI에서의 역할**(주 액션/위험 액션/중립 밝음/중립 어둠)이다. "Button color=pink"처럼 임의의 hue를 넣는 건 의미가 없다 — 그래서 Badge와 달리 TDS의 4개 역할을 그대로 유지했다. `size`도 TDS가 정의한 4단계(`small`/`medium`/`large`/`xlarge`)를 전부 그대로 구현했고 더 좁히거나 늘리지 않았다 — 이미 TDS 범위와 정확히 일치한다.

## 크기

| 크기 | 높이 | 모서리 반지름 | 글자(타이포 토큰) |
|---|---|---|---|
| `small` | 32px | 8px | `text-t7` (13px) |
| `medium` | 38px | 10px | `text-t6` (15px) |
| `large` | 48px | 14px | `text-t5` (17px) |
| `xlarge` | 56px | 16px | `text-t5` (17px) |
| `icon` | 38px 정사각형 | 10px | — |

**모서리 반지름은 픽셀을 직접 적는다.** `theme.css`의 `--radius`(20px)는 카드 컴포넌트 기준이라, Tailwind의 `rounded-lg`를 그대로 쓰면 버튼이 알약 모양이 된다. 버튼 전용 수치를 별도로 쓰는 이유다.

**기본 크기는 `medium`이다.** TDS 원본 문서의 기본값은 `xlarge`인데, 이는 모바일 화면 하단에 붙는 전체너비 CTA를 기준으로 잡은 값이다. 이 프로젝트는 데스크톱 웹의 조밀한 폼·목록 화면이 기준이라 `medium`을 기본값으로 뒀다. `large`/`xlarge`는 화면에서 강조가 필요한 주요 CTA에만 명시적으로 지정한다.

## 색 조합 — 실측 대비비 전부

각 `variant × color` 조합의 배경/글자 색과, 그 조합이 실제로 만족하는 WCAG 명도 대비비다. `01-colors.md`의 원칙(색상마다 규칙을 바꾸지 않는다)을 그대로 따른다.

| variant | color | 배경(기본→hover→active) | 글자 | 대비비 |
|---|---|---|---|---|
| `fill` | `primary` | blue-800 → blue-900 → blue-900 | white | 5.02 |
| `fill` | `danger` | red-800 → red-900 → red-900 | white | 4.51 |
| `fill` | `light` | grey-100 → grey-200 → grey-300 | grey-900 | 13.87 |
| `fill` | `dark` | grey-900 → grey-800 → grey-700 | white | 15.43 (기본 기준) |
| `weak` | `primary` | blue-100 → blue-200 → blue-200 | blue-900 | 4.93 (기본) / **4.02 — AA 미달**(hover·active) |
| `weak` | `danger` | red-100 → red-200 → red-200 | red-900 | 4.51 (기본) / **3.76 — AA 미달**(hover·active) |
| `weak` | `light` | transparent → grey-100 → grey-100 | grey-700 | 8.18(흰 배경 위 기본) / 7.35(hover·active) |
| `weak` | `dark` | grey-100 → grey-200 → grey-200 | grey-800 | 10.34 (기본) / 9.70 (hover·active) |

### `light`/`dark`는 접근성 예외가 아니라 TDS 자체의 설계다

`fill`의 기본 공식은 "진한 배경 + 흰 글자"이고 `primary`/`danger`가 이 공식을 그대로 따른다. 반면 `light`(밝은 중립 배경 + 어두운 글자)와 `dark`(가장 어두운 배경 + 흰 글자)는 **공식이 다르다** — 이건 대비를 맞추려고 예외를 둔 게 아니라, TDS 문서가 애초에 `light`/`dark`를 색이 있는 배경 위에서도 쓸 수 있는 중립색으로 정의해 뒀기 때문이다. 두 색은 원래부터 `primary`/`danger`와 다른 역할이다.

### hover/active가 진해지거나 밝아지는 이유

`fill`의 hover/active는 "가능한 방향으로 한 단계 더 이동"이 규칙이다. `primary`/`danger`/`light`는 이미 어두운 쪽으로 갈 여유가 있어 더 진해지고, `dark`는 이미 팔레트의 가장 어두운 900단계(grey-900)에서 시작하므로 반대로 밝아지는 것 외에는 이동할 방향이 없다.

### `weak`의 hover/active — 색에 관계없이 배경을 한 단계 진하게

`weak`의 기본 공식은 "100단계 배경 + 900단계 글자"이고, hover/active는 **색에 관계없이 배경을 한 단계(100→200) 진하게** 하는 것으로 통일했다.

`primary`/`danger`는 이렇게 하면 900단계 글자와의 대비가 4.5 밑으로 떨어진다(blue 4.02, red 3.76 — 계산해서 확인했다). 이 두 색만 다른 방식(예: 밑줄)을 쓰는 방법도 있었지만 채택하지 않았다 — 색마다 hover 표현 방식이 다르면("이 색은 배경이 진해지고, 저 색은 밑줄이 그어진다") 그 자체가 사용자에게 또 다른 비일관성으로 읽힌다. `01-colors.md`에서 green·yellow의 낮은 대비를 감수한 것과 같은 판단 기준이다 — **개별 조합의 대비 수치보다 상호작용 규칙의 일관성을 우선한다.**

## display — 레이아웃

```
display: inline | block | full
```

| 값 | 클래스 | 동작 |
|---|---|---|
| `inline`(기본) | `inline-flex` | 다른 요소와 나란히 놓인다. 문장 중간에 넣거나, 여러 버튼을 가로로 배치할 때 |
| `block` | `flex` | 자기 줄을 차지하지만 너비는 내용만큼만 |
| `full` | `flex w-full` | 부모 요소의 너비를 꽉 채운다 |

`variant`/`color`와 독립적인 축이라 `compoundVariants`에 조합을 추가할 필요가 없다 — `size`처럼 `variants.display`에 세 클래스만 등록하면 끝난다. base 클래스에 있던 `inline-flex`를 이 축으로 옮겼다(전에는 항상 `inline-flex`였다).

## 상태

### loading

```
loading: boolean
```

로딩 중에도 버튼 안의 글자를 지우지 않는다 — 버튼 너비가 바뀌면 연타나 오클릭이 생기기 때문이다. `lucide`의 `LoaderCircle`을 글자 앞에 얹고 `animate-spin`으로 돌린다. `loading`이 켜지면 내부적으로 `disabled`도 같이 켜져 클릭을 막는다.

`disabled:opacity-40`을 무조건 걸지 않고 `not-data-loading:disabled:opacity-40`을 쓴다 — 로딩 중에는 `disabled`가 `loading` 때문에 켜진 것이지 실제로 못 누르는 상태가 아니므로, 흐려지지 않고 색이 유지돼야 한다.

### disabled

```
disabled: boolean
```

`disabled:pointer-events-none`으로 클릭을 막고, `not-data-loading:disabled:opacity-40`으로 흐리게 표시한다(로딩 중이 아닐 때만).

### type

```
type: 'button' | 'submit' | 'reset' = 'button'
```

네이티브 `<button>`의 `type` 속성 그대로다. **TDS 문서는 기본값을 명시하지 않지만, 이 구현은 명시적으로 `button`을 기본값으로 둔다.** HTML 표준에서 `<form>` 안의 `<button>`은 `type`을 안 적으면 기본이 `submit`이다 — 폼 안에 있는 줄 모르고 만든 버튼이 페이지를 새로고침하며 폼을 제출해 버리는, 잘 알려진 실수의 원인이다. 기본값을 `button`으로 고정해 이 사고를 원천적으로 막는다. 실제로 폼을 제출하는 버튼에는 `type="submit"`을 명시적으로 지정해야 한다.

## TDS에서 가져오지 않은 것

- **`as`** — 별도로 만들지 않았다. 이 컴포넌트가 감싸고 있는 [Reka UI](https://reka-ui.com/)의 `Primitive`가 `PrimitiveProps`로 `as`(`"button"` | `"a"`)와 `asChild`를 이미 제공하고, `Button.vue`의 `Props`가 `PrimitiveProps`를 상속하므로 **이미 동작한다.** `<Button as="a" href="/foo">`처럼 그대로 쓸 수 있다. TDS와 똑같은 기능을 다른 경로(우리가 새로 만든 코드가 아니라 기반 라이브러리)로 이미 갖고 있으니 중복 구현하지 않는다.
- **`htmlStyle`** — TDS(React)에서 인라인 스타일을 넘기는 전용 prop이다. Vue는 이런 prop이 따로 필요 없다 — `Button.vue`가 `inheritAttrs`를 끄지 않았으므로, 선언되지 않은 속성(`style`도 포함)은 Vue가 **자동으로** 컴포넌트의 루트 엘리먼트에 전달한다. `<Button style="margin-top: 4px">`라고 쓰면 그대로 적용된다. 별도 prop을 만드는 건 프레임워크가 이미 하는 일을 다시 만드는 것이다.
- **3점 로딩 애니메이션** — TDS는 로딩 표시를 점 세 개 애니메이션으로 하는데, 이 프로젝트는 아이콘 라이브러리(`@lucide/vue`)의 회전 아이콘을 대신 쓴다. 기능은 같고(너비 유지, 진행 중임을 표시) 구현 방식만 다르다.

## Badge와 함께 쓰는 방법

TDS Button 문서에는 Badge와 조합하는 예시가 없다 — 두 컴포넌트를 나란히 쓰는 방법은 이 프로젝트에서 실제 화면을 만들며 정한 것이다.

### 상태는 Badge, 행동은 Button — 겹치지 않는다

이 앱에서 Badge와 Button은 **한 컴포넌트 안에 중첩되지 않는다.** Badge는 "지금 상태가 무엇인가"를 나타내고 Button은 "무엇을 할 수 있는가"를 나타낸다 — 서로 다른 질문에 답하므로, 같은 자리에서 하나로 합치지 않고 나란히 배치한다. `TaskGroupsPage`의 카드 헤더가 실제 예다.

```vue
<div class="flex items-center justify-between">
  <span class="text-17 font-semibold">메일서버 이중화 작업</span>
  <Badge color="blue">진행중</Badge>
</div>
```

여기서는 Badge만 쓰고 Button은 없다 — 카드 자체가 클릭 가능한 영역(상세로 이동)이라 별도 버튼이 필요 없기 때문이다. 상태 표시와 행동이 함께 필요한 자리(예: 태스크 행에서 "상태 배지 + 완료 처리 버튼")는 아래처럼 형제 요소로 나란히 둔다.

```vue
<div class="flex items-center gap-2">
  <Badge color="blue">진행중</Badge>
  <Button size="small" variant="weak">완료 처리</Button>
</div>
```

### 정렬 — 높이가 달라도 `items-center`면 충분하다

Button과 Badge는 같은 `size` 이름을 써도 실제 높이가 다르다(Button medium=38px, Badge medium=24px). 높이를 맞추려고 padding을 억지로 조정하지 않는다 — 부모에 `flex items-center`만 있으면 두 컴포넌트가 자동으로 세로 중앙 정렬된다. 위 예시의 `items-center`가 그 역할이다.

### 크기 짝 맞추기 — 눈으로 봤을 때 균형 잡힌 조합

같은 줄에 Button과 Badge를 둘 때, 다음 조합이 시각적으로 균형이 맞는다. 배지 높이가 버튼 높이의 대략 60~70%가 되도록 고른 것이다.

| Button `size` | 높이 | 짝이 되는 Badge `size` | 높이 |
|---|---|---|---|
| `small` | 32px | `small` 또는 `xsmall` | 20px / 18px |
| `medium` | 38px | `medium` | 24px |
| `large` | 48px | `large` | 28px |
| `xlarge` | 56px | `large`(Badge의 최대) | 28px |

이건 강제 규칙이 아니라 권장 조합이다 — 화면 밀도가 높은 목록에서는 Button `small` + Badge `xsmall`처럼 한 단계 더 작게 갈 수도 있다.

## 다른 프로젝트에서 재사용하는 방법

1. `01-colors.md`의 팔레트를 먼저 옮긴다.
2. 원본 디자인 시스템의 **인터페이스**(prop 이름·타입·개수)부터 전부 나열하고, 지금 프로젝트에 뭐가 있고 뭐가 빠졌는지 표로 대조한다 — "대충 비슷하게 만들었다"가 아니라 빠짐없이 구현했는지 확인할 수 있어야 한다.
3. prop이 **hue 이름**(Badge의 `color`처럼)이면 이 프로젝트 팔레트 전체로 넓히고, **역할 이름**(Button의 `color`인 primary/danger/light/dark처럼)이면 원본 개수를 그대로 유지한다 — 역할은 hue가 아니라서 팔레트를 넓힌다고 선택지가 늘어나지 않는다.
4. `variant`(fill/weak) × `color`(그 프로젝트에 필요한 의미 색) 2축 구조를 그대로 쓴다.
5. 각 조합의 배경·글자를 정하고 **반드시 실측 대비비를 계산**한다. `light`/`dark`처럼 공식 자체가 다른 중립색이 필요하면 별도로 정의하되, 어떤 색이 예외인지와 그 이유를 주석에 남긴다.
6. hover/active 표현 방식은 색상마다 다르게 두지 않는다. 배경을 진하게 하는 쪽으로 정했다면 모든 색이 그 방식을 따른다 — 일부 색에서 대비가 깨지더라도, 대비를 지키려고 그 색만 다른 상호작용 방식(밑줄 등)으로 바꾸면 사용자에게는 그게 더 큰 비일관성으로 읽힌다.
7. 프레임워크가 이미 해결해 주는 것은 다시 만들지 않는다. Vue의 attrs 자동 전달, 기반 프리미티브가 이미 제공하는 `as`/`asChild` 같은 것들이다. 원본 문서에 있다고 전부 새로 구현하지 말고, 이미 있는지부터 확인한다.
8. HTML 표준의 함정을 프레임워크가 안 막아 주는 자리는 명시적 기본값으로 막는다 — `<button>`이 `<form>` 안에서 기본이 `submit`인 것처럼, 원본 문서가 기본값을 안 정해 뒀어도 이 프로젝트에서는 사고를 막는 쪽으로 기본값을 정하고 그 이유를 남긴다.
9. 원본 디자인 시스템 문서에 컴포넌트 간 조합 예시가 없으면(이 프로젝트의 Button+Badge처럼), 실제 화면 코드에서 조합 규칙을 뽑아낸다 — "상태는 어디에, 행동은 어디에" 같은 역할 분리 원칙과 정렬·크기 짝 맞추기를 별도 절로 문서화한다.
