<template>
  <component
    :is="as"
    class="glass-card"
    :class="{
      interactive,
      muted,
      bordered,
    }"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  as?: string
  interactive?: boolean
  muted?: boolean
  bordered?: boolean
}>(), {
  as: 'div',
  interactive: false,
  muted: false,
  bordered: true,
})
</script>

<style scoped>
.glass-card {
  background: var(--glass-bg);
  border: 1px solid transparent;
  border-color: transparent;
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(18px) saturate(1.25);
  -webkit-backdrop-filter: blur(18px) saturate(1.25);
}

.glass-card.bordered {
  border-color: var(--glass-border);
}

.glass-card.muted {
  background: var(--glass-bg-muted);
}

.glass-card.interactive {
  transition:
    transform 0.28s ease,
    box-shadow 0.28s ease,
    border-color 0.28s ease,
    background 0.28s ease;
}

.glass-card.interactive:hover {
  transform: translateY(-2px);
  border-color: var(--glass-border-strong);
  box-shadow: var(--shadow-floating);
}
</style>
