# 타이포그래피

**원천 파일**: [`apps/frontend/src/app/styles/theme.css`](../../frontend/src/app/styles/theme.css)
**전제**: [01-colors.md](./01-colors.md)를 먼저 읽는다. 이 문서는 그 문서와 같은 원칙(구조는 TDS 참고, 값은 라이선스 문제 없는 자원, 리셋 후 전 범위 등록)을 타이포그래피에 적용한 것이다.

## 왜 이렇게 만들었나

크기·행간 스케일의 **구조**는 [TDS 타이포그래피 문서](https://tossmini-docs.toss.im/tds-mobile/foundation/typography/)를 참고했다. **폰트는 참고하지 않았다** — TDS가 쓰는 서체(Toss Product Sans)는 상업 라이선스라 가져다 쓸 수 없다. 이 프로젝트는 애초에 그 자리에 [Pretendard](https://github.com/orioncactus/pretendard)를 쓰고 있었고, 이 문서는 그 선택을 그대로 유지한다. TDS 문서의 서체 관련 내용은 전부 무시했다.

> Pretendard, Copyright (c) 2021 Kil Hyung-jin, SIL Open Font License 1.1.
> 라이선스 전문은 `node_modules/pretendard/dist/LICENSE.txt`에 그대로 들어 있다.

## 크기 스케일 — TDS 20단계를 하나로 합친다

TDS는 크기·행간을 두 계열로 나눠 문서화한다.

- **주요 토큰** — Typography 1~7 (7단계)
- **보조 토큰** — sub Typography 1~13 (13단계, 주요 토큰 사이사이를 채운다)

이 둘을 크기 순서로 합치면, **11px부터 30px까지 정수가 하나도 빠짐없이 채워진다.** (7 + 13 = 20단계, 30-11+1 = 20 — 정확히 맞아떨어진다.)

| TDS 원본 | px | 행간(px) | 이 프로젝트의 토큰 이름 |
|---|---|---|---|
| Typography 1 | 30 | 40 | `text-30` |
| sub 1 | 29 | 38 | `text-29` |
| sub 2 | 28 | 37 | `text-28` |
| sub 3 | 27 | 36 | `text-27` |
| Typography 2 | 26 | 35 | `text-26` |
| sub 4 | 25 | 34 | `text-25` |
| sub 5 | 24 | 33 | `text-24` |
| sub 6 | 23 | 32 | `text-23` |
| Typography 3 | 22 | 31 | `text-22` |
| sub 7 | 21 | 30 | `text-21` |
| Typography 4 | 20 | 29 | `text-20` |
| sub 8 | 19 | 28 | `text-19` |
| sub 9 | 18 | 27 | `text-18` |
| Typography 5 | 17 | 25.5 | `text-17` |
| sub 10 | 16 | 24 | `text-16` |
| Typography 6 | 15 | 22.5 | `text-15` |
| sub 11 | 14 | 21 | `text-14` |
| Typography 7 | 13 | 19.5 | `text-13` |
| sub 12 | 12 | 18 | `text-12` |
| sub 13 | 11 | 16.5 | `text-11` |

### 토큰 이름을 `t1`처럼 짓지 않고 실제 px 값으로 지은 이유

이전 버전은 `--text-t1`~`--text-t7`(주요 토큰 7개만)로 이름 붙였는데, 이름만 봐서는 크기를 알 수 없어 표를 찾아봐야 했다. 컬러 팔레트가 `blue-500`처럼 값 자체를 이름에 담는 것과 같은 방식으로, **타이포 토큰도 px 값을 이름으로 쓴다.** `text-22`는 22px라는 뜻이고, 그 이상도 이하도 아니다.

### 지금 안 쓰는 13단계도 전부 등록해 둔다

지금 실제로 쓰는 크기는 7개(과거 Typography 1~7 자리, 즉 `text-30`/`text-26`/`text-22`/`text-20`/`text-17`/`text-15`/`text-13`)뿐이지만, `theme.css`에는 **20단계 전부** 등록돼 있다. 컬러 팔레트에서 지금 안 쓰는 5개 색상(pink·violet·indigo·cyan·lime)도 미리 등록해 둔 것과 같은 이유다 — 나중에 두 크기 사이의 값이 필요할 때, 값을 새로 만들지 않고 바로 골라 쓸 수 있게 하기 위해서다.

```css
@theme {
  /* Tailwind 기본 크기 스케일(text-sm, text-base 등)을 지운다.
     이유는 컬러 팔레트를 리셋한 것과 같다 — 이 스케일에 없는 크기를
     실수로 쓰면 조용히 Tailwind 기본값이 나오는 것을 막는다. */
  --text-*: initial;
  --text-30: 30px;   --text-30--line-height: 40px;
  --text-29: 29px;   --text-29--line-height: 38px;
  /* ...11까지 20단계 */
}
```

## 글자 굵기 — 별도 스케일을 만들지 않는다

TDS는 Light·Regular·Medium·Semibold·Bold 다섯 단계를 쓴다(문서에 숫자 매핑은 나와 있지 않다). 이 다섯 이름은 CSS 표준 `font-weight` 값과 다음처럼 대응한다 — 업계 관행이자 Tailwind의 기본 굵기 유틸리티 이름과도 그대로 일치한다.

| TDS 이름 | `font-weight` | Tailwind 유틸리티 |
|---|---|---|
| Light | 300 | `font-light` |
| Regular | 400 | `font-normal` |
| Medium | 500 | `font-medium` |
| Semibold | 600 | `font-semibold` |
| Bold | 700 | `font-bold` |

**Tailwind의 기본 `font-weight` 스케일은 리셋하지 않는다.** 컬러·크기와 달리 `font-weight`는 100~900 아홉 단계가 이미 CSS 표준값 그대로라 "정의 안 한 값을 썼을 때 조용히 다른 값이 나온다"는 문제 자체가 없다 — `font-bold`는 어디서 봐도 700이다.

실제로 이 폰트가 그 범위를 지원하는지도 확인했다.

```
/* node_modules/pretendard/dist/web/variable/pretendardvariable.css */
font-family: 'Pretendard Variable';
font-weight: 45 920;
```

`45~920`은 TDS의 다섯 단계(300~700)를 포함해 Thin(100)부터 Black(900)까지 표준 아홉 단계를 전부 지원한다는 뜻이다. `font-light`부터 `font-black`까지 어떤 Tailwind 굵기 유틸리티를 써도 실제로 다른 굵기가 렌더링된다.

## 사용 규칙

### 1. 리터럴 픽셀 값을 쓰지 않는다

컴포넌트 코드에 `style="font-size: 22px"`나 임의값(`text-[22px]`)을 쓰지 않는다. 항상 스케일의 토큰(`text-22`)을 통해서만 크기를 지정한다.

### 2. 크기와 행간은 항상 짝으로 움직인다

`text-22`를 쓰면 행간(`31px`)이 자동으로 따라온다. 크기만 바꾸고 행간을 별도로 챙기는 실수를 방지하기 위해 Tailwind v4의 `--text-{name}--line-height` 짝 문법을 그대로 쓴다.

### 3. Tailwind 기본 스케일이 남아 있던 자리는 전부 이 스케일로 옮긴다

shadcn-vue가 생성한 컴포넌트(Dialog·Table·Tabs·Alert·Card·Input)에는 원래 Tailwind 기본값 `text-sm`(14px)·`text-base`(16px)가 남아 있었다. 이 스케일에 정확히 대응하는 값(`text-14`·`text-16`)이 있으므로 전부 옮겼다 — 팔레트를 리셋하면서 `text-grey-600`처럼 정의 안 된 색을 쓰던 곳을 전수 확인했던 것과 같은 절차다.

## 다른 프로젝트에서 재사용하는 방법

1. 서체는 그 프로젝트가 이미 쓰고 있는 라이선스 문제 없는 폰트를 그대로 쓴다. TDS(또는 참고하는 원본 디자인 시스템)의 서체 지정은 무시한다.
2. 원본 디자인 시스템의 "주요 토큰 + 보조 토큰" 구조가 있다면, 이 프로젝트처럼 크기 순서로 합쳐 빈틈없는 하나의 스케일을 만들 수 있는지 확인한다. 합쳐지지 않으면(정수 간격이 아니거나 겹치는 값이 있으면) 원본 그대로 두 계열로 남겨도 된다.
3. 토큰 이름은 값 자체(px)로 짓는다 — 나중에 이 시스템을 처음 보는 사람이 표를 찾아보지 않아도 크기를 알 수 있게 한다.
4. 프레임워크가 제공하는 기본 크기 스케일은 리셋하고, 지금 안 쓰는 단계도 전부 정의해 둔다.
5. 굵기는 원본 디자인 시스템의 이름(Light/Regular/…)이 표준 CSS `font-weight` 값(100~900)과 자연스럽게 대응하는지 먼저 확인한다. 대응한다면 프레임워크의 기본 굵기 유틸리티를 그대로 쓰고 별도 스케일을 만들지 않는다 — 새로 만드는 건 이미 있는 표준을 다시 발명하는 것이다.
6. 실제로 쓰는 폰트 파일이 그 굵기 범위를 지원하는지 `@font-face`의 `font-weight` 선언(가변 폰트라면 `min max` 두 숫자)으로 확인한다.
