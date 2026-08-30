# Alert

**원천 파일**: [`apps/frontend/src/shared/ui/alert/`](../../frontend/src/shared/ui/alert/) (`Alert.vue` + `AlertTitle.vue` + `AlertDescription.vue` + `AlertAction.vue`)
**전제**: [01-colors.md](./01-colors.md)·[09-input.md](./09-input.md)를 먼저 읽는다. 이 문서는 09번 문서와 같은 방식(참고 디자인 시스템의 컴포넌트 경계가 아니라, 이미 쓰는 프레임워크의 컴포넌트 경계를 유지하며 개념만 흡수)을 Alert에 적용한 것이다.

## 왜 이렇게 만들었나

shadcn은 페이지 안에 계속 머무는 정적 배너를 `Alert` 하나로 둔다. TDS는 "사용자에게 상태·메시지를 전달한다"는 같은 목적의 컴포넌트를 여러 개로 나눠 각자 다른 문서에 둔다. [09-input.md](./09-input.md)에서 TextField 계열을 `Input` 하나로 합친 것과 같은 방식으로, **`Alert`라는 컴포넌트 경계는 유지하고 TDS가 나눠 둔 개념 중 실제로 겹치는 것만 흡수**했다.

## TDS 사이드바에서 확인한 후보 넷

"알림·메시지" 개념에 해당할 만한 TDS 컴포넌트를 전부 확인했다.

