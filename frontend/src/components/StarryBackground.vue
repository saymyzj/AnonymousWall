<template>
  <div class="starry-bg" aria-hidden="true">
    <div class="stars" ref="starsEl"></div>
    <div class="nebula n1"></div>
    <div class="nebula n2"></div>
    <div class="nebula n3"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const starsEl = ref<HTMLElement>()

onMounted(() => {
  if (!starsEl.value) return
  const count = 120
  const frag = document.createDocumentFragment()
  for (let i = 0; i < count; i++) {
    const star = document.createElement('div')
    star.className = 'star'
    const size = 1 + Math.random() * 2
    star.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      top: ${Math.random() * 100}%;
      left: ${Math.random() * 100}%;
      --d: ${2 + Math.random() * 3}s;
      animation-delay: ${Math.random() * 3}s;
    `
    frag.appendChild(star)
  }
  starsEl.value.appendChild(frag)
})
</script>

<style scoped>
.starry-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.stars {
  position: absolute;
  inset: 0;
}

.star {
  position: absolute;
  background: #fff;
  border-radius: 50%;
  animation: twinkle var(--d, 3s) ease-in-out infinite alternate;
}

.nebula {
  position: fixed;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
}

.nebula.n1 {
  width: 500px;
  height: 500px;
  background: rgba(124, 92, 252, 0.2);
  top: -10%;
  left: -5%;
}

.nebula.n2 {
  width: 400px;
  height: 400px;
  background: rgba(255, 107, 157, 0.15);
  bottom: 10%;
  right: -8%;
}

.nebula.n3 {
  width: 350px;
  height: 350px;
  background: rgba(6, 214, 160, 0.08);
  top: 50%;
  left: 60%;
}
</style>
