# Input

**원천 파일**: [`apps/frontend/src/shared/ui/input/`](../../frontend/src/shared/ui/input/) (`Input.vue`)
**전제**: [01-colors.md](./01-colors.md)·[02-typography.md](./02-typography.md)·[03-button.md](./03-button.md)를 먼저 읽는다.

## 왜 이렇게 만들었나

이 컴포넌트는 지금까지의 방식과 방향이 다르다. Button·Badge·Dialog·Tab은 **TDS가 컴포넌트를 나눈 단위 그대로** 이 프로젝트의 컴포넌트를 대응시켰다. Input은 그렇게 하지 않았다.

shadcn(이 프로젝트가 쓰는 UI 프리미티브 생성기)은 텍스트를 입력받는 컴포넌트를 **`Input` 하나**로 둔다. 반면 TDS는 이걸 `TextField`·`TextArea`·`SearchField` 세 개의 별도 컴포넌트로 나눈다. 처음엔 TDS를 따라 `TextField.vue`·`TextArea.vue`를 새로 만들었는데, 그러면 **이 프로젝트가 원래 갖고 있던 구조(shadcn의 Input 하나)를 버리고 TDS의 구조로 바꾸는** 것이 된다. 이 프로젝트가 지금까지 해 온 건 그게 아니었다 — shadcn이 만든 컴포넌트는 그대로 두고, 그 안의 **색·크기·상태 규칙**만 TDS를 참고해 채워 넣는 것이었다.

그래서 다시 만들었다. **`Input` 컴포넌트 하나**를 유지하고, TDS가 세 컴포넌트로 나눠 각각 문서화한 인터페이스를 **전부 이 하나에 흡수**했다. `multiline` prop 하나로 한 줄/여러 줄을 오가고, `clearable` prop 하나로 TextField의 지우기 버튼과 SearchField의 내장 지우기 버튼을 둘 다 흡수했다.

## 세 TDS 문서를 하나로 흡수한 근거

