# 匿名宇宙 MVP 最小闭环 — TODO LIST

> 目标：从零搭建环境，实现核心功能闭环：用户注册登录 + 发帖/列表/详情 + 评论 + 点赞 + 敏感词审核 + Django Admin 后台
> 创建日期：2026-03-26

---

## 阶段 0：环境搭建与项目骨架

### 后端

- [x] 0-1. 创建 `backend/` 目录，初始化 Django 项目（`config` 为项目名），Python 3.12+
- [x] 0-2. 安装核心依赖：`django`, `djangorestframework`, `djangorestframework-simplejwt`, `django-cors-headers`, `psycopg2-binary`, `pillow`, `django-filter`
- [x] 0-3. 配置 settings 分环境：`config/settings/base.py`, `dev.py`, `prod.py`
- [x] 0-4. `base.py` 配置：`INSTALLED_APPS`（DRF、corsheaders）、REST_FRAMEWORK 默认认证/分页/异常处理、JWT 参数（7天过期）、CORS 允许前端开发域名
- [x] 0-5. `dev.py` 配置 PostgreSQL 连接（本地 Docker 或本机）、DEBUG=True
- [x] 0-6. 创建 `common/` 公共模块：统一分页类（`pagination.py`）、统一异常处理（`exceptions.py`）、统一响应格式 `{code, message, data}`
- [x] 0-7. 编写根路由 `config/urls.py`，挂载 `/api/` 前缀和 `/admin/`

### 前端

- [x] 0-8. 使用 `npm create vite@latest frontend -- --template vue-ts` 初始化前端项目
- [x] 0-9. 安装核心依赖：`vant`（移动端组件库）、`pinia`、`vue-router`、`axios`、`@vant/use`
- [x] 0-10. 配置 Vite：代理 `/api` 到后端 `localhost:8000`、自动导入 Vant 组件
- [x] 0-11. 搭建前端目录结构：`api/`、`components/`、`composables/`、`pages/`、`router/`、`stores/`、`styles/`
- [x] 0-12. 创建 `styles/variables.css`，写入 UI 设计文档中的 CSS 变量（亮/暗色两套）
- [x] 0-13. 创建 `styles/global.css`，设置全局样式：渐变背景、字体栈、基础 reset
- [x] 0-14. 创建 `api/index.ts`：Axios 实例封装，请求拦截器加 JWT Token，响应拦截器统一错误处理（401 跳登录）
- [x] 0-15. 创建 `router/index.ts`：定义路由占位（首页/登录/注册/帖子详情/发帖/个人中心），配置路由守卫（未登录重定向）
- [x] 0-16. 创建 `layouts/DefaultLayout.vue`：顶部导航栏骨架 + `<router-view>` + 悬浮发帖按钮

### 基础设施

- [x] 0-17. 编写 `docker-compose.dev.yml`：PostgreSQL 16 + Redis 7（MVP 阶段 Redis 可选，仅 PG 必须）
- [x] 0-18. 启动 Docker 容器，验证数据库连接
- [x] 0-19. 后端 `python manage.py migrate` 运行初始迁移，`createsuperuser` 创建管理员
- [x] 0-20. 前后端分别启动，验证前端能通过代理请求到后端 API（可用简单的 health check 接口验证）

---

## 阶段 1：用户体系（注册 / 登录 / 匿名身份）

### 后端 — `apps/users/`