| TDS 컴포넌트 | 실제로 하는 일 | Alert에 흡수했나 |
|---|---|---|
| [Toast](https://tossmini-docs.toss.im/tds-mobile/components/toast/) | 화면에 잠깐 떴다가 자동으로 사라지는 상태 메시지 | **흡수함** — 아래 설명 |
| [Bottom Info](https://tossmini-docs.toss.im/tds-mobile/components/bottom-info/) | 화면 맨 아래 고정된 약관·고지 문구(금융 상품 안내 등) | 안 함 — 알림이 아니라 **상시 고정 푸터**다. 사라지지도, 배너처럼 끼어들지도 않는다 |
| [Bubble](https://tossmini-docs.toss.im/tds-mobile/components/bubble/) | 대화형 UI의 말풍선(내 메시지/상대 메시지 구분) | 안 함 — 알림이 아니라 **채팅 메시지**다. 목적 자체가 다르다 |
| [Result](https://tossmini-docs.toss.im/tds-mobile/components/result/) | 작업 결과(성공/실패)를 전달하는 **전체 화면** 단위 컴포넌트(큰 아이콘+제목+설명+버튼) | 안 함 — 메시지를 전달한다는 목적은 같지만 **화면을 통째로 차지하는 규모**라 Alert의 "본문 안 작은 배너"와 성격이 다르다. 이건 페이지 레이아웃 패턴에 가깝다 |

Toast만 진짜로 겹친다 — 둘 다 "짧은 메시지 + 아이콘 + 선택적 액션 + 색으로 심각도 표현"이라는 같은 구조를 쓴다. 다른 건 **화면에 계속 머무는가, 잠깐 떴다 사라지는가** 하나뿐이다.

## 인터페이스

| Prop | 출처 | 타입/기본값 |
|---|---|---|
| `variant` | Alert(기존) | `"default"` \| `"destructive"`, 기본 `default` |
| `floating` | (새로 추가) | `boolean`, 기본 `false` — 켜면 Toast처럼 동작한다 |
| `open` | Toast의 `open` | `boolean`, 기본 `true`(`v-model`) — `floating`일 때만 의미가 있다 |
| `position` | Toast의 `position` | `"top"` \| `"bottom"`, 기본 `bottom` |
| `duration` | Toast의 `duration` | `number`(ms), 기본 `3000`. `0`이면 자동으로 안 닫힌다 |
| `ariaLive` | Toast의 `aria-live` | `"polite"` \| `"assertive"`, 기본은 `variant`에서 자동으로 정함(아래 설명) |
| `text` | Toast의 `text` | 구현 안 함 — `AlertDescription` 슬롯으로 이미 됨 |
| `leftAddon` | Toast의 아이콘 | 구현 안 함 — 기존 default 슬롯에 `<svg>`를 직접 넣으면 이미 됨(아래 설명) |
| `higherThanCTA` | Toast 고유 | 구현 안 함(아래 설명) |
| `onClose` | Toast의 콜백 | `update:open` 이벤트(`open=false`) — Vue의 `v-model` 관용구 |

## `floating` — 정적 배너와 뜨는 토스트를 하나의 컴포넌트로

```
floating: boolean = false
```

`false`(기본)면 지금까지의 Alert 그대로 — 호출부가 있는 자리에 그대로 렌더링되고, 사라지게 하려면 호출부가 `v-if`로 걷어낸다. `true`면 `Teleport`로 `<body>` 바로 아래에 옮겨져 화면 상/하단에 고정 위치로 뜨고, `duration` 뒤에 스스로 `open`을 꺼서 사라진다.

**색·라벨·구조(`AlertTitle`/`AlertDescription`/`AlertAction`)는 두 모드가 완전히 같은 걸 쓴다.** `floating`은 오직 "어디에, 얼마나 오래 보이는가"만 바꾼다 — [09-input.md](./09-input.md)의 `multiline`이 높이 모델만 바꾸고 색·테두리 규칙은 그대로 공유하는 것과 같은 설계다.

## `ariaLive` — variant에서 자동으로 정한다

```ts
const resolvedAriaLive = ariaLive ?? (variant === 'destructive' ? 'assertive' : 'polite')
```

에러(`destructive`)는 사용자가 지금 하던 일을 끊고서라도 즉시 들어야 하니 `assertive`, 나머지는 읽던 흐름을 방해하지 않는 `polite`가 기본이다. `role`도 짝을 맞춘다 — `assertive`면 `role="alert"`(ARIA 명세상 암묵적으로 assertive를 내포한다), `polite`면 `role="status"`(암묵적으로 polite). 매번 `ariaLive`를 직접 지정할 필요 없이, `variant`만 정하면 접근성 우선순위도 같이 정해진다.

## 만들지 않은 것

- **`text`** — Toast는 문자열 하나를 받지만, 이 컴포넌트는 이미 `AlertDescription` 슬롯이 있다. 새 prop을 만들면 "문자열을 줄 것이냐 슬롯을 쓸 것이냐" 두 가지 방법이 생겨 오히려 헷갈린다.
- **`leftAddon`(아이콘)** — 새 prop이 필요 없다. `alertVariants`의 `has-[>svg]:grid-cols-[auto_1fr]`가 이미 "SVG 자식이 있으면 아이콘+텍스트 2열 배치로 바꾼다"를 처리한다. `<Alert floating><XCircleIcon /><AlertTitle>...</AlertTitle></Alert>`처럼 그냥 슬롯에 아이콘을 넣으면 된다.
- **`higherThanCTA`** — 화면 하단에 고정된 CTA 바 위로 토스트를 올리는 기능이다. 이 앱은 그런 고정 CTA 바 패턴 자체가 없어서 만들지 않았다.

## 그림자 — 이 프로젝트에서 유일하게 예외를 둔 자리

`floating`일 때만 `shadow-lg`를 쓴다. [01-colors.md](./01-colors.md)의 카드 어법(그림자 없이 배경색 차이나 딤머로 면을 구분)을 이 프로젝트 전체가 지켜 왔는데, 여기서는 깼다 — Card는 페이지 안에서 다른 요소와 나란히 있어 배경색 차이만으로 충분하고, Dialog는 뒤에 딤머가 있어 구분이 저절로 된다. 하지만 **떠 있는 토스트는 딤머도 없고, 페이지 위 아무 데나 겹쳐 뜬다** — 그림자 없이는 배경과 구분이 안 될 수 있다. 이 프로젝트에서 그림자를 쓰는 자리는 여기 하나뿐이고, 그 이유를 코드 주석에도 남겨 뒀다.

## 다른 프로젝트에서 재사용하는 방법

1. [01-colors.md](./01-colors.md)·[09-input.md](./09-input.md)를 먼저 읽는다.
2. "메시지를 전달한다"는 목적이 같아 보여도, **화면에 머무는 방식**(계속 머무는지, 잠깐 떴다 사라지는지, 화면을 통째로 차지하는지)이 다르면 하나로 합칠지 신중히 판단한다. 이 프로젝트는 Toast(짧게 떴다 사라짐)만 합쳤고, Result(전체 화면)는 규모가 달라 별개로 남겨 뒀다.
3. 자동 소멸 타이머는 컴포넌트가 스스로 관리하게 한다 — 호출부가 `setTimeout`을 직접 만들어 껐다 켰다 하게 시키지 않는다.
4. `aria-live`/`role`처럼 접근성 속성이 여러 개 얽혀 있으면, 이미 있는 다른 prop(여기서는 `variant`)에서 합리적인 기본값을 자동으로 뽑아낸다 — 매번 명시하게 하면 잊어버리기 쉽다.
5. 프로젝트 전체가 지켜 온 규칙(그림자 없음 등)을 깨야 하는 정당한 이유가 생기면, 그 컴포넌트에서만 예외를 두고 **왜 이 자리만 다른지** 코드와 문서에 분명히 남긴다. 예외가 조용히 스며들면 나중에 "여기 왜 그림자가 있지"를 아무도 설명 못 하게 된다.
