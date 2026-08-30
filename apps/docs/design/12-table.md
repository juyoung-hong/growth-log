# Table

**원천 파일**: [`apps/frontend/src/shared/ui/table/`](../../frontend/src/shared/ui/table/) (`Table.vue` 등 9개 파일 + `TableInfoRow.vue`)
**전제**: [01-colors.md](./01-colors.md)·[02-typography.md](./02-typography.md)·[11-card.md](./11-card.md)를 먼저 읽는다.

## 왜 이렇게 만들었나

TDS 사이드바에서 "table"이라는 이름을 가진 컴포넌트는 [Table Row](https://tossmini-docs.toss.im/tds-mobile/components/table-row/) 하나뿐이었다. 열어 보니 **이름과 실제가 다르다** — 문서가 스스로 이렇게 말한다.

> TableRow는 실제 HTML 테이블 행이 아니다. "정보를 간결하고 읽기 쉽게 나란히 배치"하기 위한 레이아웃 컴포넌트다.

TDS의 TableRow는 왼쪽에 라벨, 오른쪽에 값을 두는 **2분할 정보 표시 행**이다 — 담당자, 거래 상세, 설정 항목처럼 "이름: 값" 형태를 보여줄 때 쓴다. shadcn의 `Table`(진짜 `<table>`을 감싸는 다중 컬럼 그리드)과는 근본적으로 다른 개념이다.

## 두 개념을 같은 폴더 안에서, 다른 파일로 나눴다

`shared/ui/table/`이라는 **경계(폴더)는 유지**하면서, 서로 다른 HTML 구조가 필요한 두 개념을 **다른 파일**로 나눴다.

| | 무엇인가 | HTML | 파일 |
|---|---|---|---|
| 기존 Table 계열 | 다중 컬럼 그리드 데이터 | 진짜 `<table>`/`<tr>`/`<td>` | `Table.vue`~`TableRow.vue`(9개, 그대로 유지) |
| TDS TableRow | 2분할 키-값 정보 행 | 순수 `<div>` flex(테이블 아님) | `TableInfoRow.vue`(신규) |

기존 `TableRow`(shadcn)는 실제 `<tr>`이라 `<table>`/`<tbody>` 안에서만 유효한 HTML이다. TDS의 TableRow는 문서가 명시한 대로 테이블이 아니라서, 이 자리에 끼워 넣으면 잘못된 HTML이 된다(테이블 밖에서 `<tr>`를 쓰는 셈이 된다). 그래서 **억지로 기존 `TableRow`를 확장하지 않고, 새 파일을 같은 폴더에 뒀다** — [06-dialog.md](./06-dialog.md)에서 `DialogContent`와 `DialogScrollContent`를 같은 `dialog/` 폴더 안에 별개 파일로 둔 것과 같은 판단이다. Input의 `multiline`처럼 하나의 파일 안에서 prop으로 갈랐던 것과는 다르다 — 그때는 `<input>`/`<textarea>`가 둘 다 flex wrapper 안에 자유롭게 들어갈 수 있는 인라인 요소였지만, 여기는 한쪽이 `<table>` 안에서만 유효한 HTML이라 같은 파일로 합칠 수 없다.

## `TableInfoRow` 인터페이스

| Prop | TDS 타입/기본값 | 이 구현 |
|---|---|---|
| `left` | `ReactNode`, 필수 | `left` 슬롯 |
| `right` | `ReactNode`, 필수 | `right` 슬롯 |
| `align` | `"left"` \| `"space-between"`, 필수(기본값 없음) | 동일한 두 값, **기본값 `space-between`을 추가** — "왼쪽 라벨 : 오른쪽 값"이 가장 흔한 모양이라 매번 지정할 필요가 없게 했다 |
| `leftRatio` | `number`(%) | 동일 — 왼쪽 영역의 고정 폭 비율. 안 주면 내용 크기만큼만 차지한다 |

`left`/`right`를 문자열 prop이 아니라 **슬롯**으로 만들었다 — TDS 문서도 "문자열, 숫자, 컴포넌트 모두 받는다"고 하고, 실제로 왼쪽에 아이콘+라벨, 오른쪽에 Badge를 넣는 조합이 이 앱에서도 나올 법하다(예: 태스크 상세의 "상태: [배지]").

### 정렬은 `align`에 따라 값 쪽도 같이 바뀐다

`space-between`이면 값이 오른쪽 끝에 붙어야 자연스러워 `text-right`를 준다. `left`면 라벨과 값이 둘 다 왼쪽에 뭉쳐야 하는데, 이때 값만 오른쪽 정렬하면 어색하게 떨어져 보인다 — 그래서 `left`일 땐 값도 왼쪽 정렬로 둔다.

## 색상

라벨은 `text-grey-700`(`8.18:1`), 값은 `text-grey-900`(`15.43:1`) — 둘 다 흰 배경 기준 WCAG AA를 넉넉히 넘긴다. 라벨을 더 옅게, 값을 더 진하게 둬서 "이건 이름표고, 이게 실제 정보"라는 위계를 색으로도 드러냈다.

## 기존 Table 계열은 왜 안 건드렸나

대조하면서 확인했지만, 기존 `Table`/`TableHeader`/`TableRow`/`TableCell` 등은 [11-card.md](./11-card.md)의 CardHeader/CardFooter 같은 자기모순(다른 모서리 값, 원칙 위반, 죽은 prop)이 없었다. 이미 [02-typography.md](./02-typography.md) 작업 때 `text-sm`/`text-base`를 우리 스케일로 옮겨 뒀고, 나머지는 셀렉터가 가리키는 대상(`data-state=selected`, `has-aria-expanded`)이 지금 이 앱에서 안 쓰이고 있을 뿐 서로 어긋나 있진 않았다 — 나중에 정렬 가능한 헤더나 펼침 행이 필요해지면 그대로 쓸 수 있게 남겨 뒀다.

테두리 색(`--border` = grey-200, `1.19:1`)도 그대로 뒀다. [09-input.md](./09-input.md)에서 텍스트필드 테두리는 "여기가 조작 영역이다"를 알리는 자리라 `grey-600`으로 올렸지만, 테이블 행 구분선은 Separator와 같은 성격이다 — 사용자가 눌러야 할 경계가 아니라 내용을 훑어보기 쉽게 나누는 장식적 구분이라, 더 엄격한 3.0:1 기준을 적용하지 않았다.

## 다른 프로젝트에서 재사용하는 방법

1. [01-colors.md](./01-colors.md)·[02-typography.md](./02-typography.md)·[11-card.md](./11-card.md)를 먼저 읽는다.
2. 참고 문서의 컴포넌트 이름이 이 프로젝트의 기존 컴포넌트와 같아도(TDS "Table Row" vs shadcn "TableRow"), **이름이 같다고 같은 개념이라고 가정하지 않는다.** 열어서 실제 정의를 확인한다 — 이번처럼 이름은 같은데 완전히 다른 것을 가리킬 수 있다.
3. 두 개념을 통합할 때, 서로 다른 HTML 구조가 필요하면(하나는 `<table>` 안에서만 유효, 하나는 아무 데나 놓을 수 있음) 같은 파일 안에서 prop으로 가르지 않는다. **같은 폴더(경계)에 별개 파일**로 두고, 왜 파일을 나눴는지 `index.ts` 상단에 남긴다.
4. 접근성 기준(3.0:1 등)을 어디에 적용할지는 "사용자가 조작해야 하는 경계인가, 내용을 눈으로 훑을 때 도와주는 장식적 구분인가"로 판단한다. 모든 테두리에 같은 기준을 기계적으로 적용하지 않는다.
