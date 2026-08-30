# Dialog

**원천 파일**: [`apps/frontend/src/shared/ui/dialog/`](../../frontend/src/shared/ui/dialog/)
**전제**: [01-colors.md](./01-colors.md)의 팔레트·시맨틱 토큰, [02-typography.md](./02-typography.md)의 크기 스케일, [03-button.md](./03-button.md)의 인터페이스를 먼저 읽는다.

## 왜 이렇게 만들었나

[TDS Dialog 개요 문서](https://tossmini-docs.toss.im/tds-mobile/components/Dialog/dialog/)는 그 자체로 하나의 컴포넌트가 아니다. **AlertDialog**(확인 버튼 하나)와 **ConfirmDialog**(취소/확인 두 버튼) 두 구체적인 하위 컴포넌트로 나뉘고, 각각 별도 문서(`/Dialog/alert-dialog/`, `/Dialog/confirm-dialog/`)에 자기만의 props 표가 있다. 개요 문서는 props 표 대신 **구조 가이드**만 준다 — Title → Description → Button(들) 순서로 구성한다는 것.

이 문서가 다루는 건 그 구조를 만드는 **원시 부품**(`shared/ui/dialog/`)이다. TDS의 ConfirmDialog에 대응하는 이 프로젝트의 구체 컴포넌트는 `shared/ui/confirm-dialog/ConfirmDialog.vue`이고, [07-confirm-dialog.md](./07-confirm-dialog.md)에서 별도로 다룬다. 여기서는 그 위에서 쓰는 하부 조립 부품(Dialog·DialogContent·DialogHeader·DialogTitle·DialogDescription·DialogFooter 등)이 TDS의 구조 가이드와 이 프로젝트의 토큰 체계를 제대로 따르는지를 정리한다.

기반 구현은 shadcn-vue가 생성한 [Reka UI](https://reka-ui.com/) `Dialog` 프리미티브다.

## 구성 요소 — TDS의 Title → Description → Button 구조를 그대로 따른다

| 구성 요소 | TDS 대응 | 역할 |
|---|---|---|
| `Dialog` | — | 열림/닫힘 상태를 관리하는 루트. Reka `DialogRoot`를 그대로 감싼다 |
| `DialogTrigger` | — | 다이얼로그를 여는 트리거 |
| `DialogOverlay` | — | 뒤 화면을 어둡게 덮는 딤머 |
| `DialogContent` | (전체 패널) | 화면 크기에 맞는 표준 다이얼로그. 내부가 짧을 때 |
| `DialogScrollContent` | (전체 패널) | 내용이 길어 화면을 넘길 수 있는 다이얼로그. 스크롤 처리가 다르다(아래 참고) |
| `DialogHeader` | Title + Description을 담는 영역 | |
| `DialogTitle` | `AlertDialog.Title` / `ConfirmDialog.Title` | 메인 메시지 |
| `DialogDescription` | `AlertDialog.Description` / `ConfirmDialog.Description` | 보조 설명(선택) |
| `DialogFooter` | Button 영역 | 버튼을 오른쪽 정렬로 담는다 |
| `DialogClose` | — | 우측 상단 닫기 버튼과, 임의 위치의 닫기 트리거 둘 다에 쓴다 |

`DialogHeader`(Title+Description) → 본문 → `DialogFooter`(Button)라는 배치 순서가 TDS 구조 가이드 그대로다.

## `DialogContent` vs `DialogScrollContent` — 언제 무엇을 쓰나

- **`DialogContent`**: 표준. 화면 중앙에 고정 위치(`fixed top-1/2 left-1/2` + transform)로 뜬다. 확인창처럼 내용이 짧을 때.
- **`DialogScrollContent`**: 내용이 길어질 수 있는 폼(예: 태스크 생성처럼 필드가 많은 다이얼로그)에 쓴다. 오버레이 자체가 `grid place-items-center overflow-y-auto`인 스크롤 컨테이너라, 다이얼로그가 뷰포트보다 커지면 오버레이 안에서 스크롤된다. `DialogContent`는 이 구조가 없어서 내용이 넘치면 화면 밖으로 잘린다.

## 발견한 문제 — 방치된 컴포넌트가 이미 고친 것들과 어긋나 있었다

`DialogScrollContent`는 이 프로젝트에서 **아직 아무 화면도 쓰지 않는다.** 그래서 `DialogContent`·`DialogOverlay`를 TDS 토큰에 맞춰 고칠 때 같이 고쳐지지 않고 shadcn 스캐폴드 원본 그대로 남아 있었다. 실제로 대조해보니 넷이 어긋나 있었다.

| | `DialogOverlay`(고쳐진 기준) | `DialogScrollContent`(방치됨) |
|---|---|---|
| 딤머 색 | `bg-black/10` | `bg-black/80` — **8배 진함** |
| 그림자 | 없음 | `shadow-lg` |
| 테두리 | 없음 | `border border-border` |
| 닫기 버튼 | `<Button variant="weak" color="light" size="icon">` | 우리 Button을 안 쓰는 raw 마크업 |
| 애니메이션 문법 | `data-open:`/`data-closed:`(tw-animate-css 커스텀 변형) | `data-[state=open]:`(예전 Radix bracket 문법) |

**이번에 전부 고쳤다.** 핵심은 딤머를 중복 선언하지 않고 `<DialogOverlay>` 컴포넌트를 그대로 가져다 쓰는 것으로 구조를 바꾼 것이다.

```vue
<!-- 딤머 색을 이 파일에서 다시 선언하지 않는다. class로 스크롤 레이아웃만 얹는다 -->
<DialogOverlay class="grid place-items-center overflow-y-auto p-4">
  <DialogContent ...>
    <slot />
  </DialogContent>
</DialogOverlay>
```

이렇게 하면 딤머 색이 코드베이스에 **한 곳**(`DialogOverlay.vue`)에만 존재한다. 나중에 딤머를 다시 조정할 일이 생겨도 두 곳을 기억해서 같이 고칠 필요가 없다 — ProgressBar의 `color` prop을 만들 때 셀렉터 우회를 없앤 것과 같은 종류의 정리다([05-progress.md](./05-progress.md) 참고).

`@pointer-down-outside` 핸들러는 남겨 뒀다 — 스크롤 컨테이너 특유의 문제(오버레이의 여백을 눌러도 "바깥 클릭"으로 잡히는 것)를 막는 실제 필요한 로직이라, 왜 있는지 주석으로 남기고 그대로 뒀다.

## 토큰 사용 확인

- **색**: `bg-popover`/`text-popover-foreground`(시맨틱 토큰, [01-colors.md](./01-colors.md)) — 리터럴 hex나 `bg-white` 대신 의미 이름을 쓴다. 지금은 `--popover`와 `--background`가 같은 값(흰색)이지만, 나중에 배경과 떠 있는 패널의 색을 다르게 주고 싶을 때 이 이름 하나만 바꾸면 된다.
- **타이포**: `DialogTitle`은 `text-16`, `DialogDescription`은 `text-14`([02-typography.md](./02-typography.md)) — Tailwind 기본 `text-base`/`text-sm`이 남아 있던 걸 타이포그래피 작업 때 이미 옮겼다.
- **모서리 반지름**: `rounded-lg` = `theme.css`의 `--radius`(20px). Card와 같은 값을 그대로 쓴다 — 다이얼로그도 카드처럼 "떠 있는 흰 패널"이라 같은 반지름 어법이 자연스럽다.
- **그림자**: 쓰지 않는다. 딤머(`bg-black/10`)만으로 배경과 구분한다 — Card가 그림자 없이 배경색 차이만으로 면을 구분하는 것과 같은 원칙이다.
- **닫기 버튼**: `Button` 컴포넌트를 그대로 쓴다(`variant="weak" color="light" size="icon"`) — 새 버튼 스타일을 여기서 따로 만들지 않는다.

## `DialogFooter` — 회색 배경을 뺐다

shadcn 원본은 `DialogFooter`에 `bg-muted/50`(회색 반투명 채움)을 깔았다. `ConfirmDialog`처럼 버튼 두 개뿐인 짧은 푸터에서는 이 회색 면이 실제 내용(버튼)보다 훨씬 두꺼운 띠로 보여서, 본문(흰 배경)과 대비가 과했다 — 글자는 작고 버튼 영역만 색이 있는 덩어리로 도드라지는 형태였다.

배경을 완전히 지우고 `border-t` 하나로만 본문과 구분한다. 패널 전체가 흰 배경 하나로 이어지고, 위쪽 얇은 구분선만으로 "여기부터 액션 영역"이라는 걸 알려준다 — Card가 그림자 대신 배경색 차이(그리고 그마저 최소화)로 면을 나누는 원칙과 같은 방향이다. `DialogFooter`는 공용 부품이라 이 변경은 `ConfirmDialog`뿐 아니라 `PersonFormDialog` 같은 폼 다이얼로그의 푸터에도 그대로 적용된다.

## 접근성 — Reka UI가 이미 처리하는 것

포커스 트랩(다이얼로그가 열리면 포커스가 안에 갇힌다), `Escape` 키로 닫기, `aria-modal`·`role="dialog"` 같은 접근성 속성은 전부 Reka UI의 `DialogRoot`/`DialogContent`가 기본 제공한다. 이 프로젝트에서 별도로 구현한 것은 없다 — Button의 `as`처럼, 기반 라이브러리가 이미 하는 일을 다시 만들지 않는다.

`ConfirmDialog.vue`([07-confirm-dialog.md](./07-confirm-dialog.md))는 여기에 한 가지를 더한다 — 되돌릴 수 없는 결정(`danger`)일 때는 딤머 클릭이나 `Escape`로 안 닫히고, 대신 흔들림으로 "지금은 못 닫는다"는 걸 알려준다. 명시적으로 버튼을 눌러야만 닫히게 하려는 의도적 선택이다.

## 다른 프로젝트에서 재사용하는 방법

1. `01-colors.md`·`02-typography.md`·`03-button.md`를 먼저 옮긴다.
2. 원본 디자인 시스템의 Dialog가 개요 문서만 있고 구체적인 하위 타입(AlertDialog/ConfirmDialog 같은)으로 나뉜다면, **하위 타입 각각을 별도 문서로 다루고, 이 문서는 그 바탕이 되는 원시 부품만 다룬다.** 개요 문서의 구조 가이드(Title→Description→Button 순서 같은)를 원시 부품의 배치 순서로 그대로 옮긴다.
3. 같은 역할(다이얼로그 패널)을 하는 컴포넌트가 여러 변형(표준/스크롤형 등)으로 있다면, **색이나 애니메이션처럼 변형과 무관한 값은 한 컴포넌트에서만 선언하고 나머지는 그걸 재사용한다.** 값을 복붙해 두면 하나만 고치고 나머지를 놓치는 사고가 난다 — 이번에 발견한 문제가 정확히 그 경우였다.
4. 아직 화면에서 안 쓰는 컴포넌트도 주기적으로 대조 확인한다. "안 쓰니까 안 고쳐도 된다"가 아니라, 쓰는 컴포넌트를 고칠 때 **쌍을 이루는 안 쓰는 컴포넌트도 같이 확인**한다 — 나중에 누군가 그걸 처음 쓰기 시작했을 때 이미 낡아 있으면 그 사람이 원인을 모른 채 고생한다.
5. 포커스 트랩·키보드 닫기 같은 접근성은 기반 프리미티브 라이브러리(Reka UI 등)가 이미 구현했는지 먼저 확인한다. 없는 것만 프로젝트에서 추가한다.
