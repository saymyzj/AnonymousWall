# AnonymousWall UI 重构 TODO LIST

> 基于「03-27 UI设计终稿.md」Galaxy 深色宇宙主题，对前端进行全面 UI 重构。
> 技术栈：Vue 3 + TypeScript + Vite（保留），移除 Vant 移动端组件库，改为自定义组件。

---

## 第一阶段：基础设施（Design System）

- [ ] 1.1 重写 `src/styles/variables.css` — 替换为 Galaxy 深色主题色彩 Token（--bg, --bg-surface, --text-1/2/3, --brand, --pink, --cyan, --border 等）
- [ ] 1.2 重写 `src/style.css` — 全局样式：星空粒子、星云光晕、气泡配色（8种）、毛玻璃效果、圆角系统、字体系统、动画关键帧（twinkle, float 等）
- [ ] 1.3 创建 `src/components/StarryBackground.vue` — 星空粒子 + 星云光晕背景组件（全局复用）
- [ ] 1.4 创建 `src/components/GlassCard.vue` — 毛玻璃卡片通用组件（圆角、边框、backdrop-filter）

## 第二阶段：全局布局

- [ ] 2.1 重构 `src/layouts/DefaultLayout.vue` — 导航栏：64px 毛玻璃、Logo 渐变文字、中央胶囊 Tab（发现/热门/推荐）、右侧通知+头像、搜索框滚动联动（IntersectionObserver）
- [ ] 2.2 重构 FAB 悬浮发帖按钮 — 品牌渐变圆形 56px，右下固定，hover 辉光缩放

## 第三阶段：首页（列表页）

- [ ] 3.1 重构 `src/pages/Home.vue` — Hero 搜索区（标题 44px 渐变文字 + 搜索框 560px + 副标题）
- [ ] 3.2 重构首页筛选区 — 标签 Chips（pill 圆角 + 品牌色 active）+ 排序 Pills
- [ ] 3.3 重构 `src/components/PostCard.vue` — 气泡卡片：24px 圆角、8种配色渐变背景、毛玻璃、hover 上浮 + 辉光、标签胶囊 + 正文 + 图片 + footer 统计
- [ ] 3.4 重构瀑布流布局 — CSS columns 方式，4/3/2/1列响应式

## 第四阶段：帖子详情页

- [ ] 4.1 重构 `src/pages/PostDetail.vue` — 单列居中 720px，大号气泡卡片（28px 圆角、底部色条装饰）、正文 20px
- [ ] 4.2 重构操作栏 — pill 按钮行：点赞/收藏/分享/私信/举报，已点赞粉色态、私信青绿态
- [ ] 4.3 重构评论区 — 评论输入框（毛玻璃卡片、头像+匿名提示、自增高 textarea、字数统计）
- [ ] 4.4 重构 `src/components/CommentItem.vue` — 评论卡片样式（头像、楼主 badge、时间、操作区）
- [ ] 4.5 重构 `src/components/CommentTree.vue` — 嵌套回复缩进（margin-left 50px + 左边框）、折叠展开

## 第五阶段：发帖页

- [ ] 5.1 重构 `src/pages/CreatePost.vue` — 双栏布局（左编辑 + 右实时预览 400px），导航栏含草稿+发布按钮
- [ ] 5.2 左栏表单 — 匿名身份卡片（换马甲）、内容 textarea（实时联动预览）、标签选择、气泡配色色点、图片上传 3 槽、自毁时间 pills、开关（私信/投票）
- [ ] 5.3 右栏实时预览 — 预览气泡（复用 PostCard 样式，实时同步文字/标签/配色/图片）
- [ ] 5.4 响应式处理 — <960px 隐藏预览栏

## 第六阶段：登录注册页

- [ ] 6.1 重构 `src/pages/Login.vue` — 分屏布局（左装饰+右表单），左侧标语+浮动气泡+特性亮点，右侧 Tab 切换登录/注册
- [ ] 6.2 登录表单 — 邮箱+密码输入框（14px 圆角、毛玻璃背景、focus 品牌色发光）、记住我、提交按钮
- [ ] 6.3 注册表单 — 邮箱+验证码（60s 倒计时）+密码（强度指示器 3 段）+确认密码
- [ ] 6.4 响应式处理 — <768px 隐藏左侧装饰区

## 第七阶段：个人中心页

- [ ] 7.1 重构 `src/pages/Profile.vue` — Profile Hero（96px 渐变光环头像、昵称、遮掩邮箱、统计行、编辑按钮）
- [ ] 7.2 粘性 Tab 栏 — 毛玻璃容器 pill tabs（我的发布/评论/收藏/设置），sticky top 64px
- [ ] 7.3 我的发布 Tab — 瀑布流气泡卡片 + hover 删除按钮 + 空状态
- [ ] 7.4 我的评论 Tab — 列表式评论卡片 + 关联帖子链接 + 空状态
- [ ] 7.5 我的收藏 Tab — 瀑布流 + hover 取消收藏按钮 + 空状态
- [ ] 7.6 设置 Tab — 分区毛玻璃卡片（修改昵称、修改密码、深色模式 toggle、退出登录）

## 第八阶段：消息中心页（新增）

- [ ] 8.1 创建 `src/pages/Messages.vue` — 页面结构（上方私信分栏 + 下方通知分组）
- [ ] 8.2 添加路由 — `/messages` 路由，需要登录
- [ ] 8.3 私信分栏 — 左栏会话列表（头像、名称、最后消息、未读 badge、active 态）+ 右栏聊天视图（消息气泡、时间分组、输入框+字数统计）
- [ ] 8.4 通知区域 — 按日期分组（今天/昨天/更早）、毛玻璃分组卡片、通知行（彩色图标+文字+时间+未读发光边框）
- [ ] 8.5 全部标为已读 + hover 忽略按钮 + 空状态
- [ ] 8.6 响应式处理 — <768px 私信分栏变全宽列表

## 第九阶段：清理与优化

- [ ] 9.1 移除 Vant 组件库依赖 — 删除 package.json 中 vant 相关依赖，清理 vite.config.ts 中 Vant 自动导入配置
- [ ] 9.2 清理旧样式代码 — 删除不再使用的旧 CSS 变量、旧组件样式
- [ ] 9.3 全局检查 — 确保所有页面在 1200px/900px/600px 断点正常显示，无样式溢出或错位
