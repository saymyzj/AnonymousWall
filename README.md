# AnonymousWall — 匿名树洞

> 一个校园/社区匿名表白墙 Web 应用，用户可以匿名发布心声、互动评论、点赞，所有身份信息完全隔离保护。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Vant 4 + Pinia + Vue Router |
| 后端 | Django 6 + Django REST Framework + SimpleJWT |
| 数据库 | PostgreSQL 16（生产） / SQLite（开发） |
| 管理后台 | Django Admin + SimpleUI |
| 内容审核 | DFA 敏感词过滤（L1） |

## 核心功能

- **匿名身份**：注册后自动生成随机匿名昵称（匿名+动物名+#编号）和头像种子
- **发帖系统**：支持 6 种标签（表白/吐槽/求助/树洞/失物招领/搭子）、8 种气泡背景色
- **评论系统**：帖子内匿名身份分配（匿名A/B/C...），楼主标识，支持嵌套回复
- **点赞互动**：帖子/评论 toggle 点赞，实时计数更新
- **敏感词审核**：DFA 自动机过滤，硬拦截词直接阻止发布，软标记词标记待审
- **管理后台**：SimpleUI 美化，帖子/评论/用户管理，禁言操作，审核队列

## 本地开发

### 环境要求

- Python 3.12+
- Node.js 18+
- （可选）Docker — 用于 PostgreSQL

### 1. 启动数据库（可选）

如果使用 PostgreSQL：

```bash
docker compose -f docker-compose.dev.yml up -d
# 然后设置环境变量
export USE_POSTGRES=true
```

默认使用 SQLite，无需额外配置。

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境（首次）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 加载默认敏感词库
python manage.py load_sensitive_words

# 启动开发服务器
python manage.py runserver
```

后端运行在 http://localhost:8000，管理后台 http://localhost:8000/admin/

### 3. 启动前端

```bash
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

前端运行在 http://localhost:5173，API 请求自动代理到后端。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DJANGO_SETTINGS_MODULE` | Django 配置模块 | `config.settings.dev` |
| `USE_POSTGRES` | 是否使用 PostgreSQL | `false`（使用 SQLite） |
| `DJANGO_SECRET_KEY` | 生产环境密钥 | 内置开发密钥 |
| `DB_NAME` | 数据库名 | `anonymous_wall` |
| `DB_USER` | 数据库用户 | `postgres` |
| `DB_PASSWORD` | 数据库密码 | `postgres` |
| `DB_HOST` | 数据库地址 | `localhost` |
| `DB_PORT` | 数据库端口 | `5432` |

## 项目结构

```
AnonymousWall/
├── backend/
│   ├── apps/
│   │   ├── users/          # 用户体系（注册/登录/匿名身份）
│   │   ├── posts/          # 帖子系统（CRUD/筛选/排序）
│   │   ├── comments/       # 评论系统（嵌套回复/匿名标识）
│   │   ├── interactions/   # 互动（点赞）
│   │   └── moderation/     # 内容审核（DFA 敏感词）
│   ├── common/             # 公共模块（分页/异常/响应）
│   ├── config/             # Django 项目配置
│   └── manage.py
├── frontend/
│   └── src/
│       ├── api/            # API 请求封装
│       ├── components/     # 通用组件（PostCard/CommentItem）
│       ├── layouts/        # 布局组件
│       ├── pages/          # 页面（Home/Login/CreatePost/PostDetail/Profile）
│       ├── router/         # 路由配置
│       ├── stores/         # Pinia 状态管理
│       └── styles/         # 全局样式 + CSS 变量
├── docker-compose.dev.yml
└── README.md
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health/` | 健康检查 |
| POST | `/api/auth/register/` | 邮箱注册 |
| POST | `/api/auth/login/` | 登录获取 JWT |
| POST | `/api/auth/token/refresh/` | 刷新 Token |
| GET | `/api/auth/me/` | 获取当前用户信息 |
| GET | `/api/posts/` | 帖子列表（支持 tag/time/sort 筛选） |
| POST | `/api/posts/create/` | 发帖 |
| GET | `/api/posts/{id}/` | 帖子详情 |
| DELETE | `/api/posts/{id}/delete/` | 删除帖子 |
| POST | `/api/posts/{id}/like/` | 帖子点赞/取消 |
| GET | `/api/posts/{id}/comments/` | 评论列表 |
| POST | `/api/posts/{id}/comments/create/` | 发表评论 |
| DELETE | `/api/comments/{id}/delete/` | 删除评论 |
| POST | `/api/comments/{id}/like/` | 评论点赞/取消 |
