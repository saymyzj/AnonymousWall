# 匿名宇宙

校园匿名社区 Web 项目，支持匿名发帖、评论互动、点赞收藏、匿名私信、站内通知、内容审核、推荐排序与管理员工作台。

## 项目现状

- 前端：Vue 3 + TypeScript + Vite + Pinia + Vue Router
- 后端：Django 6 + DRF + SimpleJWT + SimpleUI
- 数据库：开发环境支持 SQLite / PostgreSQL，生产配置为 PostgreSQL
- 缓存：Redis 已接入未读消息摘要缓存，Redis 不可用时会自动回退数据库统计
- AI 审核：DeepSeek

## 目录结构

```text
匿名宇宙/
├── backend/                  # Django 后端
├── frontend/                 # Vue 前端
├── docx/                     # 设计文档、TODO、Bug 记录
├── docker-compose.dev.yml    # 开发环境 PostgreSQL + Redis
└── README.md
```

## 核心功能

- 匿名身份：注册后自动生成随机昵称与头像种子，支持刷新匿名身份
- 发帖系统：6 个标签、背景色、图片上传、投票、定时自毁、私信开关
- 评论系统：嵌套回复、楼主标识、点赞、举报、审核状态回显
- 互动系统：帖子/评论点赞、帖子收藏、举报处理、站内通知
- 消息中心：匿名私信会话、通知列表、未读摘要、全部已读
- 推荐排序：根据点赞、收藏、评论行为计算标签偏好
- 管理后台：管理员工作台、审核详情、举报中心、用户中心、推荐拆解

## 当前策略说明

- 搜索：已实现正文关键词相关度排序，综合命中位置、命中频次和互动热度
- 未读数：已优先走 Redis 缓存；Redis 不可用时自动回退数据库统计
- AI 审核：
  - 硬拦截词：直接 `reject`
  - 软标记词：`not_run` + `ai_suspect`
  - DeepSeek：返回 `accept / confuse / reject`
- 图片处理：当前由后端同步执行 Pillow 压缩、转 JPEG、生成缩略图
- 异步任务：Celery 暂未接入；过期检查、审核超时等仍以请求触发为主

## 环境要求

- Python 3.13 推荐
- Node.js 18+
- npm 9+
- 可选：Docker / Docker Compose

## 一、后端配置

### 1. 创建虚拟环境并安装依赖

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

如果仓库里已经有 `backend/venv`，也可以直接复用：

```bash
cd backend
source venv/bin/activate
```

### 2. 环境变量

后端会自动读取以下文件：

- `backend/.env`
- `backend/.env.local`

当前最常用的环境变量如下：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DJANGO_SETTINGS_MODULE` | Django 配置模块 | `config.settings.dev` |
| `USE_POSTGRES` | 开发环境是否使用 PostgreSQL | 未设置时使用 SQLite |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 空 |
| `DEEPSEEK_MODEL` | DeepSeek 模型名 | `deepseek-chat` |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_TIMEOUT` | AI 审核超时时间（秒） | `25` |
| `REDIS_URL` | Redis 连接串 | `redis://127.0.0.1:6379/0` |
| `REDIS_TIMEOUT` | Redis 连接超时（秒） | `0.5` |
| `REDIS_UNREAD_TTL` | 未读摘要缓存 TTL（秒） | `120` |
| `DB_NAME` | PostgreSQL 数据库名 | `anonymous_wall` |
| `DB_USER` | PostgreSQL 用户名 | `postgres` |
| `DB_PASSWORD` | PostgreSQL 密码 | 空 |
| `DB_HOST` | PostgreSQL 主机 | `localhost` |
| `DB_PORT` | PostgreSQL 端口 | `5432` |

一个可参考的 `backend/.env.local` 示例：

```env
USE_POSTGRES=true
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_TIMEOUT=25
REDIS_URL=redis://127.0.0.1:6379/0
REDIS_TIMEOUT=0.5
REDIS_UNREAD_TTL=120
```

### 3. 数据库

开发环境有两种方式：

#### 方式 A：默认 SQLite

不设置 `USE_POSTGRES=true` 时，Django 会直接使用：

- `backend/db.sqlite3`

适合快速本地体验。

#### 方式 B：使用 PostgreSQL

先启动容器：

```bash
docker compose -f docker-compose.dev.yml up -d
```

再在 `backend/.env.local` 中设置：

```env
USE_POSTGRES=true
```

### 4. Redis

当前 `docker-compose.dev.yml` 已包含 Redis：

```bash
docker compose -f docker-compose.dev.yml up -d
```

Redis 目前主要用于：

- 顶部导航栏未读消息摘要缓存
- 通知/私信未读数的短 TTL 缓存

即使 Redis 没启动，项目也可以跑，只是会回退为数据库统计。

### 5. 执行迁移

