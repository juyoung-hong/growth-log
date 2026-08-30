# Card

**원천 파일**: [`apps/frontend/src/shared/ui/card/`](../../frontend/src/shared/ui/card/) (`Card.vue` + `CardHeader.vue` + `CardTitle.vue` + `CardDescription.vue` + `CardAction.vue` + `CardContent.vue` + `CardFooter.vue`)
**전제**: [01-colors.md](./01-colors.md)를 먼저 읽는다.

## 이 문서는 지금까지와 다르다 — TDS에 대응하는 개념이 없다

[09-input.md](./09-input.md)·[10-alert.md](./10-alert.md)와 같은 절차(TDS 사이드바에서 개념이 겹치는 컴포넌트를 찾아 흡수)를 Card에도 적용해 봤다. **찾지 못했다.** TDS는 "헤더·제목·설명·본문·푸터를 갖는 범용 표면 컨테이너"라는 개념 자체가 없다.

## 확인한 후보 넷

| TDS 컴포넌트 | 정체 | Card와 맞나 |
|---|---|---|
| [Post](https://tossmini-docs.toss.im/tds-mobile/components/post/) | 제목·본문·목록의 텍스트 서식 도구(`Post.H1`~`H4`, `Post.Paragraph`, `Post.Ul`/`Ol`) | 아니다 — 표면(surface)이 아니라 텍스트 타이포그래피 프리셋 모음이다 |
| [Board Row](https://tossmini-docs.toss.im/tds-mobile/components/board-row/) | 펼침/접힘이 있는 아코디언 행(Q&A용) | 아니다 — 정적 컨테이너가 아니라 별개의 상호작용 패턴(`isOpened`/`onOpen`/`onClose`)이다 |
| [Grid List](https://tossmini-docs.toss.im/tds-mobile/components/grid-list/) | 이미지+텍스트 항목을 그리드로 배치하는 레이아웃 래퍼(`column: 1\|2\|3`) | 아니다 — 컨테이너 자체가 아니라 배치 규칙이다 |
| [ListRow](https://tossmini-docs.toss.im/tds-mobile/components/ListRow/list-row-overview/) | 왼쪽/본문/오른쪽 3분할 행 | 아니다 — 문서가 스스로 "자체 배경·테두리가 없다"고 명시한다. **Card 같은 것 안에 들어가는 용도**지 Card 자체가 아니다 |

넷 다 확인은 했지만 흡수하지 않았다. 억지로 하나를 골라 Card에 끼워 맞추면, [09-input.md](./09-input.md)의 재사용 절차 5번("비슷해 보인다고 억지로 범용화하면 원본에도 새 용도에도 안 맞는 어중간한 컴포넌트가 된다")을 스스로 어기는 셈이다.

## 대신 shadcn 스캐폴드 자체의 결함 셋을 고쳤다

TDS와 대조하다가, Card가 애초에 shadcn 스캐폴드에서 나온 뒤로 **한 번도 자기 자신과도 앞뒤가 안 맞는 상태**였다는 걸 발견했다.

### ① CardHeader/CardFooter가 Card 본체와 다른 모서리 값을 썼다

Card 본체는 `rounded-lg`(`--radius` = 20px)를 쓴다. 그런데 `CardHeader`는 `rounded-t-xl`, `CardFooter`는 `rounded-b-xl`을 썼다 — `--radius-xl`은 `--radius + 4px` = **24px**로, Card 본체보다 4px 더 크다.

실제로 눈에 보이는 차이는 없었다 — Card에 `overflow-hidden`이 있어서, 안쪽 요소가 어떤 모서리 값을 갖든 Card 자신의 20px 모양대로 잘려 보인다. **바로 그래서 더 나쁜 버그였다** — 겉보기엔 멀쩡해서 아무도 알아채지 못한 채 죽은 코드로 계속 남아 있었을 것이다. `overflow-hidden`을 나중에 다른 이유로 빼는 순간(예: 카드 모서리 밖으로 드롭다운 메뉴가 삐져나가야 하는 경우) 이 불일치가 갑자기 눈에 보이게 된다. 지금 지웠다.

### ② CardFooter가 Card 자신의 원칙을 어기고 있었다

Card.vue의 코드 주석은 이렇게 말한다 — **"내부는 Border(Separator)로 나눈다."** 실제 사용처(`TaskGroupsPage.vue`의 데모 카드)도 그렇게 한다:

```vue
<Progress :model-value="70" />
<Separator variant="full" class="my-4" />
<div class="flex flex-wrap items-center gap-2">...</div>
```

그런데 `CardFooter`는 이 원칙과 무관하게 **자기 혼자 `border-t bg-muted/50`을 자동으로 넣고 있었다.** `<Separator>`를 명시적으로 놓는 자리와, `CardFooter`가 알아서 구분선을 넣는 자리가 뒤섞이면 규칙이 두 갈래로 갈린다 — 화면마다 "여기는 왜 구분선이 자동으로 생기지"를 다시 확인해야 한다. 지웠다. 구분이 필요하면 지금까지 해 온 대로 `<Separator variant="full" />`를 명시적으로 놓는다.

### ③ `size` prop이 죽어 있었다

`CardHeader`·`CardContent`·`CardFooter`·`CardTitle` 네 파일 전부 `group-data-[size=sm]/card:` 선택자를 이미 갖고 있었다 — padding을 줄이고(`px-4`→`px-3`) 제목 글자를 줄이는(`text-16`→`text-14`) 조밀한 변형이다. 그런데 정작 `Card.vue`엔 `size` prop 자체가 없었고 `group/card` 클래스도 없어서, 이 선택자들은 **애초에 반응할 대상이 없는 죽은 셀렉터**였다.

```
size: "default" | "sm" = "default"
```

`Card.vue`에 `size` prop과 `group/card`·`data-size`를 추가해 나머지 넷이 이미 준비해 둔 규칙이 실제로 동작하게 했다. 새 CSS를 만들지 않고, **이미 쓰여 있던 코드를 마저 연결**한 것이다.

## 다른 프로젝트에서 재사용하는 방법

1. [01-colors.md](./01-colors.md)를 먼저 옮긴다.
2. 참고하는 디자인 시스템에서 지금 컴포넌트에 대응하는 걸 찾다가 **못 찾을 수도 있다.** 못 찾은 것 자체가 유효한 결론이다 — 억지로 비슷한 걸 끼워 맞추지 않는다. 무엇을 확인했고 왜 안 맞았는지는 남긴다(이 문서의 "확인한 후보 넷"처럼) — 나중에 또 같은 조사를 반복하지 않도록.
3. 대응하는 개념이 없어도, 그 컴포넌트가 **자기 자신의 다른 부분과 앞뒤가 맞는지**는 별개로 점검한다. 여러 서브 컴포넌트로 쪼개진 컴포넌트(Header/Footer/Title처럼)는 값이 서로 어긋나기 쉽다 — 특히 부모의 `overflow-hidden`처럼 자식의 실수를 가려 주는 속성이 있으면, 겉으로 멀쩡해 보여서 더 오래 방치된다.
4. `group-data-[key=value]/name:` 선택자가 자식들에 이미 쓰여 있는데 부모가 그 `key`를 실제로 설정하지 않고 있으면, 그건 "만들다 만" 축이다. 지울지 마저 연결할지 판단한다 — 이미 준비된 CSS가 있으면 마저 연결하는 쪽이 새로 만드는 것보다 싸다.
5. 컴포넌트 자신이 코드 주석으로 원칙을 남겨 뒀으면(Card의 "Border로 나눈다"처럼), 같은 컴포넌트의 다른 서브 파일이 그 원칙을 실제로 지키고 있는지 대조한다. 주석과 실제 동작이 어긋나 있는 걸 찾는 가장 쉬운 방법이다.
