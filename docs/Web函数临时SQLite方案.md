# Web 函数临时 SQLite 演示方案

仅用于课程演示，不适合正式上线。

## 适用场景

- 当前没有可用的外部 PostgreSQL
- 需要先让注册、登录、首页接口跑通
- 接受“实例重启后数据可能丢失”

## 方案原理

- 生产环境通过 `USE_SQLITE_IN_PROD=true` 切换到 SQLite
- SQLite 文件放在 Web 函数可写目录 `/tmp/anonymous_wall.sqlite3`
- Web 函数启动时自动执行 `migrate`

## Web 函数需要添加的环境变量

```txt
USE_SQLITE_IN_PROD=true
SQLITE_PATH=/tmp/anonymous_wall.sqlite3
RUN_MIGRATE_ON_START=true
RUN_DEMO_SEED_ON_START=true
```

## 建议同时保持的函数配置

- 最小实例数：`1`
- 单实例并发度：`1`
- 如果控制台支持，最大实例数也尽量限制为 `1`

## 方案风险

- 函数冷启动、重新部署、实例替换后，数据库内容可能丢失
- 多实例时，每个实例都有自己的 SQLite 文件，数据会不一致
- 只适合演示，不适合作为最终提交形态

## 演示数据自动恢复

如果你希望实例丢数据后能自动恢复演示数据，可开启：

```txt
RUN_DEMO_SEED_ON_START=true
```

它的行为不是“每次启动都强制清库重建”，而是：

1. 先执行 `migrate`
2. 检查数据库里是否已经有用户
3. 只有在空库时，才执行轻量版演示数据命令 `seed_demo_data_light`

这样更适合临时演示环境。

## 当前默认的轻量演示数据规模

- 管理员账号：`Admin / admin`
- 普通用户：`18`
- 帖子：`48`

这份数据仍然保留了原始脚本中的评论、通知、私信、举报、审核等关系，但规模明显更小，更适合 Web 函数启动。

## 如需切换演示数据命令

默认自动执行的是：

```txt
DEMO_SEED_COMMAND=seed_demo_data_light
```

通常不需要手动设置；只有你想切回其他命令时，才需要覆盖它。
