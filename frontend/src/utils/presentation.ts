const TAG_EMOJI_MAP: Record<string, string> = {
  表白: '💌',
  吐槽: '😤',
  求助: '🆘',
  树洞: '🕳️',
  失物招领: '🔍',
  搭子: '🤝',
}

export function tagEmoji(tag?: string) {
  if (!tag) return ''
  return TAG_EMOJI_MAP[tag] || ''
}

export function formatTimeAgo(dateStr?: string) {
  if (!dateStr) return ''
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 2592000) return `${Math.floor(diff / 86400)} 天前`
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
  })
}

export function getIdentityInitial(nickname?: string) {
  if (!nickname) return '?'
  const cleaned = nickname.trim()
  return cleaned.charAt(cleaned.length > 2 ? 2 : 0) || cleaned.charAt(0) || '?'
}
