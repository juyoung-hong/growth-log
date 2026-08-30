# Tab

**원천 파일**: [`apps/frontend/src/shared/ui/tabs/`](../../frontend/src/shared/ui/tabs/) (`Tabs.vue`·`TabsList.vue`·`TabsTrigger.vue`·`TabsContent.vue`)
**전제**: [01-colors.md](./01-colors.md)·[02-typography.md](./02-typography.md)를 먼저 읽는다.

## 왜 이렇게 만들었나

인터페이스는 [TDS Tab 문서](https://tossmini-docs.toss.im/tds-mobile/components/tab/)를 따른다. 이전까지는 shadcn-vue 스캐폴드가 생성한 그대로였다 — 색·크기 전부 손대지 않은 상태였다.

## 인터페이스

TDS의 `TabProps`와 `TabItemProps`는 다음과 같다.

| Prop | 대상 | TDS 타입/기본값 | 이 구현 |
|---|---|---|---|
| `size` | Tab(루트) | `"large"` \| `"small"`, 기본 `large` | `TabsList`로 옮김(아래 설명), 기본 `large` |
| `fluid` | Tab(루트) | `boolean`, 기본 `false` | `TabsList`로 옮김, 기본 `false` |
| `itemGap` | Tab(루트) | `number`(px) | `TabsList`로 옮김 |
| `ariaLabel` | Tab(루트) | `string` | `TabsList`로 옮김 |
| `onChange` | Tab(루트) | `(index, key) => void`, 필수 | Reka의 `v-model`(`update:modelValue`) — 아래 설명 |
| `selected` | Tab.Item | `boolean`, 필수 | 구현 안 함 — Reka의 값 매칭으로 이미 됨(아래 설명) |
| `redBean` | Tab.Item | `boolean`, 기본 `false` | `TabsTrigger`에 그대로 구현 |
| `stretch` | — | TDS에 없음 | `TabsList`에 새로 추가(아래 설명) |

### 왜 `size`/`fluid`/`itemGap`/`ariaLabel`을 `TabsList`로 옮겼나

TDS는 `Tab` 루트 하나에 이 네 개를 전부 둔다. 이 프로젝트는 Root(`Tabs`)/List(`TabsList`)/Trigger(`TabsTrigger`) 세 계층으로 나뉘어 있다 — Reka UI가 `role="tablist"`의 접근성을 책임지는 지점이 `TabsList`이기 때문이다. 네 prop 모두 "탭 목록 전체의 크기·간격·스크롤 여부·레이블"이라는 같은 의미고, 그 의미에 대응하는 실제 DOM 요소가 `TabsList`라 그쪽으로 옮겼다. [06-dialog.md](./06-dialog.md)에서 TDS의 평평한 구조를 여러 하위 컴포넌트로 나눠 옮긴 것과 같은 종류의 판단이다.

### `onChange(index, key)` 대신 Reka의 `v-model`을 쓴다

TDS는 인덱스와 키를 콜백 인자로 넘긴다. Reka UI의 `TabsRoot`는 `v-model:model-value`로 선택된 탭의 `value`를 직접 주고받는다 — 인덱스보다 값 자체를 다루는 쪽이 Vue에서 더 흔한 패턴이고, 실제로 `ScopeSwitch.vue`도 `@update:model-value="change"`로 값을 바로 받는다. TDS 인터페이스를 기계적으로 옮기지 않고, 이미 있는 Vue 관용구를 그대로 썼다.

### `selected`를 별도 prop으로 만들지 않은 이유

TDS는 각 `Tab.Item`에 `selected: boolean`을 명시적으로 넘겨야 한다. Reka UI의 `TabsTrigger`는 다르게 동작한다 — 자신의 `value`가 `TabsRoot`의 `modelValue`와 같으면 자동으로 `data-state="active"`가 붙는다. **선언적으로 값만 맞추면 선택 상태가 저절로 결정된다.** boolean을 직접 계산해서 넘길 필요가 없다 — [03-button.md](./03-button.md)의 `as`처럼, 기반 라이브러리가 이미 하는 일을 다시 만들지 않는다.

## 시각 스타일 — variant 축을 없애고 TDS의 밑줄 하나로 통일했다

shadcn 스캐폴드는 `default`(회색 배경의 세그먼트 버튼 묶음)와 `line`(밑줄) 두 `variant`를 뒀다. **TDS Tab 문서에는 그런 선택지가 아예 없다** — 크기(`size`) 말고는 시각적으로 고를 게 없는, 밑줄 하나만의 컴포넌트다. 그래서 `variant` 축 자체를 지웠다.

밑줄은 두 겹으로 이뤄진다.

- **회색 기준선**: `TabsList`가 목록 전체 폭에 걸쳐 **딱 한 번** 그린다(`grey-200`, ProgressBar의 트랙과 같은 색). 탭마다 따로 그리지 않는 이유는, 탭 사이 간격(gap)에서 선이 끊겨 보이기 때문이다 — 목록 하나에만 그리면 간격까지 포함해 처음부터 끝까지 이어진 선이 된다.
- **파란 강조선**: 선택된 `TabsTrigger`만 그 위에 겹쳐서 보여준다(`bg-primary`). `z-10`으로 회색 기준선보다 위에 그려지게 해서, 두 선이 겹치는 자리에서 파란색이 항상 이긴다. 글자 폭(`inset-x-0`)이 아니라 좌우로 4px씩 더 넓은 `-inset-x-1`을 쓴다 — 글자만큼만 딱 맞으면 좁아 보인다. 탭 사이 기본 간격이 16px(`gap-4`)이라 양쪽에서 4px씩 먹어도 8px이 남아 옆 탭을 침범하지 않는다.

선택된 탭은 여기에 굵은 글자(`font-bold`)와 진한 글자색(`text-grey-900`)이 더해진다.

`ScopeSwitch.vue`(유일한 현재 사용처)는 `variant`를 지정한 적이 없어서 — 원래 `default`(세그먼트) 스타일로 보이고 있었는데, 이번 변경으로 **자동으로 밑줄 스타일로 바뀐다.** 코드 수정 없이 반영된다.

## 크기

| 값 | 높이(`TabsList`) | 글자(`TabsTrigger`, `group-data-[size]` 선택자로 전달) |
|---|---|---|
| `large`(기본) | `h-11`(44px) | `text-17`(17px) |
| `small` | `h-9`(36px) | `text-14`(14px) |

`TabsTrigger`가 직접 `size` prop을 받지 않고, 부모 `TabsList`의 `data-size` 속성을 `group-data-[size=large]/tabs-list:` 선택자로 읽는다 — `TabsList` 하나에만 `size`를 지정하면 그 안의 모든 `TabsTrigger`에 자동으로 적용된다. shadcn 스캐폴드가 이미 `group-data-[variant=...]/tabs-list:` 방식으로 이 메커니즘을 쓰고 있었어서, `variant` 대신 `size`를 흘려보내도록 같은 방식을 재사용했다.

## `fluid`·`itemGap`

```
fluid: boolean = false      // 4개 넘으면 가로 스크롤
itemGap: number             // px 단위 탭 사이 간격. 안 주면 기본 16px(gap-4)
```

TDS 지침대로 기본은 스크롤을 켜지 않는다 — 4개를 넘겨서 잘리거나 줄바꿈되면 "여기 `fluid`가 필요하다"는 신호가 눈에 바로 보여야 한다. 조용히 줄바꿈시키면 그 신호를 놓치고 레이아웃이 왜 이런지 나중에 헷갈린다.

## `stretch` — TDS에 없는, 이 프로젝트가 새로 더한 옵션

```
stretch: boolean = false    // 폭을 꽉 채우고 항목마다 폭을 균등하게 나눈다
```

TDS Tab 문서는 이 옵션을 두지 않는다. TDS의 Tab은 항상 **페이지 내비게이션**(할일목록/회의록/참고자료처럼 화면을 갈아 끼우는 용도)이라, 탭이 자기 글자 폭만큼만 차지하고 나머지가 빈 공간으로 남는 게 자연스럽다. 그런데 이 프로젝트는 Tabs를 **폼 안의 값 선택기**로도 쓴다 — 인물 등록 폼의 회사/개인 선택이 그 예다. 원래 `Button` 두 개를 나란히 둔 토글이었는데, 상단 `ScopeSwitch`와 같은 회사/개인 개념을 표현 방식만 다르게(Button vs Tabs) 쓰는 게 어색하다고 판단해 `Tabs`로 통일했다. 그러면서 "값 선택기"라는 원래 성격(폭을 꽉 채워야 자연스럽다)까지 잃으면 안 되므로, `stretch`를 추가해 두 성격을 다 만족시켰다.

```html
<!-- TabsList가 group/tabs-list이고 data-stretch를 흘려보낸다 -->
<div class="group/tabs-list ..." data-stretch="true">
  <!-- TabsTrigger는 그 값을 group-data-[stretch=true]/tabs-list: 선택자로 읽는다 -->
  <button class="... group-data-[stretch=false]/tabs-list:shrink-0 group-data-[stretch=true]/tabs-list:flex-1">
```

`size`가 이미 쓰던 것과 같은 메커니즘이다(`TabsList`의 `data-*` 속성을 `TabsTrigger`가 `group-data-[...]/tabs-list:` 선택자로 읽는다). `shrink-0`/`flex-1`을 무조건 하나로 정해 두지 않고 **둘 다 조건부 선택자로만 존재**하게 한 이유가 있다 — `flex-1`을 그냥 덧붙이는 override 방식도 가능은 했지만(twMerge가 `shrink-0`을 실제로 지워준다는 걸 확인했다), 이미 `size`가 "기본값을 하드코딩하지 않고 둘 다 조건부로 둔다"는 방식을 쓰고 있어서 그 관례를 그대로 따랐다 — 나중에 이 컴포넌트를 보는 사람이 "왜 size는 조건부고 stretch는 override 방식이지"처럼 두 가지 패턴을 기억할 필요가 없다.

## `redBean` — 새 소식 알림 점

```
redBean: boolean = false
```

탭 오른쪽 위에 빨간 점(`bg-red-600`)을 띄운다. TDS 문서는 스크린리더 안내를 `title` 속성에 "(업데이트 있음)"을 자동으로 붙여 처리하는데, 이 구현은 `title` 대신 **`sr-only` 텍스트**를 썼다. `title`은 마우스 호버가 있어야 읽히는 보조기술이 있어 키보드·스크린리더 사용자에게 항상 전달된다는 보장이 없다 — `sr-only` span은 DOM에 항상 존재해 더 넓은 범위의 보조기술에서 안정적으로 읽힌다.

```vue
<span aria-hidden="true" class="bg-red-600 absolute top-0.5 right-0.5 size-1.5 rounded-full" />
<span class="sr-only">(업데이트 있음)</span>
```

## 색상 — `01-colors.md`의 이미 검증된 값만 쓴다

선택 안 된 탭 글자를 `grey-600`이 아니라 **`grey-700`**으로 쓴다. `grey-600`은 흰 배경에서 `3.32:1`로 WCAG AA(4.5:1) 미달이다 — [02-typography.md](./02-typography.md)에서 사이트 전체를 이미 `grey-700`(`8.18:1`)으로 옮긴 것과 같은 이유로, TDS 원본이 어떤 회색조를 쓰든 이 프로젝트는 이미 검증된 값만 쓴다. 밑줄 색은 `--primary`(`blue-800`)를 그대로 참조한다 — 새 색을 만들지 않고 시맨틱 토큰을 재사용한다.

## 다른 프로젝트에서 재사용하는 방법

1. [01-colors.md](./01-colors.md)·[02-typography.md](./02-typography.md)를 먼저 옮긴다.
2. 원본이 여러 시각 변형(세그먼트/밑줄 등)을 제공해도, **문서에 실제로 선택 가능한 축으로 나와 있는지** 확인한다. 기반 UI 라이브러리(shadcn 등)가 자체적으로 추가한 변형이 원본 디자인 시스템에 없으면, 그 변형은 지우고 원본이 실제로 쓰는 스타일 하나로 통일한다.
3. 원본이 명시적 boolean(`selected` 등)으로 상태를 넘기라고 해도, 기반 프리미티브 라이브러리(Reka UI 등)가 값 매칭 같은 선언적 방식으로 이미 처리한다면 그쪽을 쓴다 — 상태를 직접 계산해서 넘기는 코드를 새로 만들지 않는다.
4. 원본 디자인 시스템에 없는 옵션이라도, 이 프로젝트에서 그 컴포넌트를 원본과 다른 용도(페이지 내비게이션이 아니라 폼 안의 값 선택기 등)로 쓰게 되면 필요한 만큼 추가한다. 단, 새 옵션을 이미 있는 메커니즘(`data-*` + `group-data-[...]:` 선택자 등)과 같은 방식으로 만든다 — 컴포넌트 하나 안에 서로 다른 두 가지 조건부 스타일링 패턴이 섞이지 않게 한다.
4. 원본이 컴포넌트 계층 없이 평평하게 props를 두더라도(TDS의 `Tab` 루트처럼), 이 프로젝트의 실제 컴포넌트 구조(Root/List/Trigger 등 여러 계층)에서 각 prop이 의미상 어느 계층에 속하는지 판단해서 그쪽으로 옮긴다.
5. 부모 컴포넌트의 설정(크기 등)을 자식 여러 개에 일일이 전달하고 싶지 않으면, `data-*` 속성 + `group-data-[key=value]/name:` 선택자로 전달한다 — prop을 모든 자식에 반복해서 넘기지 않아도 된다.
6. 보조기술 안내가 `title` 속성처럼 상호작용(호버 등)에 의존하는 방식으로 문서화돼 있으면, 항상 읽히는 `sr-only` 텍스트로 바꾸는 걸 고려한다.
