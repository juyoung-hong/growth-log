/**
 * shadcn의 Table 계열(Table·TableHeader·TableRow·TableCell 등, 실제
 * <table>을 감싸는 다중 컬럼 그리드)은 그대로 유지한다. 여기에 TDS의
 * Table Row 개념을 더한다.
 * https://tossmini-docs.toss.im/tds-mobile/components/table-row/
 *
 * TDS의 "Table Row"는 이름과 달리 실제 HTML 테이블 행이 아니다 — 문서가
 * 스스로 "실제 테이블 행이 아니다"라고 명시한다. 왼쪽에 라벨, 오른쪽에
 * 값을 두는 2분할 정보 표시 행이다("담당자: 홍주영"처럼). shadcn의
 * `<TableRow>`(진짜 <tr>, <table>/<tbody> 안에서만 유효한 HTML)에
 * 억지로 끼워 넣지 않고, 같은 폴더 안에 별도 파일(TableInfoRow.vue)로
 * 뒀다 — <table> 밖에서도 쓸 수 있는 순수 flex 레이아웃이라 <tr>과
 * 같은 자리에 놓일 수 없다.
 *
 * "table"이라는 컴포넌트 경계는 유지하되(같은 폴더·같은 index.ts로
 * export), 서로 다른 HTML 구조가 필요한 두 개념은 각자 다른 파일로
 * 나눈다 — Dialog가 DialogContent/DialogScrollContent처럼 폴더 하나
 * 안에 여러 파일을 두는 것과 같은 방식이다.
 */
export { default as Table } from './Table.vue'
export { default as TableBody } from './TableBody.vue'
export { default as TableCaption } from './TableCaption.vue'
export { default as TableCell } from './TableCell.vue'
export { default as TableEmpty } from './TableEmpty.vue'
export { default as TableFooter } from './TableFooter.vue'
export { default as TableHead } from './TableHead.vue'
export { default as TableHeader } from './TableHeader.vue'
export { default as TableInfoRow } from './TableInfoRow.vue'
export { default as TableRow } from './TableRow.vue'
