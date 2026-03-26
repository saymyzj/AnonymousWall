<template>
  <div class="comment-node">
    <CommentItem
      :comment="comment"
      @reply="$emit('reply', comment)"
      @like="$emit('like', comment.id)"
      @delete="$emit('delete', comment.id)"
    />
    <div v-if="comment.children?.length" class="children-group" :class="{ nested: depth < 2 }">
      <CommentTree
        v-for="child in comment.children"
        :key="child.id"
        :comment="child"
        :depth="Math.min(depth + 1, 2)"
        @reply="$emit('reply', $event)"
        @like="$emit('like', $event)"
        @delete="$emit('delete', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import CommentItem from './CommentItem.vue'

withDefaults(defineProps<{ comment: any; depth?: number }>(), {
  depth: 0,
})

defineEmits(['reply', 'like', 'delete'])
</script>

<style scoped>
.children-group.nested {
  margin-left: 20px;
  padding-left: 12px;
  border-left: 2px solid var(--divider);
}
</style>
