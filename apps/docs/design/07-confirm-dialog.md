# ConfirmDialog

**원천 파일**: [`apps/frontend/src/shared/ui/confirm-dialog/`](../../frontend/src/shared/ui/confirm-dialog/) (`ConfirmDialog.vue`)
**전제**: [01-colors.md](./01-colors.md)·[02-typography.md](./02-typography.md)·[03-button.md](./03-button.md)·[06-dialog.md](./06-dialog.md)를 먼저 읽는다.

## 왜 이렇게 만들었나

인터페이스는 [TDS ConfirmDialog 문서](https://tossmini-docs.toss.im/tds-mobile/components/Dialog/confirm-dialog/)를 따른다. 값(색·타이포)은 이 프로젝트의 팔레트·타이포 스케일에서 계산하되, TDS 기본값이 우리 접근성 기준에 못 미치는 자리는 예외를 둔다(아래 참고).

이 컴포넌트는 [06-dialog.md](./06-dialog.md)의 원시 부품(`Dialog`·`DialogContent`·`DialogHeader`·`DialogFooter` 등) 위에 지은 **구체 컴포넌트**다. 이 앱의 모든 삭제 확인이 이 하나를 재사용한다 — 화면마다 확인창을 따로 만들면 어떤 곳은 "정말 삭제할까요?"만 묻고 어떤 곳은 연쇄 삭제를 경고하는 식으로 위험 안내가 들쭉날쭉해지기 때문이다.

## 인터페이스

### Root

| Prop | TDS 타입/기본값 | 이 구현 |
|---|---|---|
| `open` | `boolean`, 필수 | `defineModel`(`v-model:open`) — React의 `open`+`onClose` 분리를 Vue의 양방향 바인딩 하나로 합쳤다 |
| `title` | `ReactNode`, 필수 | `string` |
| `description` | `ReactNode`, 선택 | `string` |
| `cancelButton` / `confirmButton` | 버튼 엘리먼트를 통째로 받는 슬롯, 필수 | **슬롯이 아니라 좁은 prop**(`cancelText`/`confirmText`/`danger`/`loading`) — 아래 설명 |
| `closeOnDimmerClick` | `boolean`, 기본 `true` | `boolean`, **기본값을 `danger`에서 파생**(아래 설명) |
| `closeOnBackEvent` | `boolean`, 기본 `true` | 구현 안 함(아래 "TDS에서 가져오지 않은 것") |
| `onClose` | 콜백, 필수 | `@cancel` 이벤트 + `v-model:open`이 같은 역할 |
| `onEntered` / `onExited` | 애니메이션 콜백, 선택 | 구현 안 함 |
| `portalContainer` | 렌더링 위치, 기본 `document.body` | 구현 안 함 |

### CancelButton / ConfirmButton

| | TDS 기본값 | 이 구현 |
|---|---|---|
| CancelButton | `type="dark"` `style="weak"` `size="large"` | `<Button variant="weak" color="dark">` — size는 `medium`(기본값 그대로, 아래 설명) |
| ConfirmButton | Button 전체 상속, `size="large"` | `<Button :color="danger ? 'danger' : 'primary'">` — size는 `medium` |

### Title / Description 프리셋

| | TDS 기본값 | 이 구현 |
|---|---|---|
| Title | `typography="t4"`(20px) `fontWeight="bold"` `color=grey800` | `text-20 font-bold text-grey-800` — **그대로 따름** |
| Description | `typography="t6"`(15px) `fontWeight="medium"` `color=grey600` | `text-15 font-medium text-grey-700` — **색만 예외** |

## `cancelButton`/`confirmButton`을 슬롯으로 열지 않은 이유

TDS는 두 버튼을 임의의 엘리먼트를 통째로 받는 슬롯으로 둔다 — 호출부가 버튼을 완전히 다르게 구성할 수 있다는 뜻이다. 이 구현은 일부러 그렇게 하지 않았다. 텍스트·`danger`·`loading`만 받는 좁은 prop으로 고정했다 — 슬롯으로 열어두면 화면마다 버튼을 다르게 구성하게 되고, 그러면 이 컴포넌트를 만든 이유(앱 전체의 위험 안내를 하나로 통일하는 것)가 무너진다. TDS 인터페이스를 기계적으로 옮기지 않고, 이 컴포넌트의 목적에 맞게 의도적으로 좁혔다.

## `closeOnDimmerClick` — 기본값을 `danger`에서 파생시킨다

TDS 기본값은 `true`(딤머를 누르면 닫힌다)다. 이 프로젝트는 그 기본값을 그대로 쓰지 않고, **prop을 지정하지 않으면 `danger`의 반대값**을 쓴다.

```ts
const allowImplicitClose = computed(() => props.closeOnDimmerClick ?? !props.danger)
```

되돌릴 수 없는 결정(`danger`)은 실수로 딤머를 눌러 닫히면 안 되고, 일반 확인은 TDS 기본값대로 편하게 닫혀도 된다. 필요하면 `closeOnDimmerClick`을 명시해 이 자동 판단을 덮어쓸 수 있다. `Escape` 키도 같은 판단을 따른다 — TDS는 이걸 별도 prop(`closeOnBackEvent`)으로 분리하지만, 이 프로젝트는 "명시적 버튼 클릭이 아닌 모든 암묵적 닫기"를 하나의 판단으로 묶었다.

### 닫히지 않을 때 흔들림으로 알려준다

TDS 문서는 `closeOnDimmerClick=false`일 때 딤머를 누르면 "흔들림 애니메이션"을 보여주라고 명시한다. 이유가 명확하다 — 아무 반응이 없으면 클릭이 안 먹은 건지 의도적으로 막힌 건지 구분이 안 된다. `theme.css`에 `--animate-shake` 토큰과 `@keyframes shake`를 등록하고, 딤머·`Escape`가 막힐 때 `DialogContent`에 `animate-shake` 클래스를 짧게 얹는다.

## Title/Description — 색상 하나만 TDS와 다르다

TDS 기본값을 그대로 따르되 **Description의 글자색만 예외**를 뒀다. TDS는 `grey600`을 쓰는데, 흰 배경 위에서 `3.32:1`로 WCAG AA(4.5:1)에 못 미친다 — [02-typography.md](./02-typography.md)에서 사이트 전체의 `text-grey-600`을 `text-grey-700`(`8.18:1`)으로 옮기며 이미 고친 문제와 정확히 같은 값이다. 여기서만 TDS 기본값을 되살리면 고쳤던 버그를 다시 집어넣는 셈이라, `grey-700`을 그대로 쓴다.

Title의 `grey800`(`11.51:1`)은 대비 문제가 없어 TDS 기본값을 그대로 따랐다. `font-bold`도 TDS 기본값(`bold`)을 따른 것이다 — `DialogTitle`의 기본 굵기는 `font-medium`이라, `ConfirmDialog`에서 명시적으로 덮어써야 했다.

## 버튼 크기 — TDS `large` 대신 우리 기본값 `medium`을 쓴다

TDS는 ConfirmDialog의 두 버튼에 `size="large"`를 기본값으로 준다. 이건 TDS Mobile이 손가락 터치를 기준으로 크기를 잡기 때문이다 — 이 프로젝트는 데스크톱 웹이고, 다이얼로그 패널 자체도 `max-w-sm`(384px)으로 좁게 잡혀 있다. `large`(48px)를 강제하면 좁은 패널에 비해 버튼이 과하게 커 보인다. `Button`의 기본값(`medium`, 38px)을 그대로 두는 쪽이 이 프로젝트의 실제 밀도에 맞는다 — [03-button.md](./03-button.md)에서 전체 기본 크기를 `xlarge`(TDS) 대신 `medium`으로 정한 것과 같은 판단이다.

## TDS에서 가져오지 않은 것

- **`closeOnBackEvent`** — 네이티브 앱의 하드웨어 뒤로가기, 또는 모바일 브라우저의 뒤로가기 제스처를 가로채는 기능이다. 데스크톱 웹에는 이에 대응하는 제스처가 없고, 브라우저 히스토리(`history.pushState`)에 개입해야 하는 별개의 기능이라 지금 필요하지 않다.
- **`onEntered`/`onExited`** — 애니메이션 완료 후 콜백. Vue의 `<Transition>`이 이미 `@after-enter`/`@after-leave`로 같은 걸 제공한다(Reka UI의 데이터 속성 기반 애니메이션이 내부적으로 이를 쓴다). 지금 이 콜백이 필요한 화면이 없어 노출하지 않았다 — 필요해지면 이미 있는 메커니즘을 연결하면 된다.
- **`portalContainer`** — Reka UI의 `DialogPortal`이 Vue `Teleport`의 `to` prop을 이미 지원한다. TDS와 같은 기능을 기반 라이브러리가 이미 갖고 있어 다시 만들지 않는다 — [03-button.md](./03-button.md)의 `as`/`asChild`와 같은 이유다.

## AlertDialog는 만들지 않는다

TDS는 ConfirmDialog(버튼 2개) 옆에 AlertDialog(버튼 1개)도 문서화한다. 두 문서를 대조해 보면 AlertDialog는 `closeOnDimmerClick`·`closeOnBackEvent`·`portalContainer`·Title/Description 프리셋까지 ConfirmDialog와 구조가 완전히 같고, **버튼이 하나뿐이라는 것 외에 새로운 게 없다.**

전용 `AlertDialog` 컴포넌트를 따로 만들지 않았다. 단일 버튼 알림창이 필요해지면 [06-dialog.md](./06-dialog.md)의 원시 부품(`Dialog`·`DialogContent`·`DialogHeader`·`DialogTitle`·`DialogDescription`·`DialogFooter`)으로 그 자리에서 바로 조립하면 된다 — 그러려고 원시 부품을 구체 컴포넌트와 별도로 만들어 뒀다. 딱 한 번 쓰일 조합을 위해 컴포넌트를 미리 만들어 두는 건 실체 없는 코드를 유지보수 부담으로 남기는 것이다.

## 다른 프로젝트에서 재사용하는 방법

1. [01-colors.md](./01-colors.md)·[02-typography.md](./02-typography.md)·[03-button.md](./03-button.md)·[06-dialog.md](./06-dialog.md)를 먼저 옮긴다.
2. 원본 문서가 버튼을 슬롯(임의 엘리먼트)으로 열어 둬도, 이 컴포넌트의 목적이 "일관성 강제"라면 좁은 prop으로 의도적으로 제한한다. 유연성보다 일관성이 우선인 컴포넌트라는 걸 인터페이스로도 보여주는 것이다.
3. "암묵적으로 닫기"(딤머 클릭, Escape, 뒤로가기)를 언제 막을지는 다른 prop(`danger` 등)에서 파생시킨다 — 매번 명시적으로 지정하게 하면 위험한 다이얼로그를 실수로 안전하게 만드는 걸 잊기 쉽다.
4. 원본이 "닫히지 않을 때 시각 피드백을 줘라" 같은 지침을 명시했으면 반드시 구현한다 — 아무 반응 없는 UI는 고장난 것처럼 보인다.
5. 원본의 기본 색상값이 이 프로젝트의 접근성 기준에 못 미치면, 원본을 따르지 않고 이미 고친 값을 유지한다. 어떤 색을 왜 다르게 썼는지 표로 명시한다.
6. 원본이 터치 기기 기준으로 큼직하게 잡은 크기(버튼 등)를, 이 프로젝트의 실제 화면 밀도(데스크톱 웹의 좁은 다이얼로그 등)에 맞춰 그대로 따를지 판단한다.
7. 원본 문서에 있는 두 변형(TDS의 AlertDialog/ConfirmDialog처럼)이 구조적으로 거의 같고 하나가 다른 하나의 부분집합이면, 둘 다 전용 컴포넌트로 만들지 않는다. 실제로 쓰는 쪽만 구체 컴포넌트로 만들고, 나머지는 원시 부품으로 그때 조립한다.