- [x] 1-1. 创建 `users` app，定义 `User` 模型（扩展 `AbstractUser`），字段：`email`（唯一）、`is_banned`、`ban_until`，去掉 username 改用 email 登录
- [x] 1-2. 定义 `AnonymousIdentity` 模型，字段：`user`（FK）、`nickname`、`avatar_seed`（用于生成头像的哈希种子）、`created_at`
- [x] 1-3. 编写 `utils.py`：随机昵称生成函数（"匿名+动物名+#4位数字"）、avatar_seed 生成逻辑
- [x] 1-4. 注册 Serializer：邮箱+密码（强度校验8位含字母数字），注册成功后自动创建一个默认 `AnonymousIdentity`
- [x] 1-5. 注册 View：`POST /api/auth/register/`，返回用户信息（不含敏感字段）
- [x] 1-6. 登录 View：`POST /api/auth/login/`，使用 SimpleJWT 的 `TokenObtainPairView`，自定义返回 payload 包含 `user_id` 和默认匿名昵称
- [x] 1-7. Token 刷新 View：`POST /api/auth/token/refresh/`
- [x] 1-8. 个人信息 View：`GET /api/me/`，返回当前用户的匿名身份信息
- [x] 1-9. `admin.py`：注册 User 和 AnonymousIdentity 到 Django Admin，用户列表显示邮箱、注册时间、是否禁言

### 前端

- [x] 1-10. 创建 `stores/auth.ts`（Pinia）：管理 token 存储（localStorage）、用户信息、登录/登出 action
- [x] 1-11. 创建 `api/auth.ts`：封装注册、登录、刷新 token、获取个人信息接口
- [x] 1-12. 实现 `pages/Login.vue`：UI 参照 UI 设计 7.15（气泡背景动画 + 邮箱密码表单 + 登录按钮），含登录/注册 tab 切换
- [x] 1-13. 路由守卫完善：已登录用户访问登录页自动跳首页，未登录用户访问受保护页面跳登录页
- [x] 1-14. 导航栏右侧：未登录显示"登录"入口，已登录显示匿名头像

---

## 阶段 2：帖子系统（发帖 / 列表 / 详情）

### 后端 — `apps/posts/`

- [x] 2-1. 创建 `posts` app，定义 `Post` 模型，字段：`author`(FK User)、`identity`(FK AnonymousIdentity)、`content`(500字)、`tag`(choices: 表白/吐槽/求助/树洞/失物招领/搭子)、`bg_color`(预设8色编号)、`status`(normal/ai_suspect/pending/rejected)、`is_deleted`、`like_count`、`comment_count`、`favorite_count`、`created_at`、`updated_at`
- [x] 2-2. 帖子列表 Serializer：返回匿名昵称/头像种子、内容、标签、背景色、互动计数、发布时间（不返回真实 user_id）
- [x] 2-3. 帖子详情 Serializer：在列表基础上增加完整内容（列表可截断）、当前用户是否点赞/收藏状态
- [x] 2-4. 帖子列表 ViewSet：`GET /api/posts/`，支持分页（滚动加载分页）、标签筛选（`?tag=表白`）、排序（最新/最热）、时间筛选（today/week/month/all）
- [x] 2-5. 发帖 View：`POST /api/posts/`，需登录，内容长度校验、标签必选校验、背景色校验，自动关联用户默认匿名身份
- [x] 2-6. 帖子详情 View：`GET /api/posts/{id}/`，查看计数+1
- [x] 2-7. 删除帖子 View：`DELETE /api/posts/{id}/`，仅作者可操作，软删除
- [x] 2-8. `admin.py`：帖子管理——列表展示内容摘要/标签/状态/作者真实邮箱/互动数据，支持状态筛选、批量下架操作

### 前端

