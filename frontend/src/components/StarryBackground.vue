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
  starsEl.value.innerHTML = ''
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
      --duration: ${2 + Math.random() * 3}s;
      --delay: ${Math.random() * 3}s;
      --opacity: ${0.18 + Math.random() * 0.38};
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
  opacity: var(--opacity, 0.35);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.18);
  animation: twinkle var(--duration, 3s) ease-in-out infinite alternate;
  animation-delay: var(--delay, 0s);
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
  background: rgba(124, 92, 252, 0.22);
  top: -12%;
  left: -2%;
}

.nebula.n2 {
  width: 400px;
  height: 400px;
  background: rgba(255, 107, 157, 0.16);
  bottom: 8%;
  right: -8%;
}

.nebula.n3 {
  width: 350px;
  height: 350px;
  background: rgba(6, 214, 160, 0.08);
  top: 46%;
  left: 60%;
}

@media (max-width: 768px) {
  .nebula {
    filter: blur(100px);
  }

  .nebula.n1 {
    width: 360px;
    height: 360px;
  }

  .nebula.n2 {
    width: 300px;
    height: 300px;
  }

  .nebula.n3 {
    width: 260px;
    height: 260px;
    left: 52%;
  }
}
</style>
