# AnonymousWall MVP Bug 修复方案

> 基于 "2026-03-26 BUGs.md" 中记录的 4 个问题，逐一分析并给出完整修复方案。
> 创建日期：2026-03-26

---

## Bug 1：实名部分 — 注册需增加学号/工号验证

### 问题描述

当前注册只收集邮箱和密码，缺少学号/工号等实名信息。未校验真实性的用户应仅能浏览，不能发帖/评论/点赞。

### 根因分析

- **后端** `User` 模型（`backend/apps/users/models.py`）仅有 `email`、`is_banned`、`ban_until` 字段，缺少学号/工号字段及审核状态字段。
- **后端** `RegisterSerializer`（`backend/apps/users/serializers.py`）仅校验 `email` + `password`。
- **前端** `Login.vue` 注册表单仅有邮箱和密码两个输入框。
- **权限控制**：发帖/评论/点赞的 View 仅检查 `IsAuthenticated`，未检查用户是否已通过实名审核。

### 修复方案

#### 后端

- [x] **1-1. User 模型增加字段**（`backend/apps/users/models.py`）
  ```python
  # 新增字段
  student_id = models.CharField('学号/工号', max_length=30, blank=True, default='')
  real_name = models.CharField('真实姓名', max_length=50, blank=True, default='')
  is_verified = models.BooleanField('是否已验证', default=False)
  ```
  - `student_id`：用户提交的学号或工号
  - `real_name`：真实姓名（配合学号做人工审核）
  - `is_verified`：管理员审核通过后设为 `True`
  - 运行 `python manage.py makemigrations users && python manage.py migrate`

- [x] **1-2. 注册 Serializer 增加字段**（`backend/apps/users/serializers.py`）
  ```python
  class RegisterSerializer(serializers.Serializer):
      email = serializers.EmailField()
      password = serializers.CharField(write_only=True, min_length=8)
      student_id = serializers.CharField(max_length=30)
      real_name = serializers.CharField(max_length=50)
  ```
  - `student_id` 和 `real_name` 为必填
  - `validate_student_id`：校验格式（仅允许字母和数字）、校验唯一性（同一学号不可重复注册）
  - `create` 方法中将 `student_id` 和 `real_name` 写入 User

- [x] **1-3. 自定义权限类**（新建 `backend/common/permissions.py`）
  ```python
  from rest_framework.permissions import BasePermission

  class IsVerifiedUser(BasePermission):
      """仅允许已通过实名验证的用户"""
      message = '您的账号尚未通过验证，暂时只能浏览内容'

      def has_permission(self, request, view):
          return (
              request.user
              and request.user.is_authenticated
              and request.user.is_verified
          )
  ```

- [x] **1-4. 替换发帖/评论/点赞 View 的权限**
  - `backend/apps/posts/views.py` 的 `create_post`、`delete_post`：`IsAuthenticated` → `IsVerifiedUser`
  - `backend/apps/comments/views.py` 的 `create_comment`、`delete_comment`：`IsAuthenticated` → `IsVerifiedUser`
  - `backend/apps/interactions/views.py` 的点赞 View：`IsAuthenticated` → `IsVerifiedUser`
  - 注意：帖子列表 `post_list` 和详情 `post_detail` 保持 `AllowAny`，未验证用户可浏览

- [x] **1-5. 用户信息接口返回验证状态**
  - `UserInfoSerializer` 的 `fields` 增加 `is_verified`、`student_id`
  - 前端可据此判断是否展示操作按钮

- [x] **1-6. Admin 后台增加审核操作**（`backend/apps/users/admin.py`）
  - 用户列表增加 `student_id`、`real_name`、`is_verified` 列
  - 增加自定义 Action："通过验证"（批量设置 `is_verified=True`）
  - 增加筛选器：按 `is_verified` 筛选待审核用户

#### 前端

- [x] **1-7. 注册表单增加字段**（`frontend/src/pages/Login.vue`）
  - 注册模式下显示额外输入框：`学号/工号`（必填）、`真实姓名`（必填）
  - 登录模式下仍然只需邮箱和密码
  - 提交注册时将 `student_id` 和 `real_name` 一并发送

- [x] **1-8. auth store 和 API 适配**（`frontend/src/stores/auth.ts`、`frontend/src/api/auth.ts`）
  - `register()` 方法增加 `student_id`、`real_name` 参数
  - `userInfo` 中存储 `is_verified` 状态

