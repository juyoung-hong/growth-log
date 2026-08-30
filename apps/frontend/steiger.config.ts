import fsd from '@feature-sliced/steiger-plugin'
import { defineConfig } from 'steiger'

export default defineConfig([
  ...fsd.configs.recommended,
  {
    // shared는 성격상 파일이 잘게 쪼개져서 공개 API 규칙을 강제하지 않는다
    files: ['./src/shared/**'],
    rules: { 'fsd/public-api': 'off' },
  },
  {
    // 슬라이스를 하나씩 늘려가는 중이라 "참조가 하나뿐이면 합쳐라"는
    // 조언이 매 단계 걸린다. 로드맵상 뒤 단계에서 소비자가 늘어나는 것이
    // 예정돼 있어(예: entities/storage는 Phase 10의 저장공간 화면이
    // 다시 쓴다) 지금 합치면 나중에 도로 쪼개야 한다.
    rules: { 'fsd/insignificant-slice': 'off' },
  },
])