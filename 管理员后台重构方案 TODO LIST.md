# 管理员后台重构方案 TODO LIST

## 背景与问题

当前管理员后台的核心问题是：所有工作台页面继承自 SimpleUI 的 `admin/base_site.html`，在 SimpleUI 已有侧边栏的基础上又嵌套了一套自定义侧边栏布局，导致两套导航系统冲突——自定义侧边栏撑满了 SimpleUI 内容区的全部宽度，主内容区完全不可见。具体表现为：

- 进入任何工作台页面后，只能看到自定义侧边栏导航，右侧的仪表盘、审核队列、内容列表等核心内容全部被挤出可视区域。
- SimpleUI 的框架布局（iframe + 左侧菜单）与工作台的 CSS Grid 布局互相干扰，无法通过简单调整 CSS 修复。
- `/admin/` 首页（home.html）同样继承 SimpleUI 基础模板，存在相同的布局冲突。
- 页面之间的导航高亮、跨流程跳转虽然在代码层面已实现，但由于布局完全不可用，这些功能从未真正生效。

## 目标

- 建立完全独立于 SimpleUI 的工作台骨架，让工作台页面拥有自己的完整 HTML 文档结构，不再受 SimpleUI 框架布局干扰。
- 保留 SimpleUI 作为 Django 原始后台的 UI 框架，工作台侧边栏底部提供回到 Django 原始后台的入口。
- 按"总览 → 审核 → 举报 → 内容 → 用户 → 运营"的工作流组织导航入口。
- 让每个工作台页面正确渲染：侧边栏导航 + 页面标题/说明/指标 + 主内容区。
- 保持现有功能和数据层（`admin_panel.py`、`admin_views.py`）可用，不做数据库结构调整。

## 非目标

- 不改动审核业务规则本身。
- 不替换 Django Admin 或 SimpleUI（原始后台仍然可用）。
- 不在本轮新增复杂图表或前端框架。

## 方案概述

1. 新建 `backend/templates/admin/workbench/_base.html` 作为独立的工作台基础模板，是一个完整的 HTML 文档（不继承 SimpleUI），内含自定义侧边栏、页面头部和内容插槽。
2. 重写 `_styles.html`，使用完全自包含的 CSS（含 reset），实现 260px 侧边栏 + 自适应主内容区的 Grid 布局，并包含移动端响应式适配（≤1024px 时侧边栏变为抽屉式）。
3. 所有工作台页面模板改为继承 `_base.html` 而非 `admin/base_site.html`，消除与 SimpleUI 的布局冲突。
4. `/admin/` 首页（`home.html`）改为独立 HTML 文档（使用模板标签获取数据），不再继承 SimpleUI 基础模板。
5. 侧边栏底部保留"Django 原始后台"入口，确保管理员仍可访问原始表单页。
6. 修复 `user_detail_view` 中缺少的异常处理。

## 风险与约束

- 工作台页面不再继承 SimpleUI，意味着 SimpleUI 的主题切换、消息提示等功能不会出现在工作台页面中。这是预期行为——工作台是独立的管理界面。
- Django 原始 admin 页面（帖子表单、评论表单、敏感词管理等）仍使用 SimpleUI，不受影响。
- 工作台导航中的"原始表单"分组提供了回到 SimpleUI 管理的入口。

## 验证计划

- 运行 `python manage.py check` 确认 Django 配置与模板引用无误 ✅
- 逐一检查以下页面是否能正常渲染：
  - `/admin/` 首页 ✅
  - `/admin/workbench/dashboard/` 后台总览 ✅
  - `/admin/workbench/review-queue/` 审核队列 ✅
  - `/admin/workbench/reports/` 举报中心 ✅
  - `/admin/workbench/content/` 内容中心 ✅
  - `/admin/workbench/users/` 用户中心 ✅
  - `/admin/workbench/users/<id>/` 用户详情 ✅
  - `/admin/workbench/operations/` 运营配置 ✅
  - `/admin/workbench/recommendation/` 推荐系统 ✅
- 检查导航高亮、快捷入口、内容筛选是否符合预期 ✅
- 检查移动端响应式（≤1024px 汉堡菜单）是否正常 ✅

## TODO LIST

- [x] 诊断现有问题并建立重构方案
  - 范围：仓库根目录文档
  - 验证：文档包含问题根因分析、方案、验证与分项 TODO
  - 依赖：无

- [x] 新建独立工作台基础模板，脱离 SimpleUI 布局
  - 范围：`backend/templates/admin/workbench/_base.html`
  - 验证：工作台页面作为独立 HTML 文档渲染，不再受 SimpleUI iframe/sidebar 干扰
  - 依赖：无

- [x] 重写工作台共享组件（样式、导航、页面头部）
  - 范围：`backend/templates/admin/workbench/_styles.html`、`_nav.html`、`_page_header.html`
  - 验证：260px 侧边栏 + 自适应内容区正确渲染，响应式断点生效，导航高亮正常
  - 依赖：依赖独立基础模板

- [x] 重建所有工作台页面模板
  - 范围：`dashboard.html`、`review_queue.html`、`report_center.html`、`content_center.html`、`user_center.html`、`user_detail.html`、`operations_center.html`、`recommendation_center.html`、`moderation_detail.html`
  - 验证：每个页面继承 `_base.html`，指标卡片、列表、筛选、操作按钮均可正常渲染和交互
  - 依赖：依赖共享组件完成

- [x] 统一 `/admin/` 首页与工作台入口
  - 范围：`backend/templates/admin/home.html`
  - 验证：管理员登录后首页使用独立 HTML 文档结构，与工作台页面信息架构一致
  - 依赖：依赖共享组件完成

- [x] 修复边缘情况与完成回归检查
  - 范围：`backend/common/admin_views.py`、`backend/common/admin_panel.py`
  - 验证：`python manage.py check` 通过，所有工作台页面无模板错误，用户不存在时优雅降级
  - 依赖：依赖前序重构完成

## 本轮完成记录

- **根因**：所有工作台模板继承 `admin/base_site.html`（SimpleUI），自定义侧边栏与 SimpleUI 自身侧边栏冲突，导致主内容区不可见。
- **解法**：新建 `_base.html` 作为独立 HTML 文档模板，所有工作台页面改为继承此模板，彻底绕过 SimpleUI 布局。
- 已重写全部 12 个模板文件（1 个基础模板 + 3 个共享组件 + 8 个页面模板 + 1 个首页）。
- 已重写 CSS 样式系统，使用 260px 侧边栏 + 自适应内容区的 Grid 布局，包含移动端响应式支持。
- 侧边栏底部保留"Django 原始后台"入口，确保与 SimpleUI 管理页面的双向可达。
- 精简导航结构：工作流主线、对象中心、原始表单三个分组，底部单独放置 Django 原始后台入口。
- 修复 `user_detail_view` 中 `User.DoesNotExist` 未捕获的问题。
- `python manage.py check` 通过，全部 9 个工作台页面 + `/admin/` 首页均已验证可正常渲染。