- [x] **1-9. 未验证用户的 UI 限制**
  - 全局判断 `authStore.isVerified`：
    - 未验证用户：隐藏发帖 FAB 按钮，帖子详情隐藏评论输入框，点赞按钮点击时 Toast 提示"账号审核中，暂时只能浏览"
    - 已验证用户：正常交互
  - 注册成功后跳转首页，显示提示："注册成功！账号审核中，审核通过后即可发帖评论"

---

## Bug 2：评论部分 — 评论树回复归属错误

### 问题描述

当匿名D回复评论2（评论1的子评论）时，回复应该出现在评论1的评论树下，但实际出现在评论4的评论树下。

### 根因分析

- **前端** `PostDetail.vue` 中评论是以**扁平列表** `v-for="c in comments"` 渲染的，按 `created_at` 时间顺序排列
- 后端返回的也是扁平列表，每条评论有 `parent` 字段（父评论 ID）和 `parent_label`（父评论者标识）
- 前端**没有将扁平列表组装成树结构**，所有评论包括回复都按时间顺序平铺
- 因此新回复（匿名D回复评论2）按时间排在最后，紧跟在评论4后面，而不是嵌套在评论1的树下
- `CommentItem.vue` 只是通过 `is-reply` CSS class 给有 `parent` 的评论加了缩进，但位置仍然在时间序列中

### 修复方案

#### 前端（核心修复）

- [x] **2-1. PostDetail.vue 中增加评论树构建逻辑**

  将后端返回的扁平评论列表组装为树结构，然后按树的顺序渲染：

  ```typescript
  interface CommentNode {
    // ...原有评论字段
    children: CommentNode[]
  }

  function buildCommentTree(flatComments: any[]): CommentNode[] {
    const map = new Map<number, CommentNode>()
    const roots: CommentNode[] = []

    // 第一遍：创建映射
    for (const c of flatComments) {
      map.set(c.id, { ...c, children: [] })
    }

    // 第二遍：建立父子关系
    for (const c of flatComments) {
      const node = map.get(c.id)!
      if (c.parent) {
        const parentNode = map.get(c.parent)
        if (parentNode) {
          parentNode.children.push(node)
        } else {
          // 父评论不在当前列表中（可能被删除），作为顶层评论
          roots.push(node)
        }
      } else {
        roots.push(node)
      }
    }

    return roots
  }
  ```

- [x] **2-2. 修改评论列表渲染为递归组件**

  将 `PostDetail.vue` 的评论列表改为递归渲染树结构：

  ```vue
  <template v-for="c in commentTree" :key="c.id">
    <CommentItem :comment="c" @reply="startReply(c)" ... />
    <!-- 子评论递归，限制嵌套深度为 2 层 -->
    <div v-if="c.children.length > 0" class="replies-group">
      <template v-for="reply in c.children" :key="reply.id">
        <CommentItem :comment="reply" @reply="startReply(reply)" ... />
        <!-- 第三层及以后不再缩进，但仍保持树结构 -->
        <template v-for="subReply in reply.children" :key="subReply.id">
          <CommentItem :comment="subReply" @reply="startReply(subReply)" ... />
        </template>
      </template>
    </div>
  </template>
  ```

  或者更简洁地，将 `CommentItem` 改造为递归组件，接收 `children` 并自行渲染子评论。

- [x] **2-3. 修改 CommentItem.vue 支持嵌套渲染**

  方案一（推荐）：创建 `CommentTree.vue` 递归组件：

  ```vue
  <!-- CommentTree.vue -->
  <template>
    <div class="comment-node" :class="{ 'is-nested': depth > 0 }">
      <CommentItem
        :comment="comment"
        @reply="$emit('reply', comment)"
        @like="$emit('like', comment.id)"
        @delete="$emit('delete', comment.id)"
      />
      <div v-if="comment.children?.length" class="children-group" :style="{ marginLeft: depth < 2 ? '40px' : '0' }">
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
  ```
  - 嵌套深度限制：最多缩进 2 层（`depth < 2`），超过 2 层不再缩进但仍在父评论树下
  - `CommentItem.vue` 本身不再处理 `is-reply` 样式，由 `CommentTree.vue` 控制缩进

