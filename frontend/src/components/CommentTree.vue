<template>
  <div class="comment-node">
    <CommentItem
      :comment="comment"
      @reply="$emit('reply', comment)"
      @like="$emit('like', comment.id)"
      @delete="$emit('delete', comment.id)"
      @report="$emit('report', comment)"
    />

    <CommentComposer
      v-if="replyTargetId === comment.id"
      :model-value="commentText"
      :avatar-text="myAvatarText"
      :submitting="commentSubmitting"
      :reply-label="replyLabel"
      :autofocus="true"
      :inline="true"
      @update:model-value="$emit('update:commentText', $event)"
      @cancel-reply="$emit('cancel-reply')"
      @blur-exit="$emit('blur-exit-reply')"
      @submit="$emit('submit-reply')"
    />

    <div v-if="visibleChildren.length" class="children" :class="{ nested: depth < 2 }">
      <CommentTree
        v-for="child in visibleChildren"
        :key="child.id"
        :comment="child"
        :depth="Math.min(depth + 1, 2)"
        :reply-target-id="replyTargetId"
        :comment-text="commentText"
        :comment-submitting="commentSubmitting"
        :my-avatar-text="myAvatarText"
        :reply-label="replyLabel"
        @reply="$emit('reply', $event)"
        @like="$emit('like', $event)"
        @delete="$emit('delete', $event)"
        @report="$emit('report', $event)"
        @update:comment-text="$emit('update:commentText', $event)"
        @cancel-reply="$emit('cancel-reply')"
        @blur-exit-reply="$emit('blur-exit-reply')"
        @submit-reply="$emit('submit-reply')"
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
import CommentComposer from './CommentComposer.vue'
import CommentItem from './CommentItem.vue'

const props = withDefaults(
  defineProps<{
    comment: any
    depth?: number
    replyTargetId?: number | null
    commentText?: string
    commentSubmitting?: boolean
    myAvatarText?: string
    replyLabel?: string
  }>(),
  {
    depth: 0,
    replyTargetId: null,
    commentText: '',
    commentSubmitting: false,
    myAvatarText: '匿',
    replyLabel: '',
  },
)

defineEmits(['reply', 'like', 'delete', 'report', 'update:commentText', 'cancel-reply', 'blur-exit-reply', 'submit-reply'])

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
  margin: 12px 0 0 50px;
  padding-left: 20px;
  border-left: 2px solid var(--brand);
  border-image: linear-gradient(180deg, var(--brand), var(--pink)) 1;
}

.toggle-replies {
  margin: 8px 0 0 50px;
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  background: var(--bg-card);
  color: var(--brand);
  font-size: 0.8125rem;
  transition: background 0.2s, transform 0.2s;
}

.toggle-replies:hover {
  background: var(--bg-card-hover);
  color: var(--pink);
  transform: translateY(-1px);
}

@media (max-width: 599px) {
  .children.nested,
  .toggle-replies {
    margin-left: 20px;
  }
}
</style>
