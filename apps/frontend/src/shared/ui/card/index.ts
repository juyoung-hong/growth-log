/**
 * TDS에는 이 개념(헤더·제목·설명·본문·푸터를 갖는 범용 표면 컨테이너)이
 * 없다 — Post(텍스트 서식)·Board Row(아코디언)·Grid List(그리드 배치
 * 래퍼)·ListRow(자체 표면이 없는 3분할 행)를 전부 확인했지만 어느 것도
 * Card와 맞지 않았다. 자세한 이유는 apps/docs/design/11-card.md에 있다.
 *
 * 그래서 흡수할 TDS 개념은 없고, shadcn 스캐폴드 자체의 결함만 정리했다
 * — CardHeader/CardFooter가 Card 본체와 다른 모서리 값(rounded-xl vs
 * rounded-lg)을 쓰고 있었고, CardFooter가 Card의 원칙("내부는 Border/
 * Separator로 나눈다")을 어기고 자체 테두리를 넣고 있었고, size prop을
 * 위한 선택자가 이미 쓰여 있는데 정작 Card 본체엔 그 prop이 없어 죽은
 * 코드였다.
 */
export { default as Card } from './Card.vue'
export { default as CardAction } from './CardAction.vue'
export { default as CardContent } from './CardContent.vue'
export { default as CardDescription } from './CardDescription.vue'
export { default as CardFooter } from './CardFooter.vue'
export { default as CardHeader } from './CardHeader.vue'
export { default as CardTitle } from './CardTitle.vue'