- [x] **2-4. 后端确保返回完整评论列表**

  当前分页可能导致评论树不完整（父评论在第 1 页，子评论在第 2 页）。有两种策略：

  - **方案A（推荐，适合 MVP 评论量不大时）**：评论不分页或加大分页 size（如每页 100 条），一次性返回所有评论
  - **方案B（评论量大时）**：后端改为返回树形结构，仅顶层评论分页，每条顶层评论携带其所有子评论

  MVP 阶段建议用方案A，修改 `comment_list` View 的分页 size：
  ```python
  # 在 comment_list view 中使用更大的分页或不分页
  paginator = StandardPagination()
  paginator.page_size = 200  # 或直接不使用分页
  ```

- [x] **2-5. CommentItem.vue 移除 is-reply 相关样式**

  由于缩进逻辑由外层 `CommentTree.vue` 控制，`CommentItem.vue` 中的 `.is-reply` class 和对应样式应移除，改为纯展示组件。

---

## Bug 3：UI 部分 — 界面未按"气泡宇宙"风格实现

### 问题描述

帖子卡片是固定大小的矩形排列在规则网格中，而设计要求是"气泡宇宙"风格：不等高瀑布流、内容自适应大小、非对称排列、气泡有呼吸感。

### 根因分析

- `Home.vue` 的 `.post-list` 使用 `flex-direction: column`（移动端）和 `grid-template-columns: repeat(2, 1fr)`（桌面端），这是标准等高网格布局
- `PostCard.vue` 的 `.card-content` 使用了 `-webkit-line-clamp: 3` 固定截断 3 行，导致所有卡片高度一致
- 缺少 CSS masonry 或 JS 瀑布流布局实现
- 缺少卡片加载动画（气泡淡入上浮）
- 缺少视差浮动效果

### 修复方案

#### 前端 — Home.vue 布局修复

- [x] **3-1. 实现瀑布流布局**

  移动端（< 768px）保持单列，但卡片高度自适应（不截断）：

  桌面端（≥ 768px）使用 CSS `column` 实现瀑布流：
  ```css
  @media (min-width: 768px) {
    .post-list {
      column-count: 2;
      column-gap: 16px;
    }
    .post-list .post-card-wrapper {
      break-inside: avoid;
      margin-bottom: 12px;
    }
  }
  ```

  如果 CSS column 有兼容性或顺序问题，可改用 JS 双列分配方案：
  ```typescript
  // 将 posts 分为左右两列，按高度均衡分配
  const leftColumn = computed(() => postsStore.posts.filter((_, i) => i % 2 === 0))
  const rightColumn = computed(() => postsStore.posts.filter((_, i) => i % 2 === 1))
  ```
  ```html
  <div class="masonry">
    <div class="masonry-col">
      <PostCard v-for="p in leftColumn" :key="p.id" :post="p" />
    </div>
    <div class="masonry-col">
      <PostCard v-for="p in rightColumn" :key="p.id" :post="p" />
    </div>
  </div>
  ```

- [x] **3-2. PostCard.vue 移除固定行截断，改为内容自适应**

  当前 `.card-content` 的 `-webkit-line-clamp: 3` 使所有卡片等高。修改为：
  - 短文本（≤ 50 字）：不截断，卡片自然小（小气泡）
  - 中等文本（51-150 字）：显示前 5 行，超出截断
  - 长文本（> 150 字）：显示前 5 行，超出截断（大气泡）

  ```css
  .card-content {
    font-size: 15px;
    line-height: 24px;
    /* 不强制截断，让内容自然撑开 */
    word-break: break-word;
    white-space: pre-wrap;
  }

  .card-content.clamp {
    display: -webkit-box;
    -webkit-line-clamp: 5;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  ```

  ```vue
  <p class="card-content" :class="{ clamp: post.content.length > 100 }">
    {{ post.content }}
  </p>
  ```

#### 前端 — PostCard.vue 气泡样式增强

- [x] **3-3. 卡片加载动画（气泡淡入浮上）**

  参照 UI 设计 8.3，卡片从下方淡入浮上：
  ```css
  @keyframes bubble-in {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .post-card {
    animation: bubble-in 0.3s ease-out both;
  }

  /* 逐个延迟 */
  .post-card:nth-child(1) { animation-delay: 0ms; }
  .post-card:nth-child(2) { animation-delay: 50ms; }
  .post-card:nth-child(3) { animation-delay: 100ms; }
  .post-card:nth-child(4) { animation-delay: 150ms; }
  .post-card:nth-child(5) { animation-delay: 200ms; }
  .post-card:nth-child(6) { animation-delay: 250ms; }
  ```

