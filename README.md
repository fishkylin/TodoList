# Todo CLI

[English](#english) | [中文](#chinese)

---

## English

A terminal-based task manager built with Python — lightweight, bilingual, and production‑ready.

### Features

- **CRUD operations** — add, list, show, edit, delete tasks
- **Priority levels** — 0 (lowest) to 3 (highest)
- **Numeric ID shorthand** — ``todo show 1`` works just like ``todo show TASK-0001``
- **Completion toggle** — mark done or reopen with one command
- **Bilingual UI** — switch between English and Chinese via `--lang` or `.env`
- **JSON persistence** — atomic writes to `~/.todo/tasks.json` (rotating log files in `logs/`)
- **Rich terminal output** — colour‑coded tables and detail panels powered by [Rich](https://github.com/Textualize/rich)
- **Clean architecture** — repository pattern, service layer, DTOs, custom exceptions, full type hints

### Installation

**Requirements:** Python ≥ 3.13

```bash
git clone <repo-url>
cd TodoList
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
```

After installation the `todo` command is available globally inside the venv:

```bash
todo --help
```

Or run directly without installing:

```bash
python -m todo_app.main --help
```

### Quick Start

```bash
# Add tasks
todo add "Buy groceries" -p 2
todo add "Write report" -d "Q2 summary" -p 3

# List all (hide completed by default)
todo list
todo list --all

# View details (both forms are equivalent)
todo show TASK-0001
todo show 1

# Mark as done / reopen
todo done 1
todo done 1    # toggles back to pending

# Edit a task
todo edit 1 -t "Buy groceries + snacks" -p 1

# Delete (with confirmation)
todo delete 1
todo delete 1 --force    # skip confirmation
```

### Chinese Mode

```bash
todo --lang zh add "买牛奶" -p 1
todo --lang zh list
todo --lang zh show 1
```

Set the default language in `.env`:

```
TODO_LANGUAGE=zh
```

### Configuration

Create a `.env` file (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `TODO_DATA_DIR` | `~/.todo` | Data storage directory |
| `TODO_LANGUAGE` | `en` | UI language (`en` / `zh`) |
| `TODO_LOG_LEVEL` | `INFO` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

### Project Structure

```
todo_app/
├── main.py                  # Typer app entry point, dependency assembly
├── config.py                # Settings (pydantic-settings, .env)
├── dest.py                  # Context accessors (get_service / get_texts)
├── logger.py                # Rotating file + console logging
├── exceptions.py            # TodoError → StorageError / TaskNotFoundError
├── commands/
│   ├── add.py               # todo add
│   ├── list.py              # todo list   (rich Table)
│   ├── show.py              # todo show   (rich Panel)
│   ├── done.py              # todo done   (toggle)
│   ├── edit.py              # todo edit   (partial update)
│   └── delete.py            # todo delete
├── models/
│   └── task.py              # Task entity, TaskStatus enum, ID generator
├── dto/
│   ├── task_create.py       # CreateTaskDTO  (Pydantic validation)
│   ├── task_update.py       # UpdateTaskDTO  (partial update)
│   └── task_response.py     # TaskResponseDTO + from_task() factory
├── repositories/
│   ├── base.py              # TaskRepository ABC (interface)
│   ├── json_repo.py         # JsonTaskRepository (atomic writes)
│   └── memory_repo.py       # MemoryTaskRepository (tests only)
├── services/
│   └── task_service.py      # Business logic layer
├── i18n/
│   ├── __init__.py          # get_texts() factory
│   ├── en.py                # English strings
│   └── zh.py                # Chinese strings
└── tests/
    ├── conftest.py           # Shared fixtures
    ├── test_models.py        # 23 tests
    ├── test_dtos.py          # 18 tests
    ├── test_exceptions.py    #  7 tests
    ├── test_i18n.py          # 13 tests
    ├── test_memory_repo.py   # 17 tests
    ├── test_json_repo.py     # 19 tests
    └── test_task_service.py  # 27 tests
```

### Architecture

```
CLI (Typer)  →  Commands  →  Service  →  Repository (ABC)
     │              │            │              │
     └── ctx.obj ───┘            │         ┌────┴────┐
                              DTOs       JSON      Memory
                                       (prod)    (tests)
```

- **Commands** are thin — they parse CLI input, call the service, and format output.
- **Service** owns business logic, depends on the `TaskRepository` interface (not concrete storage).
- **Repositories** implement persistence; `JsonTaskRepository` uses atomic temp‑file writes.
- **DTOs** decouple the wire format (CLI ↔ service) from the domain model.

### Running Tests

```bash
pytest todo_app/tests/ -v     # 134 tests
pytest todo_app/tests/ -q     # compact output
pytest todo_app/tests/ --cov  # with coverage (if pytest-cov installed)
```

### Logging

Logs are written to `logs/app.log` (everything) and `logs/error.log` (errors only), with automatic rotation at 10 MB (5 backups). Enable debug output:

```bash
todo --debug list
```

---

## 中文

一个基于 Python 的终端任务管理工具——轻量、双语、可正式发布。

### 功能

- **完整 CRUD** — 添加、列表、详情、编辑、删除任务
- **优先级** — 0（最低）至 3（最高）
- **数字 ID 简写** — ``todo show 1`` 等同于 ``todo show TASK-0001``
- **完成状态切换** — 一键标记完成或重新打开
- **中英双语** — 通过 `--lang` 或 `.env` 切换界面语言
- **JSON 持久化** — 原子写入 `~/.todo/tasks.json`（`logs/` 目录下带滚动日志）
- **Rich 终端输出** — 基于 [Rich](https://github.com/Textualize/rich) 的彩色表格和详情面板
- **整洁架构** — 仓储模式、服务层、DTO、自定义异常、完整类型标注

### 安装

**环境要求：** Python ≥ 3.13

```bash
git clone <repo-url>
cd TodoList
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
```

安装后可在虚拟环境中直接使用 `todo` 命令：

```bash
todo --help
```

或无需安装直接运行：

```bash
python -m todo_app.main --help
```

### 快速上手

```bash
# 添加任务
todo add "买菜" -p 2
todo add "写周报" -d "第二季度总结" -p 3

# 列出任务（默认隐藏已完成）
todo list
todo list --all

# 查看详情（两种写法等价）
todo show TASK-0001
todo show 1

# 标记完成 / 重新打开
todo done 1
todo done 1    # 再次执行切换回待完成

# 编辑任务
todo edit 1 -t "买菜 + 零食" -p 1

# 删除（需确认）
todo delete 1
todo delete 1 --force    # 跳过确认
```

### 中文模式

```bash
todo --lang zh add "买牛奶" -p 1
todo --lang zh list
todo --lang zh show 1
```

在 `.env` 中设置默认语言：

```
TODO_LANGUAGE=zh
```

### 配置

创建 `.env` 文件（参考 `.env.example`）：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TODO_DATA_DIR` | `~/.todo` | 数据存储目录 |
| `TODO_LANGUAGE` | `en` | 界面语言（`en` / `zh`） |
| `TODO_LOG_LEVEL` | `INFO` | 日志级别（`DEBUG`、`INFO`、`WARNING`、`ERROR`） |

### 项目结构

```
todo_app/
├── main.py                  # Typer 入口，依赖组装
├── config.py                # 配置（pydantic-settings，.env）
├── dest.py                  # 上下文访问器（get_service / get_texts）
├── logger.py                # 滚动文件 + 控制台日志
├── exceptions.py            # TodoError → StorageError / TaskNotFoundError
├── commands/
│   ├── add.py               # todo add
│   ├── list.py              # todo list   (rich Table)
│   ├── show.py              # todo show   (rich Panel)
│   ├── done.py              # todo done   (状态切换)
│   ├── edit.py              # todo edit   (部分更新)
│   └── delete.py            # todo delete
├── models/
│   └── task.py              # Task 实体、TaskStatus 枚举、ID 生成器
├── dto/
│   ├── task_create.py       # CreateTaskDTO  (Pydantic 校验)
│   ├── task_update.py       # UpdateTaskDTO  (部分更新)
│   └── task_response.py     # TaskResponseDTO + from_task() 工厂
├── repositories/
│   ├── base.py              # TaskRepository 抽象基类
│   ├── json_repo.py         # JsonTaskRepository（原子写入）
│   └── memory_repo.py       # MemoryTaskRepository（仅测试用）
├── services/
│   └── task_service.py      # 业务逻辑层
├── i18n/
│   ├── __init__.py          # get_texts() 工厂
│   ├── en.py                # 英文字典
│   └── zh.py                # 中文字典
└── tests/
    ├── conftest.py           # 共享 fixtures
    ├── test_models.py        # 23 项
    ├── test_dtos.py          # 18 项
    ├── test_exceptions.py    #  7 项
    ├── test_i18n.py          # 13 项
    ├── test_memory_repo.py   # 17 项
    ├── test_json_repo.py     # 19 项
    └── test_task_service.py  # 27 项
```

### 架构

```
CLI (Typer)  →  Commands  →  Service  →  Repository (ABC)
     │              │            │              │
     └── ctx.obj ───┘            │         ┌────┴────┐
                              DTOs       JSON      Memory
                                       (生产)    (测试)
```

- **Commands** 层极薄——只负责解析输入、调用服务、格式化输出。
- **Service** 持有业务逻辑，依赖 `TaskRepository` 接口而非具体存储。
- **Repository** 实现持久化；`JsonTaskRepository` 使用临时文件 + 重命名保证原子写入。
- **DTO** 隔离传输格式（CLI ↔ Service）与领域模型。

### 运行测试

```bash
pytest todo_app/tests/ -v     # 134 项测试
pytest todo_app/tests/ -q     # 紧凑输出
pytest todo_app/tests/ --cov  # 含覆盖率（需安装 pytest-cov）
```

### 日志

日志写入 `logs/app.log`（全部级别）和 `logs/error.log`（仅错误），单文件 10 MB 自动滚动（保留 5 个备份）。开启调试输出：

```bash
todo --debug list
```

---

*Todo CLI — simple tools, well built.*
