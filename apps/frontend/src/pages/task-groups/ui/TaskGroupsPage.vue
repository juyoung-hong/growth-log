<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ScopeSwitch } from '@/features/scope-switch'
import { parseScopeParam, toScope } from '@/shared/lib/scope'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card } from '@/shared/ui/card'
import { ConfirmDialog } from '@/shared/ui/confirm-dialog'
import { Input } from '@/shared/ui/input'
import { Progress } from '@/shared/ui/progress'
import { Separator } from '@/shared/ui/separator'

const route = useRoute()
const scopeParam = computed(() => parseScopeParam(route.query.scope))

// 아래는 Phase 3에서 실제 목록으로 교체된다. 지금은 TDS 적용 결과를
// 눈으로 확인하려고 프리미티브를 한 번씩 늘어놓은 것이다.
const confirmOpen = ref(false)
const deleted = ref(false)
</script>

<template>
  <section class="flex flex-col gap-5">
    <div class="flex items-center justify-between">
      <h1 class="text-22 font-bold">할일관리</h1>
      <Button size="medium">+ 새 프로젝트</Button>
    </div>

    <ScopeSwitch />

    <p class="text-15 text-grey-700">
      현재 분류: <strong class="text-foreground">{{ toScope(scopeParam) }}</strong>
      <span class="text-13 text-grey-700">(URL: {{ scopeParam }})</span>
    </p>

    <Separator variant="height16" />

    <!-- ── 여기부터 Phase 3에서 삭제 ── -->
    <Card class="p-5">
      <div class="flex items-center justify-between">
        <span class="text-17 font-semibold">메일서버 이중화 작업</span>
        <Badge color="blue">진행중</Badge>
      </div>
      <p class="text-15 text-grey-700 mt-1">기존 단일 메일서버를 이중화하여 장애 대응력 확보</p>
      <div class="mt-4 flex items-center gap-3">
        <Progress :model-value="70" />
        <span class="text-13 text-grey-700 shrink-0 tabular-nums">7/10 완료</span>
      </div>
      <Separator variant="full" class="my-4" />
      <div class="flex flex-wrap items-center gap-2">
        <Badge color="green">완료</Badge>
        <Badge color="yellow">보류</Badge>
        <Badge color="blue">회사</Badge>
        <Badge color="purple">개인</Badge>
      </div>
    </Card>

    <div class="flex flex-wrap items-end gap-2">
      <Button size="small">small 32</Button>
      <Button size="medium">medium 38</Button>
      <Button size="large">large 48</Button>
      <Button size="xlarge">xlarge 56</Button>
    </div>

    <div class="flex flex-wrap items-end gap-2">
      <Button>fill primary</Button>
      <Button color="danger">fill danger</Button>
      <Button color="light">fill light</Button>
      <Button color="dark">fill dark</Button>
      <Button variant="weak">weak primary</Button>
      <Button variant="weak" color="danger">weak danger</Button>
      <Button variant="weak" color="light">weak light</Button>
      <Button variant="weak" color="dark">weak dark</Button>
      <Button loading>loading</Button>
      <Button color="danger" @click="confirmOpen = true">삭제 확인창</Button>
    </div>

    <Input variant="box" placeholder="Input 확인용" class="max-w-xs" />

    <p v-if="deleted" class="text-15 text-destructive">확인창에서 삭제를 눌렀습니다.</p>

    <ConfirmDialog
      v-model:open="confirmOpen"
      title="정말 삭제할까요?"
      description="삭제하면 되돌릴 수 없습니다."
      confirm-text="삭제"
      danger
      @confirm="deleted = true; confirmOpen = false"
    />
    <!-- ── 여기까지 Phase 3에서 삭제 ── -->
  </section>
</template>