- [x] **3-4. 点赞动效增强**

  参照 UI 设计 8.3，点赞时心形弹跳：
  ```css
  @keyframes like-bounce {
    0% { transform: scale(1); }
    30% { transform: scale(1.4); }
    60% { transform: scale(0.9); }
    100% { transform: scale(1); }
  }

  .action-btn.active span:first-child {
    animation: like-bounce 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  ```

- [x] **3-5. 标签选中弹性动效**

  参照 UI 设计 7.2，标签选中时弹性放大：
  ```css
  .tag-btn.active {
    animation: tag-bounce 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  @keyframes tag-bounce {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
  }
  ```

#### 前端 — DefaultLayout.vue 导航栏修复

- [x] **3-6. 导航栏增加搜索图标和通知图标**

  参照 UI 设计 7.1，导航栏右侧应有：搜索图标 + 通知铃铛 + 用户头像。
  当前只有用户头像/登录按钮，需增加搜索和通知图标：
  ```html
  <div class="nav-right">
    <button class="nav-icon" @click="toggleSearch">🔍</button>
    <router-link to="/notifications" class="nav-icon">
      🔔<span v-if="unreadCount" class="badge">{{ unreadCount }}</span>
    </router-link>
    <!-- 用户头像/登录 -->
  </div>
  ```
  注意：通知功能不在 MVP 范围，图标可先占位不跳转。搜索功能见 Bug 4。

- [x] **3-7. Logo 增加气泡 emoji 前缀**

  参照 UI 设计 7.1，Logo 应带气泡 emoji：
  ```html
  <router-link to="/" class="logo">🫧 AnonymousWall</router-link>
  ```

- [x] **3-8. FAB 按钮滚动隐藏/显示**

  参照 UI 设计 7.7，向下滚动时隐藏 FAB，向上滚动时显示：
  ```typescript
  // 在 DefaultLayout.vue 中
  const showFab = ref(true)
  let lastScrollY = 0

  function onScroll() {
    const currentY = window.scrollY
    showFab.value = currentY < lastScrollY || currentY < 100
    lastScrollY = currentY
  }

  onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
  onUnmounted(() => window.removeEventListener('scroll', onScroll))
  ```
  ```html
  <button v-if="authStore.isLoggedIn" class="fab" :class="{ hidden: !showFab }" @click="...">+</button>
  ```
  ```css
  .fab { transition: transform 0.3s, opacity 0.3s; }
  .fab.hidden { transform: translateY(80px); opacity: 0; pointer-events: none; }
  ```

#### 前端 — 全局样式补充

- [x] **3-9. variables.css 中补充缺失的 CSS 变量**

  参照 UI 设计 2.4，检查并补充缺失的变量定义。当前缺少 `--shadow-sm` 等变量在深色模式下的覆盖值（深色模式下阴影应替换为边框），以及缓动函数变量等。

- [x] **3-10. global.css 补充深色模式下气泡渐变色**

  参照 UI 设计 2.2，深色模式下降低饱和度 30%、亮度 20%：
  ```css
  [data-theme="dark"] .bubble-1 { background: linear-gradient(135deg, #B39EA6, #B38995); }
  /* ...其余 7 种颜色 */
  ```

#### 其他页面对照 UI 设计检查

- [x] **3-11. 帖子详情页对照 UI 设计 7.9 检查评论区样式**
  - 评论容器背景使用 `var(--card-bg)`，圆角 20px ✅（已实现）
  - 匿名标识颜色池对照 UI 设计 7.9 的 8 种颜色 ✅（serializer 中已实现）

- [x] **3-12. 发帖页对照 UI 设计 7.13 检查**
  - 背景色选择器：8 个色彩圆点应有选中双圈效果
  - 标签选择器：胶囊形单选

- [x] **3-13. 个人中心页对照 UI 设计 7.14 检查**
  - 顶部用户区居中、大头像（72px）
  - 数据统计三等分卡片
  - 菜单列表圆角卡片包裹

- [x] **3-14. 隐藏滚动条**
  当前 `global.css` 已有 `::-webkit-scrollbar { display: none; }`，但标签栏等横向滚动区域需要额外确认 Firefox 兼容：
  ```css
  .tag-bar {
    scrollbar-width: none; /* Firefox */
  }
  ```

---

## Bug 4：搜索功能 — 完全缺失

### 问题描述

没有任何帖子搜索功能，无法通过关键词查找相关帖子。

### 根因分析

- 后端 `post_list` View 没有关键词搜索参数
- 前端没有搜索 UI 组件
- 导航栏没有搜索入口