- [x] 2-9. 创建 `api/posts.ts`：封装帖子列表、详情、发帖、删除接口
- [x] 2-10. 创建 `stores/posts.ts`：帖子列表状态管理、当前筛选条件、分页光标
- [x] 2-11. 实现 `components/PostCard.vue`：参照 UI 设计 7.4——气泡卡片样式（渐变背景色、大圆角24px、匿名头像+昵称+时间、正文3行截断、标签胶囊、互动栏点赞/评论/收藏计数）
- [x] 2-12. 实现 `pages/Home.vue`：顶部导航栏 + 标签筛选栏（参照 UI 7.2，胶囊横向滚动） + 排序栏（最新/最热）+ 帖子卡片列表（单列移动端）+ 触底加载更多（Intersection Observer）+ 空状态
- [x] 2-13. 实现 `pages/CreatePost.vue`：参照 UI 7.13——文本输入区（500字限制计数器）+ 标签单选胶囊 + 背景色圆点选择器（8色）+ 发布按钮，发布成功后跳转首页
- [x] 2-14. 实现 `pages/PostDetail.vue`：展示帖子完整内容（背景色+匿名身份+全文+标签+互动栏）+ 评论区域（阶段3实现，先留占位）
- [x] 2-15. 实现响应式布局：移动端单列 / ≥768px 双列瀑布流 / ≥1024px 双列 max-960px 居中

---

## 阶段 3：评论系统

### 后端 — `apps/comments/`

- [x] 3-1. 创建 `comments` app，定义 `Comment` 模型，字段：`post`(FK)、`author`(FK User)、`identity`(FK AnonymousIdentity)、`parent`(FK self, nullable，支持回复)、`content`(200字)、`status`、`like_count`、`created_at`
- [x] 3-2. 实现帖子内匿名身份分配逻辑：同一帖子中同一用户使用固定标识（匿名A/B/C...），楼主标识为"楼主"。逻辑放在 Serializer 或 Service 层
- [x] 3-3. 评论列表 Serializer：返回匿名标识（A/B/C + 对应颜色）、楼主标识、内容、点赞数、回复的父评论信息
- [x] 3-4. 评论列表 View：`GET /api/posts/{id}/comments/`，按时间排序，分页，返回扁平列表（前端根据 parent_id 组装嵌套）
- [x] 3-5. 发表评论 View：`POST /api/posts/{id}/comments/`，需登录，支持 `parent_id` 回复某评论，发布后帖子 `comment_count` +1
- [x] 3-6. 删除评论 View：`DELETE /api/comments/{id}/`，仅作者可操作
- [x] 3-7. `admin.py`：评论管理——列表展示内容/关联帖子/状态/发布时间，支持批量下架

### 前端

- [x] 3-8. 创建 `api/comments.ts`：封装评论列表、发评论、删评论接口
- [x] 3-9. 实现 `components/CommentItem.vue`：参照 UI 7.9——匿名头像（小号28px）+ 匿名标识（带颜色）+ 楼主标签 + 评论内容 + 点赞/回复按钮 + 子评论缩进展示
- [x] 3-10. 在 `PostDetail.vue` 中集成评论区：评论列表 + 底部固定评论输入框（200字限制）+ 回复某条评论时显示"回复 匿名A"提示
- [x] 3-11. 评论发布成功后刷新评论列表，帖子评论计数同步更新

---

## 阶段 4：点赞功能

### 后端 — `apps/interactions/`

- [x] 4-1. 创建 `interactions` app，定义 `Like` 模型，字段：`user`(FK)、`target_type`(post/comment)、`target_id`(int)、`created_at`，联合唯一约束 `(user, target_type, target_id)`
- [x] 4-2. 帖子点赞/取消点赞 View：`POST /api/posts/{id}/like/`，toggle 逻辑——已赞则取消、未赞则点赞，同步更新帖子 `like_count`
- [x] 4-3. 评论点赞/取消点赞 View：`POST /api/comments/{id}/like/`，同理
- [x] 4-4. 帖子列表/详情 Serializer 增加 `is_liked` 字段（当前用户是否已点赞）

### 前端

- [x] 4-5. 帖子卡片和详情页的点赞按钮：空心♡/实心♥ 切换 + 计数变化 + 弹跳动画（参照 UI 8.3 动效）
- [x] 4-6. 评论项的点赞按钮：同理
- [x] 4-7. 乐观更新：点击后立即更新 UI 状态和计数，API 失败时回退

---

## 阶段 5：L1 敏感词审核

