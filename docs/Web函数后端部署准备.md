# Django 后端接入阿里云 Web 函数前的准备

## 推荐控制台参数

- 地域：`中国香港`
- 运行时：`自定义运行时 / Debian 11`
- `vCPU`：`0.5`
- 内存：`1 GB`
- 磁盘：`512 MB`
- 最小实例数：
  - 平时调试：`0`
  - 演示检查：`1`
- 单实例并发度：`1`
- 代码上传方式：`通过 ZIP 包上传代码`

## 启动命令与监听端口

- 启动命令：`bash start_fc.sh`
- 监听端口：`9000`

说明：

- 阿里云自定义运行时 Web 函数需要你自己启动 HTTP Server。
- 当前项目已经补了 `backend/start_fc.sh`，它会在 Debian 11 上切到 Python 3.12，并用 `gunicorn` 启动 Django。
- 阿里云会向 `FC_SERVER_PORT` 注入端口；脚本默认兜底为 `9000`。

## 代码 ZIP 应该包含什么

代码 ZIP 的根目录应直接包含这些内容：

- `apps/`
- `common/`
- `config/`
- `templates/`
- `manage.py`
- `requirements.txt`
- `start_fc.sh`

如果你已经本地执行过 `collectstatic`，还应把下面内容一并带上：

- `staticfiles/`

## 代码 ZIP 不应包含什么

这些内容不要打进代码 ZIP：

- `venv/`
- `__pycache__/`
- `.DS_Store`
- `.env.local`
- `db.sqlite3`
- `media/`
- `.git/`

## 为什么不要把依赖直接理解成“都放进代码 ZIP”

当前项目依赖里有：

- `pillow`
- `psycopg2-binary`

它们都包含平台相关二进制内容。你在 macOS 本地直接 `pip install` 打包出来的依赖，通常不能直接在阿里云 Debian 11 环境里运行。

因此更稳妥的做法是：

1. 代码 ZIP 只放项目源码和启动脚本
2. Python 依赖单独做成 Debian 11 兼容的层

这也和课件后半部分“先报缺依赖，再制作层”的路线一致。

## 上传代码前建议先做的两件事

1. 生成 Django 静态文件

在 `backend/` 目录执行：

```bash
python manage.py collectstatic --settings=config.settings.prod --noinput
```

2. 确认生产环境变量

可参考：

- `backend/.env.production.example`

上线到 Web 函数控制台时，需要把这些环境变量填到函数配置里，而不是依赖本地 `.env.local`。