| TDS 문서 | 핵심 개념 | 이 컴포넌트에서 |
|---|---|---|
| [TextField](https://tossmini-docs.toss.im/tds-mobile/components/TextField/text-field/) | 한 줄 입력, variant/label/help/error | 기본 동작 그대로 |
| [TextArea](https://tossmini-docs.toss.im/tds-mobile/components/TextField/text-area/) | "TextField를 확장하고 prefix/suffix/right만 뺀 것" | `multiline: true` — TDS 문서가 스스로 "확장 관계"라고 밝힌 걸 그대로 반영했다. 새 컴포넌트가 아니라 같은 컴포넌트의 한 상태다 |
| [SearchField](https://tossmini-docs.toss.im/tds-mobile/components/search-field/) | "내장 지우기 버튼이 있는 TextField" | `clearable: true` — SearchField 고유 기능(`onDeleteClick`)이 TextField의 `TextField.Clearable`과 본질적으로 같은 기능이라, 이미 있는 `clearable`이 그대로 커버한다 |

TDS 사이드바에서 "input"(텍스트를 입력받는) 개념에 해당하는 컴포넌트는 이 셋이 전부였다. Checkbox·Switch·Slider·Segmented Control 같은 나머지는 텍스트 입력이 아니라 **선택**(choice)을 다루는 컴포넌트라 이 범주에 넣지 않았다.

## 인터페이스

| Prop | 출처 | 타입/기본값 |
|---|---|---|
| `variant` | TextField | `"box"` \| `"line"` \| `"big"` \| `"hero"`, 필수 |
| `multiline` | TextArea | `boolean`, 기본 `false` |
| `label` | TextField | `string` |
| `labelOption` | TextField | `"appear"` \| `"sustain"`, 기본 `appear` |
| `help` | TextField | `string`(TDS는 `ReactNode` — [07-confirm-dialog.md](./07-confirm-dialog.md)의 title/description과 같은 이유로 단순화) |
| `hasError` | TextField | `boolean`, 기본 `false` |
| `disabled` | TextField | `boolean`, 기본 `false` |
| `prefix` / `suffix` | TextField | `string` (`multiline`일 때는 무시 — TDS TextArea도 이 셋을 뺀다) |
| `right` | TextField | `right` 슬롯 (`multiline`일 때는 무시) |
| `placeholder` | TextField | `string` |
| `clearable` | TextField.Clearable / SearchField | `boolean`, 기본 `false` |
| `type` | (네이티브 HTML) | `string`, 기본 `text` |
| `minHeight` / `height` | TextArea | `number`(px) |
| `value`/`defaultValue`/`onChange` | TextField | `modelValue`(Vue `v-model`) |

## `multiline` — 높이 모델만 갈린다

```
multiline: boolean = false
```

`false`(TextField)면 `variant`가 고정 높이를 정하고, `true`(TextArea)면 최소 높이로 바뀌고 세로로만 늘어난다(`resize-y`). 테두리·모서리·글자 크기는 두 모드가 **완전히 같은 규칙**을 쓴다 — `variant`가 그 값을 결정하고, `multiline`은 높이 모델만 바꾼다.

| variant | 한 줄(고정 높이) | 여러 줄(최소 높이) | 모서리 | 글자 |
|---|---|---|---|---|
| `box` | 38px | 96px | 10px | `text-15` |
| `line` | 38px | 96px | 0 | `text-15` |
| `big` | 48px | 128px | 14px | `text-17` |
| `hero` | 56px | 160px | 16px | `text-20` |

높이 수치는 [03-button.md](./03-button.md)의 높이 리듬(38/48/56)을 그대로 가져왔다 — 새 크기 체계를 발명하지 않고 화면에서 이미 검증된 값을 재사용했다.

## 테두리 색 — `--border` 토큰을 쓰지 않는다

셸 전역 토큰 `--border`(`grey-200`)는 흰 배경과 `1.19:1`이다. 구분선 같은 장식적인 자리는 괜찮지만, 입력창 테두리처럼 "여기가 조작 가능한 영역이다"를 알려야 하는 경계는 WCAG 비텍스트 기준(`3.0:1`)이 적용된다. 이 기준을 넘는 가장 얕은 단계인 **`grey-600`(`3.32:1`)** 을 여기서만 썼다 — 전역 토큰 자체를 바꾸면 위험도가 낮은 다른 용도까지 전부 진해진다.

지우기 버튼 아이콘도 같은 이유로 `grey-600`을 쓴다. `grey-500`(`2.07:1`)으로 처음 만들었다가 계산 후 고쳤다.

## `labelOption`

```
appear(기본): label이 자리표시자로만 보인다. sr-only로 항상 DOM엔 있어 스크린리더에는 전달된다.
sustain:      label이 입력창 위에 항상 보인다.
```

## `clearable`이 켜지면 `right` 슬롯을 덮는다

TDS도 `TextFieldClearableProps`를 "`right`를 제외한 TextField props 확장"이라고 명시한다. 지우기 버튼과 커스텀 우측 콘텐츠는 같은 자리를 두고 경쟁하므로, 이 구현도 `clearable`이 우선한다. 값이 있을 때만 버튼이 보인다.

## 만들지 않은 것

- **`TextField.Password`** — 이 앱은 로그인·인증 화면이 로드맵에 없다.
- **`TextField.Button`**(클릭으로 다른 UI를 여는 필드) — 지금 이 형태가 필요한 화면이 없다.
- **`format`**(입력값 실시간 변환) — 지금 필드는 전부 자유 텍스트다.
- **SearchField의 `fixed`/`takeSpace`**(화면 상단 고정) — 이건 입력창 자체의 성질이 아니라 **페이지 레이아웃의 문제**다. 필요한 화면이 생기면 그 화면에서 `Input`을 sticky 컨테이너로 감싸면 된다 — [07-confirm-dialog.md](./07-confirm-dialog.md)에서 `portalContainer`를 Vue `Teleport`에 맡기고 다시 안 만든 것과 같은 판단이다.
- **`SplitTextField`** — TDS가 TextField 옆에 나란히 문서화하지만, 확인해보니 범용 컴포넌트가 아니라 **한국 주민등록번호 입력 전용**이다(`RRN13`/`RRNFirst7` 두 변형뿐, `label` 기본값도 `'주민등록번호'`로 고정). 이 앱은 개인 성장 기록 도구라 그런 화면이 로드맵에 없다. 원본이 이미 특정 용도에 맞춰 결정을 많이 내려 둔 컴포넌트라, 비슷한 용도(예: 인증번호 입력)가 생겨도 이걸 재활용하기보다 그때 새로 설계하는 게 낫다고 판단했다.

넷 다 "지금 쓰는 곳이 없다"는 이유로 뺐다 — 필요해지면 같은 인터페이스 아래 추가하면 된다.

## 다른 프로젝트에서 재사용하는 방법

1. [01-colors.md](./01-colors.md)·[02-typography.md](./02-typography.md)·[03-button.md](./03-button.md)를 먼저 옮긴다.
2. **참고하는 디자인 시스템의 컴포넌트 경계를, 이 프로젝트가 이미 쓰는 프레임워크의 컴포넌트 경계에 맞춰 조정한다.** 참고하는 쪽이 여러 컴포넌트로 나눠 뒀다고 이쪽도 그대로 나눌 필요는 없다 — 이미 있는 컴포넌트 하나가 그 여러 개념을 자연스럽게 아우를 수 있으면, prop으로 갈래를 나누는 쪽이 낫다. Button·Badge·Dialog·Tab처럼 경계가 원래도 일치하면 그대로 따르고, Input처럼 안 맞으면 이쪽 구조를 유지한다.
3. 참고 문서가 "이 컴포넌트는 저 컴포넌트를 확장하고 일부만 뺀다"고 스스로 명시하면(TDS의 TextArea-extends-TextField처럼), 그 관계를 별도 컴포넌트가 아니라 **같은 컴포넌트의 boolean 분기**로 옮긴다.
4. 참고 문서의 컴포넌트 목록(사이드바 등)을 훑어서, 지금 만드는 컴포넌트와 같은 개념을 공유하는 다른 컴포넌트가 있는지 확인한다(TextField 문서만 보면 SearchField의 존재를 놓친다). 있으면 흡수할지 판단한다.
5. 흡수한 컴포넌트마다 표를 만들어 "이 prop이 원래 어느 문서에서 왔는지" 남긴다 — 나중에 원본 디자인 시스템이 업데이트됐을 때, 이 프로젝트의 어느 부분을 다시 봐야 하는지 추적할 수 있게 한다.