### 修复方案

#### 后端

- [x] **4-1. post_list View 增加关键词搜索**（`backend/apps/posts/views.py`）

  在 `post_list` 函数中增加 `search` 查询参数：
  ```python
  # Keyword search
  search = request.query_params.get('search', '').strip()
  if search:
      queryset = queryset.filter(content__icontains=search)
  ```
  - 使用 Django ORM 的 `icontains` 进行大小写不敏感的模糊匹配
  - MVP 阶段不需要全文搜索引擎，`icontains` 对 SQLite 和 PostgreSQL 均可用
  - 后续可升级为 PostgreSQL 的 `SearchVector` 全文搜索

#### 前端

- [x] **4-2. 导航栏搜索交互**（`frontend/src/layouts/DefaultLayout.vue`）

  参照 UI 设计 7.1 和 7.8：
  - 导航栏右侧增加搜索图标（🔍）
  - 点击搜索图标后，导航栏展开为全宽搜索框（动画 300ms ease-out）
  - 搜索框样式参照 UI 设计 7.8：圆角 16px，高度 44px，背景 `var(--card-bg)`
  - 输入关键词后按回车或点搜索图标执行搜索
  - 搜索框左侧有搜索图标，右侧有关闭按钮

  ```html
  <!-- 导航栏搜索模式 -->
  <nav class="navbar" :class="{ 'search-mode': isSearching }">
    <template v-if="isSearching">
      <div class="search-bar">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          ref="searchInput"
          placeholder="搜索匿名心声..."
          @keyup.enter="doSearch"
        />
        <button @click="closeSearch">×</button>
      </div>
    </template>
    <template v-else>
      <!-- 正常导航栏 -->
    </template>
  </nav>
  ```

- [x] **4-3. Posts Store 增加搜索支持**（`frontend/src/stores/posts.ts`）

  在 `filters` 中增加 `search` 字段：
  ```typescript
  filters: {
    tag: undefined,
    sort: 'latest',
    time: undefined,
    search: '',  // 新增
  }
  ```

  `fetchPosts` 方法将 `search` 参数传给后端 API：
  ```typescript
  const params: any = { page: this.page }
  if (this.filters.search) params.search = this.filters.search
  // ...其余 filter 参数
  ```

- [x] **4-4. 搜索结果页面**

  两种方案选一：

  - **方案A（推荐，简单）**：搜索直接复用 Home.vue，通过 URL query 参数传递搜索词（如 `/?search=关键词`），Home.vue 的 postsStore 读取 URL 参数并发起搜索请求
  - **方案B**：创建独立的 `Search.vue` 页面

  推荐方案A，修改 Home.vue：
  ```typescript
  // 在 onMounted 中
  const searchQuery = route.query.search as string
  if (searchQuery) {
    postsStore.setFilter('search', searchQuery)
  }
  ```

  搜索时导航栏组件通过 `router.push({ path: '/', query: { search: keyword } })` 跳转

- [x] **4-5. 搜索关键词高亮（可选增强）**

  参照功能设计 7.2，搜索结果中关键词高亮显示。在 `PostCard.vue` 中：
  ```typescript
  function highlightSearch(text: string, keyword: string) {
    if (!keyword) return text
    const regex = new RegExp(`(${keyword})`, 'gi')
    return text.replace(regex, '<mark>$1</mark>')
  }
  ```
  ```html
  <p class="card-content" v-html="highlightSearch(post.content, searchKeyword)"></p>
  ```
  注意：使用 `v-html` 时需对 `keyword` 做转义以防 XSS。

---

## 修复优先级与执行顺序

| 优先级 | Bug | 预估工作量 | 说明 |
|--------|-----|-----------|------|
| P0 | Bug 2 - 评论树 | 中 | 核心功能 Bug，影响评论体验 |
| P0 | Bug 4 - 搜索 | 中 | 基础功能缺失 |
| P1 | Bug 1 - 实名验证 | 大 | 涉及数据库迁移、前后端改动 |
| P1 | Bug 3 - UI 风格 | 大 | 涉及多个页面、布局重构 |

建议执行顺序：Bug 2 → Bug 4 → Bug 1 → Bug 3

- Bug 2 和 Bug 4 相对独立，改动范围小，可快速修复
- Bug 1 涉及数据库变更，需要谨慎处理迁移和已有数据
- Bug 3 工作量最大，建议逐个页面/组件迭代修复
