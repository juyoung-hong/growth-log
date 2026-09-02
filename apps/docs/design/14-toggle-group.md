# ToggleGroup

**원천 파일**: [`apps/frontend/src/shared/ui/toggle-group/`](../../frontend/src/shared/ui/toggle-group/) (`ToggleGroup.vue`·`ToggleGroupItem.vue`)
**전제**: [01-colors.md](./01-colors.md)·[04-badge.md](./04-badge.md)·[08-tab.md](./08-tab.md)를 먼저 읽는다.

## 왜 만들었나

TDS 공개 문서에는 이 컴포넌트가 없다. Phase 3(TaskGroup 등록·수정 폼)에서 "상태(보류/진행중/완료)를 고르는 자리가 Tabs(밑줄)로 돼 있는데, 버튼 같은 형태로 바꾸고 목록 카드의 배지 색과 일치시켜 달라"는 요구로 새로 만들었다.

Tabs를 그대로 재스타일링하지 않고 별도 컴포넌트로 뗀 이유가 있다. [08-tab.md](./08-tab.md)의 `stretch` 절이 이미 짚었듯, Tabs는 원래 **페이지 내비게이션**(밑줄 강조가 자연스러운 자리)이고, 폼 안의 값 선택기로 쓸 때도 그 시각 언어(밑줄)를 그대로 가져가고 있었다. 그런데 이번 요구는 "밑줄이 아니라 버튼처럼, 그리고 선택한 값이 배지와 같은 색으로 채워지길" 바란다 — Tabs의 밑줄 스타일과 근본적으로 다른 시각 언어라, `variant` 하나 추가하는 대신 **값 하나를 고른다는 의미에 맞는 다른 프리미티브**(Reka UI `RadioGroup`)로 새로 만들었다.

## 인터페이스

| Prop | 대상 | 값 | 설명 |
|---|---|---|---|
| `modelValue` | `ToggleGroup` | 항목의 `value`와 같은 타입 | 선택된 값. `v-model`로 쓴다 |
| `stretch` | `ToggleGroup` | `boolean`, 기본 `false` | 항목마다 폭을 균등하게 나눠 채운다. Tabs의 `stretch`와 같은 이름·같은 뜻 |
| `value` | `ToggleGroupItem` | 항목이 나타내는 값 | Reka `RadioGroupItem`의 `value` 그대로 |
| `color` | `ToggleGroupItem` | `BadgeVariants['color']`(13색), 필수 | 선택됐을 때 채울 색 |

## Tabs 대신 `RadioGroup` 위에 만든 이유

"여러 값 중 정확히 하나를 고른다"는 라디오 버튼의 정의 그 자체다. Reka UI의 `RadioGroupRoot`/`RadioGroupItem`을 쓰면 `role="radio"`·방향키 이동·"하나만 선택됨" 상태 관리가 공짜로 딸려온다 — Tabs(`role="tab"`, 원래 뜻은 "패널 전환")를 값 선택기로 억지로 맞추는 것보다 의미가 정확하다.

선택 여부는 `data-state="checked"|"unchecked"`로 내려온다 — Tabs가 `data-state`를 `data-active`라는 boolean 형태로 노출하는 것과 달리, `ToggleGroupItem`은 Tailwind의 `data-[state=checked]:` 선택자로 이 값을 직접 읽는다.

## 색상 — Badge의 weak 배합을 그대로 재사용한다

선택된 항목은 [04-badge.md](./04-badge.md)가 정의한 `weak` 배합(100단계 배경 + 같은 계열 900단계 글자)과 **정확히 같은 값**을 쓴다. "상태를 고르는 곳"과 "고른 상태가 목록 카드에서 어떻게 보이는지"가 같은 색이어야, 사용자가 폼에서 방금 고른 값과 목록에서 보는 배지를 같은 개념으로 인식한다 — 이번 요구가 명시적으로 짚은 지점이다.

`badgeVariants()`를 직접 호출하지 않고 `index.ts`의 `TOGGLE_GROUP_ITEM_COLOR`에 색 값만 따로 옮겨 적었다. 두 가지 이유가 있다.

1. `badgeVariants()`가 함께 반환하는 크기·모양 클래스(`h-6`·`rounded-[6px]`·`font-semibold` 등)가 배지 크기를 위한 것이라, 버튼 크기(`h-9`·`rounded-[8px]`·`font-bold`)의 `ToggleGroupItem`과 맞지 않는다. `cn()`으로 뒤에 다시 덮어씌울 수는 있지만, 애초에 안 맞는 값을 가져와 다시 지우는 것보다 필요한 값(배경·글자색)만 옮겨 적는 쪽이 더 명확하다.
2. Tailwind는 정적 스캐너다 — `` `data-[state=checked]:bg-${color}-100` `` 처럼 런타임에 문자열을 조립하면 그 클래스가 실제로 존재하는지 스캐너가 알 방법이 없어 스타일이 안 붙는다. 색상별 전체 클래스 문자열(`data-[state=checked]:bg-blue-100 data-[state=checked]:text-blue-900` 등)이 소스 코드에 리터럴로 그대로 적혀 있어야 한다.

`BadgeVariants['color']` 타입을 그대로 가져와 `color` prop의 타입으로 쓴다 — Badge에 색이 추가되면 `TOGGLE_GROUP_ITEM_COLOR`가 `Record`라 컴파일 타임에 누락을 바로 알 수 있다.

## 선택 표시에 별도 인디케이터(점·체크)를 안 둔 이유

Badge 자체가 배경색만으로 상태를 표시하지, 테두리나 아이콘을 더하지 않는다(01-colors.md/04-badge.md의 "flat color layering" 원칙). `ToggleGroupItem`도 같은 언어를 쓴다 — 선택된 항목은 배지와 같은 색으로 꽉 채워지는 것 자체가 선택 표시고, 그 위에 체크 아이콘이나 테두리를 더하면 배지와 다른 언어가 섞인다.

## `stretch`

```
stretch: boolean = false    // 폭을 꽉 채우고 항목마다 폭을 균등하게 나눈다
```

메커니즘은 Tabs의 `stretch`와 동일하다 — `ToggleGroup`이 `data-stretch` 속성을 흘려보내고, `ToggleGroupItem`이 `group-data-[stretch=true]/toggle-group:flex-1` 선택자로 읽는다. 지금 유일한 사용처(TaskGroupFormDialog의 상태 선택)는 3개 항목이 폼 폭을 꽉 채워야 자연스러워 `stretch`를 켠 채로 쓴다.

## 다른 프로젝트에서 재사용하는 방법

1. [01-colors.md](./01-colors.md)·[04-badge.md](./04-badge.md)를 먼저 옮긴다.
2. "값 하나를 고르는 폼 입력"이라면 Tabs(내비게이션 프리미티브)를 재스타일링하지 말고, 의미가 맞는 프리미티브(라디오 그룹 등) 위에 새로 만든다 — 겉모습만 비슷하다고 같은 컴포넌트를 억지로 쓰지 않는다.
3. 선택된 값의 색을 다른 컴포넌트(배지 등)와 맞춰야 한다면, 그 컴포넌트의 색 배합 함수를 그대로 호출하지 말고 필요한 값(배경·글자색)만 별도 상수로 옮겨 적는다 — 크기·모양까지 함께 딸려오는 걸 막을 수 있고, Tailwind가 정적으로 스캔할 수 있는 리터럴 클래스로 남는다.
