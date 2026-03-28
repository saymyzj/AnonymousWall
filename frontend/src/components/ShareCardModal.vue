<template>
  <div class="share-overlay" @click.self="$emit('close')">
    <div class="share-panel">
      <div class="share-header">
        <div>
          <h3>分享卡片</h3>
          <p>生成一张适合保存和转发的帖子图片。</p>
        </div>
        <button class="close-btn" type="button" @click="$emit('close')">✕</button>
      </div>

      <div class="canvas-wrap">
        <canvas ref="canvasEl" width="1080" height="1440"></canvas>
      </div>

      <div class="actions">
        <button class="ghost-pill" type="button" @click="downloadCard">保存图片</button>
        <button class="pill-button brand" type="button" @click="$emit('close')">完成</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'
import { formatTimeAgo, tagEmoji } from '../utils/presentation'

const props = defineProps<{ post: any }>()
defineEmits(['close'])

const canvasEl = ref<HTMLCanvasElement>()

const bubbleThemeMap: Record<number, { bg: [string, string]; accent: string }> = {
  1: { bg: ['#FFDCE8', '#FFF2F6'], accent: '#FF6B9D' },
  2: { bg: ['#FFE3CF', '#FFF2E0'], accent: '#FFA559' },
  3: { bg: ['#DDF7EE', '#F3FFFA'], accent: '#06D6A0' },
  4: { bg: ['#DDEEFF', '#EFF7FF'], accent: '#64B4FF' },
  5: { bg: ['#E7E0FF', '#F5F2FF'], accent: '#7C5CFC' },
  6: { bg: ['#FFF7CC', '#FFFBEA'], accent: '#D6A500' },
  7: { bg: ['#F4F4F7', '#FFFFFF'], accent: '#6B7280' },
  8: { bg: ['#F6E7DA', '#FFF6EE'], accent: '#B07C4D' },
}

async function drawCard() {
  await nextTick()
  const canvas = canvasEl.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const theme = bubbleThemeMap[props.post.bg_color || 5] || bubbleThemeMap[5]
  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
  gradient.addColorStop(0, theme.bg[0])
  gradient.addColorStop(1, theme.bg[1])

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.fillStyle = '#F6F5FB'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  ctx.fillStyle = 'rgba(124, 92, 252, 0.08)'
  ctx.beginPath()
  ctx.arc(180, 180, 220, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = 'rgba(255, 107, 157, 0.08)'
  ctx.beginPath()
  ctx.arc(860, 1140, 260, 0, Math.PI * 2)
  ctx.fill()

  const cardX = 96
  const cardY = 150
  const cardW = 888
  const cardH = 1040
  const radius = 42

  ctx.save()
  ctx.beginPath()
  ctx.moveTo(cardX + radius, cardY)
  ctx.arcTo(cardX + cardW, cardY, cardX + cardW, cardY + cardH, radius)
  ctx.arcTo(cardX + cardW, cardY + cardH, cardX, cardY + cardH, radius)
  ctx.arcTo(cardX, cardY + cardH, cardX, cardY, radius)
  ctx.arcTo(cardX, cardY, cardX + cardW, cardY, radius)
  ctx.closePath()
  ctx.clip()

  ctx.fillStyle = gradient
  ctx.fillRect(cardX, cardY, cardW, cardH)
  ctx.restore()

  ctx.strokeStyle = 'rgba(255,255,255,0.75)'
  ctx.lineWidth = 2
  roundRect(ctx, cardX, cardY, cardW, cardH, radius)
  ctx.stroke()

  ctx.fillStyle = 'rgba(255,255,255,0.75)'
  roundRect(ctx, cardX + 48, cardY + 54, 170, 54, 27, true)
  ctx.fillStyle = theme.accent
  ctx.font = '600 26px sans-serif'
  ctx.fillText(`${tagEmoji(props.post.tag)} ${props.post.tag}`, cardX + 76, cardY + 88)

  ctx.fillStyle = '#18152A'
  ctx.font = '700 28px sans-serif'
  ctx.fillText('匿名宇宙', cardX + 48, cardY + cardH - 92)

  ctx.fillStyle = '#6A6680'
  ctx.font = '400 24px sans-serif'
  ctx.fillText(formatTimeAgo(props.post.created_at), cardX + cardW - 220, cardY + cardH - 92)

  wrapText(ctx, props.post.content, cardX + 58, cardY + 180, cardW - 116, 60, 48, '#231F3A')
}

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number,
  fill = false,
) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.arcTo(x + width, y, x + width, y + height, radius)
  ctx.arcTo(x + width, y + height, x, y + height, radius)
  ctx.arcTo(x, y + height, x, y, radius)
  ctx.arcTo(x, y, x + width, y, radius)
  ctx.closePath()
  if (fill) ctx.fill()
}

function wrapText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  maxWidth: number,
  lineHeight: number,
  maxLines: number,
  color: string,
) {
  ctx.fillStyle = color
  ctx.font = '400 42px sans-serif'
  const chars = text.split('')
  let line = ''
  let lines = 0

  for (const char of chars) {
    const next = line + char
    if (ctx.measureText(next).width > maxWidth) {
      ctx.fillText(line, x, y + lines * lineHeight)
      line = char
      lines += 1
      if (lines >= maxLines - 1) break
    } else {
      line = next
    }
  }

  if (lines < maxLines) {
    const suffix = chars.length > line.length + lines ? '…查看全文' : ''
    ctx.fillText(line + suffix, x, y + lines * lineHeight)
  }
}

function downloadCard() {
  const canvas = canvasEl.value
  if (!canvas) return
  const link = document.createElement('a')
  link.download = `anonymouswall-post-${props.post.id}.png`
  link.href = canvas.toDataURL('image/png')
  link.click()
}

watch(() => props.post, drawCard, { deep: true })
onMounted(drawCard)
</script>

<style scoped>
.share-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  padding: 32px;
  background: rgba(8, 10, 20, 0.58);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.share-panel {
  width: min(760px, 100%);
  max-height: calc(100vh - 64px);
  overflow: auto;
  padding: 24px;
  border-radius: 28px;
  background: rgba(18, 21, 42, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.share-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.share-header h3 {
  margin: 0;
}

.share-header p {
  margin: 6px 0 0;
  color: var(--text-2);
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-1);
}

.canvas-wrap {
  border-radius: 20px;
  overflow: hidden;
}

.canvas-wrap canvas {
  width: 100%;
  height: auto;
  display: block;
  background: #fff;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 18px;
}
</style>