### 后端 — `apps/moderation/`

- [x] 5-1. 创建 `moderation` app，定义 `SensitiveWord` 模型，字段：`word`、`level`(hard/soft)、`created_at`
- [x] 5-2. 实现 DFA 敏感词过滤器（`services.py`）：基于 Trie 树构建 DFA 自动机，支持空格插入/符号替换等变体检测
- [x] 5-3. 应用启动时从数据库加载词库到内存（`AppConfig.ready()` 中初始化），管理后台修改词库时通过 Signal 触发重建
- [x] 5-4. 在发帖 View 中集成 L1 审核：提交时同步调用 DFA 过滤——命中硬拦截词返回 400 + 高亮违规词；命中软标记词放行但 status 标记为 `ai_suspect`
- [x] 5-5. 在发评论 View 中同样集成 L1 审核
- [x] 5-6. `admin.py`：敏感词管理——词库列表（支持搜索）、新增/编辑/删除、级别切换（硬拦截/软标记）、批量导入（TXT 上传）
- [x] 5-7. 初始化默认敏感词库：通过 data migration 或 management command 导入基础词库

### 前端

- [x] 5-8. 发帖/评论时处理 400 响应：展示敏感词提示 Toast，告知用户修改内容

---

## 阶段 6：管理后台完善（Django Admin）

- [x] 6-1. 安装 `django-simpleui` 美化 Admin 界面
- [x] 6-2. Admin 首页仪表盘：显示今日发帖数、今日评论数、待审核数（通过 SimpleUI 自定义首页或 Admin Index 模板覆盖）
- [x] 6-3. 帖子管理增强：增加"下架"/"恢复"自定义 Action，内容状态筛选侧栏，显示真实用户邮箱（仅管理员可见）
- [x] 6-4. 评论管理增强：增加"下架"自定义 Action
- [x] 6-5. 用户管理增强：禁言操作（自定义 Action：禁言7天/30天/永久），显示发帖数/违规次数
- [x] 6-6. 简易审核队列：帖子列表按 status 筛选 `pending`/`ai_suspect`，管理员可直接操作"通过/下架"
- [x] 6-7. 定义 `AuditLog` 模型：记录所有审核操作（审核人、时间、操作、原因），Admin 中可查看

---

## 阶段 7：联调、收尾与验收

- [x] 7-1. 前后端联调：注册 → 登录 → 发帖 → 列表展示 → 详情查看 → 发评论 → 点赞 → 敏感词拦截，完整流程走通
- [x] 7-2. 个人中心页面（简版）：`pages/Profile.vue`——展示匿名头像+昵称 + "我的发布"列表 + 登出按钮
- [x] 7-3. 错误边界处理：网络错误提示、token 过期自动跳登录、空状态展示
- [x] 7-4. 移动端体验打磨：安全区域适配（底部 safe-area）、滚动加载体验、输入法弹起时布局不错位
- [x] 7-5. 后端基础安全：CORS 白名单、SQL 注入防护（DRF 默认 ORM 即可）、XSS 防护（DRF 默认转义）
- [x] 7-6. 编写 `README.md`：项目简介、本地开发启动步骤、环境变量说明

---

## MVP 范围边界（以下不做）

| 功能 | MVP 策略 |
|------|---------|
| 图片上传 | 不做，后续迭代 |
| 投票/私信/通知 | 不做 |
| 收藏 | 不做（点赞先行验证互动链路） |
| AI 审核 (L2) | 不做，仅 L1 敏感词 |
| 推荐排序 | 不做，仅最新/最热 |
| 深色模式 | CSS 变量已预埋，不实现切换逻辑 |
| Redis 缓存 | 不做，直接查数据库 |
| Celery 异步 | 不做，敏感词审核同步执行即可 |
| Docker 部署 | 仅 `docker-compose.dev.yml` 跑数据库，前后端本地启动 |
