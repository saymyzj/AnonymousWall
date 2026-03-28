<template>
  <div class="starry-bg" aria-hidden="true">
    <div class="stars" ref="starsEl"></div>
    <div class="shooting-stars" ref="shootingEl"></div>
    <div class="nebula n1"></div>
    <div class="nebula n2"></div>
    <div class="nebula n3"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const starsEl = ref<HTMLElement>()
const shootingEl = ref<HTMLElement>()
let shootingInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  if (!starsEl.value) return
  starsEl.value.innerHTML = ''
  const count = 180
  const frag = document.createDocumentFragment()
  for (let i = 0; i < count; i++) {
    const star = document.createElement('div')
    star.className = 'starry-dot'
    const size = 0.8 + Math.random() * 2.4
    star.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      top: ${Math.random() * 100}%;
      left: ${Math.random() * 100}%;
      --duration: ${2 + Math.random() * 3}s;
      --delay: ${Math.random() * 4}s;
      --opacity: ${0.15 + Math.random() * 0.5};
    `
    frag.appendChild(star)
  }
  starsEl.value.appendChild(frag)

  function spawnShootingStar() {
    if (!shootingEl.value) return
    const star = document.createElement('div')
    star.className = 'shooting-dot'
    star.style.top = `${Math.random() * 50}%`
    star.style.left = `${Math.random() * 70}%`
    star.style.animationDuration = `${0.6 + Math.random() * 0.6}s`
    shootingEl.value.appendChild(star)
    setTimeout(() => star.remove(), 1400)
  }

  shootingInterval = setInterval(() => {
    if (Math.random() > 0.5) spawnShootingStar()
  }, 3000)

  // Spawn one immediately for visual feedback
  setTimeout(spawnShootingStar, 500)
})

onUnmounted(() => {
  if (shootingInterval) clearInterval(shootingInterval)
})
</script>

<style>
/* NOT scoped — dynamically created elements need global styles */
.starry-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.starry-bg .stars {
  position: absolute;
  inset: 0;
}

.starry-dot {
  position: absolute;
  background: var(--star-color, #fff);
  border-radius: 50%;
  opacity: var(--opacity, 0.35);
  box-shadow: 0 0 6px 1px var(--star-glow, rgba(255, 255, 255, 0.18));
  animation: twinkle var(--duration, 3s) ease-in-out infinite alternate;
  animation-delay: var(--delay, 0s);
}

.starry-bg .shooting-stars {
  position: absolute;
  inset: 0;
}

.shooting-dot {
  position: absolute;
  width: 2px;
  height: 2px;
  background: var(--star-color, #fff);
  border-radius: 50%;
  box-shadow:
    0 0 4px 1px var(--star-glow, rgba(255, 255, 255, 0.3)),
    -20px 0 12px 1px var(--star-glow, rgba(255, 255, 255, 0.15)),
    -40px 0 20px 0 transparent;
  animation: shooting-star 0.8s ease-out forwards;
}

.starry-bg .nebula {
  position: fixed;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
  animation: nebula-pulse 8s ease-in-out infinite;
}

.starry-bg .nebula.n1 {
  width: 500px;
  height: 500px;
  background: var(--nebula-1-color, rgba(124, 92, 252, 0.22));
  top: -12%;
  left: -2%;
  animation-delay: 0s;
}

.starry-bg .nebula.n2 {
  width: 400px;
  height: 400px;
  background: var(--nebula-2-color, rgba(255, 107, 157, 0.16));
  bottom: 8%;
  right: -8%;
  animation-delay: 2.5s;
}

.starry-bg .nebula.n3 {
  width: 350px;
  height: 350px;
  background: var(--nebula-3-color, rgba(6, 214, 160, 0.08));
  top: 46%;
  left: 60%;
  animation-delay: 5s;
}

@media (max-width: 768px) {
  .starry-bg .nebula {
    filter: blur(100px);
  }

  .starry-bg .nebula.n1 {
    width: 360px;
    height: 360px;
  }

  .starry-bg .nebula.n2 {
    width: 300px;
    height: 300px;
  }

  .starry-bg .nebula.n3 {
    width: 260px;
    height: 260px;
    left: 52%;
  }
}
</style>
