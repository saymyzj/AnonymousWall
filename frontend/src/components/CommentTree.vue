<template>
  <div class="comment-node">
    <CommentItem
      :comment="comment"
      @reply="$emit('reply', comment)"
      @like="$emit('like', comment.id)"
      @delete="$emit('delete', comment.id)"
      @report="$emit('report', comment)"
    />

    <div v-if="visibleChildren.length" class="children" :class="{ nested: depth < 2 }">
      <CommentTree
        v-for="child in visibleChildren"
        :key="child.id"
        :comment="child"
        :depth="Math.min(depth + 1, 2)"
        @reply="$emit('reply', $event)"
        @like="$emit('like', $event)"
        @delete="$emit('delete', $event)"
        @report="$emit('report', $event)"
      />
    </div>

    <button
      v-if="hasHiddenReplies"
      class="toggle-replies"
      type="button"
      @click="expanded = !expanded"
    >
      {{ expanded ? '收起回复' : `展开 ${hiddenReplyCount} 条回复` }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import CommentItem from './CommentItem.vue'

const props = withDefaults(
  defineProps<{
    comment: any
    depth?: number
  }>(),
  {
    depth: 0,
  },
)

defineEmits(['reply', 'like', 'delete', 'report'])

const expanded = ref(false)

const childComments = computed(() => props.comment.children || [])
const visibleChildren = computed(() => {
  if (expanded.value || childComments.value.length <= 2) {
    return childComments.value
  }
  return childComments.value.slice(0, 2)
})
const hiddenReplyCount = computed(() => childComments.value.length - 2)
const hasHiddenReplies = computed(() => childComments.value.length > 2)
</script>

<style scoped>
.children.nested {
  margin: 16px 0 0 50px;
  padding-left: 20px;
  border-left: 2px solid rgba(255, 255, 255, 0.06);
}

.toggle-replies {
  margin: 6px 0 0 50px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--brand);
  font-size: 0.8125rem;
}

.toggle-replies:hover {
  color: var(--pink);
}

@media (max-width: 599px) {
  .children.nested,
  .toggle-replies {
    margin-left: 20px;
  }
}
</style>