```bash
cd backend
source venv/bin/activate
python manage.py migrate
```

### 6. 启动后端

```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

默认地址：

- API / Admin: [http://localhost:8000](http://localhost:8000)

## 二、前端配置

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
cd frontend
npm run dev
```

默认地址：

- 前端： [http://localhost:5173](http://localhost:5173)

### 3. 生产构建

```bash
cd frontend
npm run build
```

## 三、AI 审核配置说明

AI 审核逻辑在：

- [backend/apps/moderation/services.py](/Users/zhoujia/code/webProject/AnonymousWall/backend/apps/moderation/services.py)

审核顺序：

1. DFA 敏感词过滤
2. DeepSeek 文本审核
3. 管理员人工复核

### DFA 规则

- 命中硬拦截词：直接拒绝发布
- 命中软标记词：标为 `ai_suspect`，`ai_decision=not_run`

### DeepSeek 返回值

系统期望 DeepSeek 返回 JSON，字段为：

- `decision`
- `risk_level`
- `reason`

其中 `decision` 只允许：

- `accept`
- `confuse`
- `reject`

如果 AI 调用失败，系统会自动回退为人工复核。

### 未配置 API Key 时的行为

如果未配置 `DEEPSEEK_API_KEY`：

- 项目仍可运行
- AI 审核会跳过
- 审核结果会回落为“未配置 AI key，跳过审核”的路径

## 四、初始化数据

### 1. 创建超级管理员

如果你想手动创建：

```bash
cd backend
source venv/bin/activate
python manage.py createsuperuser
```

### 2. 重建演示数据

项目内置了一个大规模演示数据命令：

```bash
cd backend
source venv/bin/activate
python manage.py reset_demo_data
```

这个命令会：

- 清空现有数据库内容
- 重建管理员账号
- 生成大量用户、帖子、评论、举报、通知、私信、投票与推荐行为数据

重建后的管理员账号固定为：

- 账号：`Admin`
- 密码：`admin`

## 五、管理后台

管理后台入口：

- [http://localhost:8000/admin/](http://localhost:8000/admin/)

当前后台主入口已经是工作台，不是传统 Django change list 工作流。主要页面有：

- `/admin/workbench/dashboard/`
- `/admin/workbench/review-queue/`
- `/admin/workbench/reports/`
- `/admin/workbench/content/`
- `/admin/workbench/users/`
- `/admin/workbench/recommendation/`
- `/admin/workbench/operations/`

## 六、常用命令

### 后端

```bash
cd backend
source venv/bin/activate

python manage.py migrate
python manage.py runserver
python manage.py createsuperuser
python manage.py reset_demo_data
python manage.py shell
```

### 前端

```bash
cd frontend
npm install
npm run dev
npm run build
```

### 容器

```bash
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml down
```

## 七、当前 API 概览

### 认证

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/token/refresh/`
- `GET /api/auth/me/`
- `PATCH /api/auth/preferences/`
- `GET /api/auth/dashboard/`
- `POST /api/auth/identities/refresh/`

### 帖子

- `GET /api/posts/`
- `GET /api/home/meta/`
- `POST /api/posts/create/`
- `GET /api/posts/{id}/`
- `PATCH /api/posts/{id}/edit/`
- `POST /api/posts/{id}/vote/`
- `DELETE /api/posts/{id}/delete/`

### 评论

- `GET /api/posts/{id}/comments/`
- `POST /api/posts/{id}/comments/create/`
- `DELETE /api/comments/{id}/delete/`

### 互动 / 消息

- `POST /api/posts/{id}/like/`
- `POST /api/posts/{id}/favorite/`
- `POST /api/comments/{id}/like/`
- `POST /api/reports/create/`
- `GET /api/notifications/`
- `POST /api/notifications/read-all/`
- `POST /api/notifications/{id}/read/`
- `GET /api/messages/unread-summary/`
- `GET /api/messages/conversations/`
- `POST /api/messages/send/`
- `POST /api/messages/conversations/{id}/reply/`
- `POST /api/messages/conversations/{id}/block/`

## 八、已知现实边界

- Redis 目前只落了一版未读摘要缓存，还没有扩展到热帖缓存、限流和 Celery
- Celery、异步图片处理、对象存储、Nginx 生产编排目前都还没有落地
- 评论回复通知、私信举报、修改密码等设计文档中的能力仍未完整实现
- 开发环境下部分管理与测试更适合配合 `reset_demo_data` 一起使用

## 九、文档位置

项目的设计文档、TODO 和历史记录统一放在：

- [docx](/Users/zhoujia/code/webProject/AnonymousWall/docx)

其中最重要的两份是：

- [docx/功能设计.md](/Users/zhoujia/code/webProject/AnonymousWall/docx/功能设计.md)
- [docx/架构设计.md](/Users/zhoujia/code/webProject/AnonymousWall/docx/架构设计.md)
