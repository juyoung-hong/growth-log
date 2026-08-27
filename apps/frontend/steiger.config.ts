import fsd from '@feature-sliced/steiger-plugin'
import { defineConfig } from 'steiger'

export default defineConfig([
  ...fsd.configs.recommended,
  {
    // shared는 성격상 파일이 잘게 쪼개져서 공개 API 규칙을 강제하지 않는다
    files: ['./src/shared/**'],
    rules: { 'fsd/public-api': 'off' },
  },
])