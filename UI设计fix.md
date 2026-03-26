# UI 设计优化 — TODO LIST

> 基于 "03-27 UI优化.md" 的反馈，以 PC 端体验为核心进行全面 UI 重构。
> 创建日期：2026-03-27

---

## 一、全局基础改造

- [x] **1-1. 全局布局从移动端优先改为 PC 端优先**
  - `DefaultLayout.vue`：`main-content` 去掉 `max-width: 960px`，改为更宽的内容区
  - 导航栏高度统一 64px，水平内边距加大，居中 logo
  - 页面内容区使用合理的最大宽度（列表页 1200px，详情/发帖/个人中心 1000px）

- [x] **1-2. 全局 hover 交互增强**
  - 所有可点击元素增加 `cursor: pointer` + hover 状态变化
  - 按钮 hover：微浮起（`translateY(-2px)` + 阴影加深）
  - 卡片 hover：阴影增强 + 微缩放（`scale(1.02)`）
  - 链接/文字按钮 hover：颜色变化 + 下划线
  - 使用 `transition: all 0.2s ease` 确保丝滑

- [x] **1-3. 背景装饰气泡**
  - `DefaultLayout.vue` 或 `global.css` 增加 3-5 个半透明渐变圆形作为背景装饰
  - 缓慢漂浮动画（CSS animation），增加"气泡宇宙"的氛围
  - `position: fixed` + `pointer-events: none` + `z-index: -1`

---

## 二、列表页重构（Home.vue + PostCard.vue）

- [x] **2-1. 瀑布流布局升级为 PC 端三列**
  - 桌面端（>=1024px）：三列瀑布流，column-count: 3
  - 平板端（768-1023px）：双列
  - 卡片间距适当加大，让气泡之间有"漂浮"感

- [x] **2-2. PostCard 气泡化增强**
  - 卡片圆角保持 24px，增加柔和阴影层次
  - hover 时气泡"浮起"效果：`transform: translateY(-4px) scale(1.01)` + 阴影加深
  - 不同卡片增加微弱的旋转偏移（`rotate(±0.5deg)`），打破规则排列
  - 短文本卡片显得更小更圆，强化"气泡"大小差异

- [x] **2-3. 卡片视差浮动效果**
  - 页面滚动时卡片有微弱的纵向差速偏移
  - 使用 `IntersectionObserver` + CSS `transform`
  - `prefers-reduced-motion: reduce` 下禁用

- [x] **2-4. 标签筛选栏 PC 端居中显示**
  - 标签栏居中排列，不再左对齐横向滚动
  - hover 时未选中标签背景变化

---

## 三、详情页重构（PostDetail.vue）

- [x] **3-1. PC 端双栏布局**
  - 左侧（60%）：帖子内容气泡
  - 右侧（40%）：评论区
  - 使用 `display: grid; grid-template-columns: 3fr 2fr; gap: 32px`
  - 去掉 `max-width: 600px`，改为 `max-width: 1000px`

- [x] **3-2. 评论区样式气泡化**
  - 评论区整体包裹在带圆角的容器内
  - 每条评论也是小气泡形态（圆角背景）
  - 子评论缩进带连线或色块区分层级

- [x] **3-3. 评论输入框重设计**
  - 不再使用 `position: fixed; bottom: 0` 全宽吸底
  - 改为评论区底部的内联输入框（跟随评论列表滚动）
  - 样式：圆角卡片内嵌 textarea + 发送按钮
  - 添加展开/收起功能：默认单行，聚焦后展开为多行

---

## 四、发帖页重构（CreatePost.vue）

- [x] **4-1. PC 端双栏布局**
  - 左侧：编辑区（textarea + 标签选择 + 背景色选择）
  - 右侧：实时预览卡片（显示效果）
  - 预览卡片使用选定的渐变背景色，跟随输入内容实时更新
  - 去掉 `max-width: 600px`，改为 `max-width: 900px`

- [x] **4-2. 编辑区域增强**
  - textarea 更大（至少 12 行高），背景半透明
  - 标签选择 hover 效果增强
  - 背景色选择圆点 hover 放大
  - 底部预留"更多选项"区域（投票、自毁等，按钮占位灰显 + tooltip "即将上线"）

---

## 五、个人中心重构（Profile.vue）

- [x] **5-1. 去掉底部弹窗，改为页面内直接展示**
  - 移除 `van-popup`，"我的发布"内容直接嵌入页面
  - 布局：上部用户信息卡片 + 下部内容列表（tab 切换"我的发布"/"我的评论"等）

- [x] **5-2. PC 端宽屏布局**
  - 左侧侧栏：用户信息卡片（头像、昵称、验证状态、统计数据、菜单）
  - 右侧主区域：帖子列表（复用 PostCard 组件）
  - 去掉 `max-width: 600px`，改为 `max-width: 1000px`

- [x] **5-3. 统计数据展示**
  - 三等分统计卡片：发布数、评论数、获赞数
  - 数字字体加大加粗，标签在下

---

## 六、微交互与动效完善

- [x] **6-1. 页面切换过渡动画**
  - `router-view` 包裹 `<Transition>` 组件
  - 进场：淡入 + 轻微上移（opacity 0→1, translateY(8px)→0, 200ms）

- [x] **6-2. 按钮点击反馈统一**
  - 所有按钮 `:active` 缩小（scale 0.96）
  - 品牌色按钮 hover 亮度提升

---

## 修复优先级

| 顺序 | 任务 | 范围 |
|------|------|------|
| 1 | 1-1~1-3 全局基础 | DefaultLayout, global.css |
| 2 | 2-1~2-4 列表页 | Home.vue, PostCard.vue |
| 3 | 3-1~3-3 详情页 | PostDetail.vue, CommentTree.vue |
| 4 | 4-1~4-2 发帖页 | CreatePost.vue |
| 5 | 5-1~5-3 个人中心 | Profile.vue |
| 6 | 6-1~6-2 动效收尾 | DefaultLayout, 全局 |
