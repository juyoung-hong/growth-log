<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/shared/lib/utils'

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes['class']
    /** default(기본) | sm — 목록처럼 조밀해야 하는 자리에 sm을 쓴다.
     * CardHeader/CardContent/CardFooter/CardTitle이 group-data-[size=sm]/card:
     * 선택자로 이 값을 읽어 padding·글자 크기를 줄인다. */
    size?: 'default' | 'sm'
  }>(),
  {
    class: undefined,
    size: 'default',
  },
)
</script>

<template>
  <!--
    그림자와 테두리를 쓰지 않는다.
    배경색 차이만으로 면을 구분하고 내부는 Border(Separator)로 나눈다.
    rounded-lg가 20px인 것은 theme의 --radius가 1.25rem이기 때문이다.

    overflow-hidden 때문에 CardHeader/CardFooter는 자기 모서리를 따로
    둥글릴 필요가 없다 — 여기서 한 번만 잘라내면 안쪽 내용은 이 모양
    그대로 잘린다. 예전엔 CardHeader/CardFooter가 각자 rounded-t-xl/
    rounded-b-xl(24px)을 갖고 있었는데, 여기 rounded-lg(20px)와 값이
    달라 죽은 코드였다 — 어차피 안 보였다. 지워서 헷갈릴 여지를 없앴다.
  -->
  <div
    data-slot="card"
    :data-size="size"
    :class="cn('group/card bg-secondary text-card-foreground flex flex-col overflow-hidden rounded-lg', props.class)"
  >
    <slot />
  </div>
</template>
