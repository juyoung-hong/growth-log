# Separator

**원천 파일**: [`apps/frontend/src/shared/ui/separator/`](../../frontend/src/shared/ui/separator/) (`Separator.vue`)
**전제**: [01-colors.md](./01-colors.md)·[12-table.md](./12-table.md)를 먼저 읽는다.

## 왜 이렇게 만들었나

인터페이스는 [TDS Border 문서](https://tossmini-docs.toss.im/tds-mobile/components/border/)를 따른다. shadcn은 이 개념을 `Separator`라는 이름으로 부르지만, TDS는 `Border`라고 부른다 — 이름은 다르지만 같은 것이다: 콘텐츠를 나누는 얇은 구분선(또는 선 없는 여백).

이 컴포넌트는 이미 Phase 1(앱 셸 작업)에서 TDS 규칙대로 만들어져 있었다. 이번에 TDS 문서를 다시 정확히 대조해 **빠진 prop 하나**를 찾아 채웠다.

## 인터페이스

| Prop | TDS 타입/기본값 | 이 구현 |
|---|---|---|
| `variant` | `"full"` \| `"padding24"` \| `"height16"`, 기본 `full` | 동일 |
| `height` | `string`, `variant="height16"`일 때만 유효 | `number`(px)로 단순화 — **이번에 추가** |

## `variant` — 세 가지

| 값 | 모양 |
|---|---|
| `full` | 폭을 꽉 채운 1px 선 |
| `padding24` | 좌우 24px을 비운 1px 선 (카드 안 항목 사이) |
| `height16` | 선 없이 16px 여백만 (문단을 갈라놓을 때) |

`height16`이 선을 안 그리는 게 이상해 보일 수 있다 — TDS에서 `Border`는 "선"이 아니라 **"구분"** 을 뜻하는 부품이라, 여백으로만 구분하는 경우도 같은 이름 아래 둔다.

## `height` — 이번에 채운 것

```
height?: number   // px. variant="height16"일 때만 의미가 있다. 기본 16px 대신 다른 값을 쓰고 싶을 때
```

TDS 문서를 처음 참고했을 때는 `variant`만 옮기고 `height`를 놓쳤다. 다시 대조하며 채웠다. TDS는 `string` 타입(예: `"24px"`)을 받지만, [09-input.md](./09-input.md)의 `minHeight`/`height`(TextArea 개념을 흡수하며 만든 숫자형 override prop)와 같은 관례를 따라 `number`(px)로 단순화했다. 인라인 `style`로 얹는다 — 팔레트·타이포처럼 정해진 스케일이 있는 값이 아니라 임의의 px라, 클래스 이름으로 표현할 수 없다.

## 테두리 색은 그대로 뒀다

`bg-border`(`--border` 토큰, `grey-200`)를 그대로 쓴다. [09-input.md](./09-input.md)에서 텍스트필드 테두리를 `grey-600`으로 올린 것과 다르다 — 그건 "여기가 조작 영역이다"를 알려야 하는 경계라 WCAG 비텍스트 기준(3.0:1)이 적용됐지만, `Separator`는 사용자가 조작할 대상이 아니라 **내용을 눈으로 훑어보기 쉽게 나누는 장식적 구분**이다. [12-table.md](./12-table.md)에서 테이블 행 구분선에 같은 판단을 내린 것과 일치한다.

## 겸사겸사 고친 것

기존 코드 주석에 "hBorder는..."이라는 오타가 있었다(`Border`가 맞다). 또 `height16` variant가 기본 높이(`h-4`)를 두 곳에서 겹쳐 선언하고 있었다 — 하나는 항상 적용되는 값, 다른 하나는 가로 방향일 때만 적용되는 조건부 값으로 사실상 같은 값을 두 번 쓰고 있었다. `height` prop을 추가하며 하나로 정리했다.

## 다른 프로젝트에서 재사용하는 방법

1. [01-colors.md](./01-colors.md)·[12-table.md](./12-table.md)를 먼저 읽는다.
2. 이미 TDS 규칙대로 만들어 둔 컴포넌트도, 시간이 지나면 원본 문서를 다시 한번 정확히 대조한다 — 처음 만들 때 빠뜨린 prop이 나중에 발견될 수 있다(이번의 `height`처럼).
3. 원본이 문자열로 임의 값을 받는 자리(`height`처럼 정해진 스케일이 없는 값)는, 이 프로젝트의 다른 컴포넌트가 이미 쓰고 있는 관례(숫자 + 인라인 style)를 그대로 따른다 — 매번 새로운 표현 방식을 고르지 않는다.
4. 테두리·구분선에 접근성 기준을 적용할지는 "조작해야 하는 경계인가, 훑어보기 쉽게 돕는 장식인가"로 판단한다([09-input.md](./09-input.md)·[12-table.md](./12-table.md)와 같은 기준).
