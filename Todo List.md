# Todo List CLI — 面向初学者的企业级 PRD 与分步开发手册

> **这份文档是什么**：一份为 Python 初学者设计的完整项目开发指南。不仅告诉你"怎么做"，更解释清楚**为什么要这样做**——每个设计决策背后的原因、每个概念的含义，确保你做完这个项目后，能看懂真实企业项目的代码结构。
>
> **适合谁**：掌握了 Python 基础语法（变量、函数、类、文件读写、异常处理），但没做过正式项目、不知道"代码该怎么组织"的开发者。
>
> **技术栈**：Python 3.14+ | UV 包管理器 | Typer (CLI) | Pydantic v2 (数据校验) | Rich (终端美化) | JSON 本地存储
>
> **读完这份文档你能获得什么**：
> - 理解分层架构（命令层 → 服务层 → 存储层）为什么这样分，每层做什么
> - 理解 Enum、DTO、Repository、依赖注入、ABC 等企业级概念
> - 拿到一个陌生项目的目录结构时，能大致判断每个文件是干什么的
> - 一个可以写到简历里的完整 CLI 项目

---

## 目录

- [0. 项目环境：UV 包管理器](#0-项目环境uv-包管理器)
- [1. 概念讲解：你必须先理解的 10 个设计概念](#1-概念讲解你必须先理解的-10-个设计概念)
- [2. 项目结构：每个文件是干什么的](#2-项目结构每个文件是干什么的)
- [3. 架构总览：一个命令的执行旅程](#3-架构总览一个命令的执行旅程)
- [4. 全局参数](#4-全局参数)
- [5. 开发阶段（按此顺序编码）](#5-开发阶段按此顺序编码)
- [6. 测试策略](#6-测试策略)
- [7. 常见误区](#7-常见误区)

---

## 0. 项目环境：UV 包管理器

### 0.1 什么是 UV？

**UV** 是一个用 Rust 写的 Python 包管理器，可以理解为 `pip` + `venv` + `pyenv` 的合体，但比它们都快 10-100 倍。它的角色：

| 传统工具 | UV 等价命令 | 做什么 |
|----------|-----------|--------|
| `python -m venv .venv` | `uv venv` | 创建虚拟环境 |
| `pip install xxx` | `uv add xxx` | 安装依赖 |
| `pip install -e .` | `uv sync` | 安装项目的所有依赖 |
| `requirements.txt` | `pyproject.toml` | 声明依赖 |
| `pyenv` (管理 Python 版本) | `uv python install 3.14` | 下载并管理 Python 版本 |

### 0.2 初始化项目

```bash
# 1. 确认 UV 已安装
uv --version
# 如果没有 → curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 安装 Python 3.14（UV 会自动管理，不需要 pyenv）
uv python install 3.14

# 3. 创建项目虚拟环境（UV 自动检测 .python-version）
cd ~/Desktop/todolist
uv venv

# 4. 激活虚拟环境（选其一）
source .venv/bin/activate     # macOS / Linux

# 5. 添加依赖（UV 自动更新 pyproject.toml + 锁文件）
uv add typer rich "pydantic>=2.0" pydantic-settings

# 6. 添加开发依赖（测试用）
uv add --dev pytest

# 7. 安装所有依赖
uv sync

# 8. 验证
uv run python -c "import typer; import pydantic; import rich; print('OK')"
```

### 0.3 `pyproject.toml` 的样子

```toml
[project]
name = "todolist"
version = "0.1.0"
description = "Terminal-based todo manager — learning project"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "typer>=0.15",
    "rich>=13.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
]

[project.scripts]
todo = "todo_app.main:app"   # 安装后用 `todo` 命令启动，不需要 ./todo 脚本了

[project.optional-dependencies]
dev = ["pytest>=8.0"]
```

> **`.python-version` 文件**：里面就一行 `3.14`。UV 看到这个文件就会自动使用 Python 3.14。不需要它时也可以删掉——UV 会从 `requires-python` 读取版本约束。

**日常开发命令**：

```bash
uv sync              # 安装/同步依赖（类似 npm install）
uv add xxx           # 添加新依赖
uv add --dev xxx     # 添加开发依赖
uv run python xxx.py # 用虚拟环境中的 Python 执行脚本
uv run todo          # 运行项目入口
uv run pytest        # 运行测试
```

---

## 1. 概念讲解：你必须先理解的 10 个设计概念

> **重要**：不要跳过这一节。很多教程只告诉你"这样写"，不告诉你"为什么"。下面每个概念都用一个生活类比开头，然后用代码验证。

### 1.1 为什么用 Enum 管理状态？

**生活类比**：快递包裹有三种状态——"运输中"、"已签收"、"已退货"。你不会用 `1`、`2`、`3` 来表示，因为三个月后你看到 `status = 1` 完全不记得什么意思。

**代码对比**：

```python
# ❌ 原始写法：用字符串，容易打错
task.status = "done"     # 打对了
task.status = "don"      # 打错了，但 Python 不会报错！bug 潜伏

# ❌ 原始写法：用整数，完全不知道什么意思
task.status = 1          # 1 是什么？已完成？未完成？

# ✅ 用 Enum：只有合法值能赋值，打错立刻报错
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"        # 未完成——任务的初始状态
    COMPLETED = "completed"    # 已完成——用户标记完成后的状态

task.status = TaskStatus.COMPLETED   # ✅ 正确
task.status = "completed"            # ✅ 也正确（因为 str 基类）
task.status = "don"                  # ❌ 报错！ValueError
```

**为什么 `str, Enum` 而不是 `Enum`**：继承 `str` 后，枚举值在 JSON 序列化时自动变成字符串 `"pending"` 而不是 `TaskStatus.PENDING`。这样存到 JSON 文件里好看，读回来也能直接构造。

### 1.2 PENDING 和 COMPLETED 分别代表什么？

| 状态 | 含义 | 数据层面发生了什么 |
|------|------|-------------------|
| `PENDING` | 任务刚创建，还没完成 | `completed_at` 为 `None` |
| `COMPLETED` | 用户标记为已完成 | `completed_at` 记录了完成时间 |

状态转换规则（状态机）：

```text
PENDING ──[mark_completed()]──→ COMPLETED
COMPLETED ──[mark_pending()]──→ PENDING
```

这就是 `Task` 模型上 `mark_completed()` 和 `mark_pending()` 两个方法的作用——它们不只是改一个字段，而是同时更新 `status`、`completed_at`、`updated_at` 三个字段，保证数据一致性。

### 1.3 为什么对存储接口进行抽象？（Repository 模式）

**生活类比**：你去图书馆借书。你只需要知道"把借书证给管理员，拿到书"。你不需要关心书是从书架 A 取的还是从仓库调来的。图书馆可以重新布置书架（换存储方式），但不影响你借书的流程。

**代码对比**：

```python
# ❌ 不抽象：Service 直接操作 JSON 文件
class TaskService:
    def add_task(self, title):
        with open("tasks.json", "r") as f:     # 读 JSON
            tasks = json.load(f)
        tasks.append({"title": title})
        with open("tasks.json", "w") as f:     # 写 JSON
            json.dump(tasks, f)

# 问题：如果未来要换成 SQLite？改 Service。换成 PostgreSQL？又改 Service。
#       Service 应该只关心"添加任务"这个业务动作，不关心"数据存哪"。

# ✅ 抽象：Service 只依赖接口，不关心实现
class TaskService:
    def __init__(self, repo: TaskRepository):   # repo 可以是任何实现了接口的东西
        self.repo = repo

    def add_task(self, title):
        task = Task(title=title)
        return self.repo.add(task)              # 不关心存哪，只关心"存了"
```

**好处清单**：
1. **换存储不改业务代码**：从 JSON 换 SQLite，写新的 repo 类即可，Service 一行不改
2. **测试不用文件系统**：测试 Service 时注入 `MemoryTaskRepository`，快、干净、隔离
3. **新人看得懂**：看到 `TaskRepository` 接口就知道"这是管存储的"，6 个方法就是全部能力

### 1.4 Service 层的主要职责和目的

**一句话**：Service 是"业务规则的执行者"，它协调 Model 和 Repository，但你从外面看就是一个方法调用完成一个业务动作。

**Service 做什么**：
- 接收校验过的数据 → 创建领域对象 → 调 Repository → 返回结果
- 处理"一个业务动作涉及多个步骤"的情况（比如"完成任务"= 找到任务 → 改状态 → 保存）
- 保证业务规则（比如"已完成的任务可以重新打开"）

**Service 不做什么**：
- 不校验输入数据（Pydantic DTO 在进入 Service 前已经校验好了）
- 不操作文件（Repository 负责）
- 不处理命令行参数（Command 负责）

**为什么需要 Service 层？为什么不能直接在命令里调 Repository？**

```python
# ❌ 命令里直接调 Repository
def add(ctx, title):
    repo = JsonTaskRepository(Path("tasks.json"))
    task = Task(title=title)
    repo.add(task)
    # 问题：如果想在添加任务时发通知、写日志、统计数量？
    #       每一条命令都要改！散落在各处。

# ✅ 有 Service 层
def add(ctx, title):
    service = ctx.obj["service"]
    service.add_task(CreateTaskDTO(title=title))
    # 所有"添加任务"的通用逻辑都在 add_task 里，一个地方改。
```

### 1.5 为什么要用私有方法？（`_method_name` 前缀）

**Python 中的约定**：名字以 `_` 开头的方法/属性是"内部实现细节，外部不要用"。

```python
class JsonTaskRepository:
    def _load_data(self):     # ← 私有方法：外部不应该直接调用
        """读 JSON 文件，处理损坏。"""
        ...

    def get_all(self):        # ← 公开方法：这是接口的一部分
        """返回所有任务。"""
        data = self._load_data()
        return [Task.model_validate(t) for t in data["tasks"]]
```

**为什么**：
- `get_all()` 是接口承诺的功能——外部放心调用
- `_load_data()` 是实现细节——未来可能改字段名、改文件格式，外部不需要知道
- 看类的时候，一眼就知道哪些方法是"对外的承诺"，哪些是"内部的帮手"

### 1.6 DTO 是什么？为什么需要它？

**DTO = Data Transfer Object（数据传输对象）**。大白话：**专门用来在不同层之间传数据的简单对象**。

**生活类比**：你去银行办业务，柜员不会让你直接操作银行金库（Model），而是给你一张"存款单"（DTO）——你填好信息，柜员验证无误后，才操作金库。

**这个项目中有三种 DTO**：

| DTO | 方向 | 用途 | 例子 |
|-----|------|------|------|
| `CreateTaskDTO` | 输入 | 用户想创建任务时传入的数据 | `{title: "Buy milk", priority: 2}` |
| `UpdateTaskDTO` | 输入 | 用户想修改任务时传入的数据 | `{task_id: "TASK-0001", title: "New title"}` |
| `TaskResponseDTO` | 输出 | 返回给用户看的任务数据 | `{id: "...", title: "...", is_completed: true}` |

**为什么不让 Command 直接创建 `Task` 对象**：

```python
# ❌ 没有 DTO：命令层直接创建内部模型
def add(ctx, title):
    task = Task(title=title, description=None, priority=0)
    # 问题：命令层需要知道 Task 的构造细节。
    #       未来 Task 加了字段，命令层也要改。
    service.add_task(task)

# ✅ 有 DTO：命令层只需要填"用户提供了什么"
def add(ctx, title, description=None, priority=0):
    dto = CreateTaskDTO(title=title, description=description, priority=priority)
    # DTO 在构造时自动校验（Pydantic）—— title 非空、priority 0-3
    # Service 内部决定如何把 DTO 转成 Task 并保存
    service.add_task(dto)
```

**DTO 的 Pydantic 校验**：
```python
dto = CreateTaskDTO(title="")  # ❌ 立刻报错！min_length=1
dto = CreateTaskDTO(title="Buy milk", priority=5)  # ❌ 立刻报错！ge=0, le=3
dto = CreateTaskDTO(title="Buy milk")  # ✅ 通过
```

### 1.7 什么是依赖注入？（Dependency Injection / DI）

**一句话**：一个对象需要的依赖（比如 Repository）不从内部创建，而是从外部传入。

```python
# ❌ 不注入：Service 内部自己创建依赖
class TaskService:
    def __init__(self):
        self.repo = JsonTaskRepository(Path("tasks.json"))  # 写死了！
        # 问题：测试时要换成内存版？不行。换成 SQLite？不行。

# ✅ 注入：依赖从外面传进来
class TaskService:
    def __init__(self, repo: TaskRepository):   # 只要实现了接口就行
        self.repo = repo

# 实际使用时：
service = TaskService(repo=MemoryTaskRepository())  # 测试用
service = TaskService(repo=JsonTaskRepository(path)) # 生产用
```

**在这个项目中 DI 怎么实现的**：`main.py` 的全局回调承担"组装工厂"的角色——它创建 Settings、Repository、Service，然后塞进 `ctx.obj`。每个命令函数从 `ctx.obj` 取出 Service。命令函数不需要知道 Service 的依赖是什么。

### 1.8 什么是分层架构？为什么不能把所有代码写一个文件里？

**分层**：

```text
┌─────────────────┐
│  commands/      │  ← 只做：解析参数 → 调 Service → 输出结果
├─────────────────┤
│  services/      │  ← 只做：业务规则 → 调 Repository
├─────────────────┤
│  repositories/  │  ← 只做：持久化（读写文件/数据库）
├─────────────────┤
│  models/        │  ← 数据"语言"——所有层都认识 Task
└─────────────────┘
```

**为什么不能写一个文件里**：

| 真实场景 | 如果全在一个文件 | 分层后 |
|----------|-----------------|--------|
| 要加一个 `export csv` 命令 | 在 800 行代码里找在哪插入 | 新建 `commands/export.py`，注册到 main.py |
| 要把 JSON 改成 SQLite | 修改所有文件 | 只新建 `repositories/sqlite_repo.py` |
| 测试"完成任务"逻辑 | 必须启动整个应用 | 注入 MemoryRepo，单独测 TaskService |
| 新同事要加功能 | 读完 800 行才敢改 | 看目录结构就知道在哪改 |

### 1.9 Pydantic BaseModel vs Python dataclass —— 为什么选前者？

| 场景 | dataclass | Pydantic BaseModel |
|------|-----------|-------------------|
| 定义一个字段默认值 | `field(default=0)` | `Field(default=0)` |
| 校验"标题不能为空" | 手写 `__post_init__` 检查 | `Field(..., min_length=1)` |
| 校验"优先级 0-3" | 手写 `if not 0 <= p <= 3` | `Field(ge=0, le=3)` |
| 传错类型（传字符串给 int 字段） | 不报错，事后才发现 | **立即报错** |
| 序列化为字典 | `dataclasses.asdict(obj)` | `model.model_dump()` |
| 从字典反序列化 | 手写 `from_dict()` | `Model.model_validate(data)` |
| 生成 JSON Schema | 不支持 | `model.model_json_schema()` → FastAPI 用来生成 API 文档 |

**一句话**：Pydantic = dataclass + 自动校验 + 自动序列化。而且语法和 FastAPI 一模一样，学了就能复用。

### 1.10 Typer vs Click —— 为什么选前者？

两者都来自同一个作者。Typer 是新作，核心区别：

```python
# Click 写法
@click.command()
@click.argument("title")
@click.option("-d", "--description")
def add(title, description):
    ...

# Typer 写法
def add(
    title: Annotated[str, typer.Argument(help="Task title")],
    description: Annotated[str | None, typer.Option("-d")] = None,
) -> None:
    ...
```

**Typer 的优势**：
- 类型注解即参数定义——`str` 自动校验，传 `int` 的地方传了 `"abc"` 自动报错
- 和 FastAPI 路由完全一致的写法——学一个，两个地方都能写
- 内建 Rich 彩色输出支持

---

## 2. 项目结构：每个文件是干什么的

```
todolist/
│
├── pyproject.toml              # ★ 项目的"身份证"：名字、版本、依赖列表、UV 配置
├── .python-version              # UV 用：声明 Python 版本（里面就一行 3.14）
├── .env.example                 # 环境变量模板（提交 git，不含真实配置）
├── .env                         # 你的本地配置（不提交 git，每人一份）
├── .gitignore                   # 告诉 git 哪些文件不提交
├── README.md                    # 项目说明（给 Github 访客看）
│
├── todo_app/                    # ★ 主包：所有 Python 代码在这下面
│   ├── __init__.py              # 空文件，标识这是一个 Python 包
│   │
│   ├── main.py                  # ★ 程序入口：Typer 应用定义 + 全局回调（依赖组装工厂）
│   ├── config.py                # 设置类：从 .env 读配置（数据目录、语言、日志级别）
│   ├── exceptions.py            # 自定义异常：TodoError → StorageError / TaskNotFoundError
│   ├── logger.py                # 日志初始化：app.log（全量）+  error.log（只错误）
│   │
│   ├── models/                  # 领域模型 —— 系统中的"通用语言"
│   │   └── task.py              # Task 数据类 + TaskStatus 枚举 + generate_task_id()
│   │
│   ├── dto/                     # 数据传输对象 —— 层与层之间的"快递包裹"
│   │   ├── task_create.py       # 创建任务输入：title, description, priority
│   │   ├── task_update.py       # 更新任务输入：task_id + 要改的字段
│   │   └── task_response.py     # 任务输出：给命令层渲染用
│   │
│   ├── commands/                # CLI 命令层 —— 用户操作的入口
│   │   ├── add.py               # `todo add "Buy milk"`
│   │   ├── list.py              # `todo list`
│   │   ├── show.py              # `todo show TASK-0001`
│   │   ├── done.py              # `todo done TASK-0001`
│   │   ├── delete.py            # `todo delete TASK-0001`
│   │   └── edit.py              # `todo edit TASK-0001 -t "new"`
│   │
│   ├── services/                # 业务逻辑层 —— "这个功能到底做什么"
│   │   └── task_service.py      # 7 个方法：增删改查完成取消
│   │
│   ├── repositories/            # 存储层 —— "数据存哪、怎么存取"
│   │   ├── base.py              # TaskRepository 抽象接口（6 个抽象方法）
│   │   └── json_repo.py         # JSON 文件实现（读写 ~/.todo/tasks.json）
│   │
│   └── i18n/                    # 国际化 —— 中英文切换
│       ├── __init__.py          # get_texts() 工厂函数
│       ├── en.py                # 英文文本常量字典
│       └── zh.py                # 中文文本常量字典
│
├── logs/                        # 日志输出目录（.gitignore 忽略其内容）
│
└── tests/                       # 测试 —— 每个模块对应一个子目录
    ├── conftest.py              # 共享的 fixture（内存 repo、临时 JSON repo）
    ├── test_models/             # 测 Task 创建/校验/序列化/状态切换
    ├── test_repositories/       # 测 JSON 读写/损坏容错/原子写入
    ├── test_services/           # 测业务逻辑/异常传播
    └── test_commands/           # 测 CLI 输入输出（端到端）
```

---

## 3. 架构总览：一个命令的执行旅程

以 `uv run todo add "Buy milk" -p 2` 为例，看看代码是怎么流转的：

```text
终端输入: uv run todo add "Buy milk" -p 2
               │
               ▼
┌────────────────────────────────────────────────┐
│ 1. pyproject.toml [project.scripts]            │
│    把 "todo" 映射到 todo_app.main:app          │
│    → 执行 app() 函数                           │
└──────────────────┬─────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────┐
│ 2. main.py: main_callback()                    │
│    - Settings() 自动从 .env 读配置              │
│    - 创建 JsonTaskRepository                    │
│    - 创建 TaskService(repo=...) → 注入 ctx.obj   │
│    - Typer 匹配子命令 "add" → 调用 add()        │
└──────────────────┬─────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────┐
│ 3. commands/add.py: add()                      │
│    - title="Buy milk", priority=2 已自动注入    │
│    - 构造 CreateTaskDTO → Pydantic 自动校验      │
│    - 调用 service.add_task(dto)                 │
│    - 输出 "Task 'Buy milk' added (ID: TASK-0001)"│
│    【这层不做任何业务逻辑】                       │
└──────────────────┬─────────────────────────────┘
                   │ service.add_task(dto)
                   ▼
┌────────────────────────────────────────────────┐
│ 4. services/task_service.py: add_task()        │
│    - dto 已被 Pydantic 校验（title 非空等）      │
│    - 构造 Task(title="Buy milk", priority=2)    │
│    - 调用 repo.add(task)                       │
│    - 返回 TaskResponseDTO.from_task(task)       │
│    【这层不关心数据存哪里】                       │
└──────────────────┬─────────────────────────────┘
                   │ repo.add(task)
                   ▼
┌────────────────────────────────────────────────┐
│ 5. repositories/json_repo.py: add()            │
│    - _load_data() 读 ~/.todo/tasks.json        │
│    - 生成 id: "TASK-0001"                      │
│    - task.model_dump() → 转成 dict             │
│    - data["tasks"].append(task_dict)           │
│    - _save_data(data) → 原子写入               │
│    【这层不校验数据，不含业务逻辑】               │
└──────────────────┬─────────────────────────────┘
                   │
                   ▼
          ┌────────────────────┐
          │ ~/.todo/tasks.json │
          │ {"tasks": [{...}], │
          │  "meta": {         │
          │   "next_index": 2}}│
          └────────────────────┘
```

**回顾设计铁律**：

| 层 | 职责 | 禁止 |
|----|------|------|
| commands/ | 解析参数 → 调 Service → 输出 | 操作文件、包含业务逻辑 |
| services/ | 业务规则 → 调 Repository | 操作文件、了解存储格式 |
| repositories/ | 读写数据，实现原子性 | 校验数据、包含业务逻辑 |
| models/ | 定义数据结构 | 包含 I/O 或业务规则 |

---

## 4. 全局参数

在 `main.py` 的全局回调中定义，所有子命令共享：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--lang` | `str` | `"en"`（从 .env 读取） | 界面语言 en / zh |
| `--debug` | `bool` | `False` | 开启后控制台输出 DEBUG 日志 |

**为什么这么少**：不像之前的文件批处理程序需要 `--path`、`--filter` 等——本工具的"数据在哪"由 `.env` / `Settings` 配置，不暴露给每次命令输入。

---

## 5. 开发阶段（按此顺序编码）

> **每个阶段都遵循同一格式**：做什么 → 完成标准 → 关键代码骨架 → 为什么要这样写 → 测试方法。

### 🔹 阶段 1：项目骨架 + 数据模型 + 配置

#### 要做什么
- 用 `uv venv` + `uv add` 创建项目环境
- 在 `pyproject.toml` 中声明依赖
- 创建 `todo_app/` 包目录及其 `__init__.py`
- 用 Pydantic `BaseModel` 定义 `Task` 数据模型和 `TaskStatus` 枚举
- 用 `pydantic-settings.BaseSettings` 定义 `Settings` 配置类
- 定义 3 个自定义异常

#### 为什么这样做（概念串联）

**为什么 Task 字段这样设计**：
- `id: str = Field(default="")` —— 创建时留空，由 Repository 分配。这样生成 id 的逻辑集中在存储层，未来改格式（比如从 `TASK-0001` 改成 UUID）只改一处。
- `created_at` / `updated_at` / `completed_at` —— 三个时间戳各司其职：创建时间永远不变；更新时间每次修改都变；完成时间只在完成时记录一次。
- `status: TaskStatus` —— 用上面讲过的 Enum，确保只有合法状态。

**为什么 Settings 用 frozen=True**：配置在程序运行期间不应该被修改。`frozen=True` 让 Settings 创建后变成只读对象——如果代码不小心尝试 `settings.data_dir = Path("/elsewhere")`，Pydantic 会立刻报错。这是一种"用代码约束防止 bug"的思想。

#### 完成标准

```bash
uv sync                          # → 无错误
uv run python -c "from todo_app.models.task import Task; t = Task(title='Buy milk'); print(t.model_dump())"
# → 输出完整字典，包含 id, title, status, priority, created_at 等所有字段

uv run python -c "from todo_app.models.task import Task; Task(title='')"
# → 抛 pydantic.ValidationError（不是手写校验！Pydantic 自动拦截）

uv run python -c "from todo_app.config import Settings; print(Settings().data_file)"
# → 输出 /Users/xxx/.todo/tasks.json (Path 对象)

uv run python -c "from todo_app.exceptions import TaskNotFoundError; raise TaskNotFoundError('TASK-0001')"
# → 正常抛异常并显示 "Task 'TASK-0001' not found."
```

#### 关键函数骨架

```python
# ── models/task.py ──
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum

class TaskStatus(str, Enum):
    """
    任务状态枚举。

    str 基类让 JSON 序列化输出 "pending" 而非 TaskStatus.PENDING
    """
    PENDING = "pending"          # 未完成 — 任务的初始状态
    COMPLETED = "completed"      # 已完成 — 用户标记后

class Task(BaseModel):
    """
    一个待办任务。

    Pydantic 的作用：
    - Field(min_length=1) → 自动校验标题非空（不需要手写 if-raise）
    - Field(ge=0, le=3) → 自动校验优先级范围
    - model_dump() / model_validate() → 自动序列化/反序列化
    """
    id: str = Field(default="", description="由 Repository 持久化时分配，创建时可为空")
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: int = Field(default=0, ge=0, le=3)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: str | None = Field(default=None)

    # METHOD: mark_completed() → None
    # 同时修改三个字段：status → COMPLETED, completed_at → now, updated_at → now

    # METHOD: mark_pending() → None
    # 同时修改三个字段：status → PENDING, completed_at → None, updated_at → now


# FUNCTION: generate_task_id(index: int) → str
# 用 f"TASK-{index:04d}" 生成 TASK-0001 格式


# ── config.py ──
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    全局配置。不可变对象（frozen=True）。

    读取优先级：环境变量 > .env 文件 > 默认值。
    例如 .env 里写 TODO_LANG=zh，则 Settings().language → "zh"
    """
    model_config = SettingsConfigDict(
        env_prefix="TODO_",  # 自动匹配以 TODO_ 开头的环境变量
        env_file=".env",
        extra="ignore",      # .env 中多余的键不报错
        frozen=True,         # 创建后只读
    )
    data_dir: Path = Path.home() / ".todo"
    language: str = "en"
    log_level: str = "INFO"

    @property
    def data_file(self) -> Path:
        """数据文件完整路径。@property 不受 frozen=True 限制。"""
        return self.data_dir / "tasks.json"


# ── exceptions.py ──
class TodoError(Exception):
    """所有自定义异常的基类。捕获时可以 catch TodoError 兜底。"""

class StorageError(TodoError):
    """JSON 读写失败（文件损坏、磁盘满、权限不足等）。"""

class TaskNotFoundError(TodoError):
    """按 ID 查找任务时不存在。携带 task_id 便于日志追查。"""
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task '{task_id}' not found.")
```

#### 测试方法

```bash
uv run python -c "
from todo_app.models.task import Task, TaskStatus
t = Task(title='Buy milk')
print(t.model_dump())          # 查看完整字典
t.mark_completed()
print(t.status)                # → TaskStatus.COMPLETED
print(t.completed_at)          # → 有值了！
"
uv run python -c "from todo_app.config import Settings; print(Settings().data_file)"
```

---

### 🔹 阶段 2：存储接口（ABC）+ 内存实现

#### 要做什么
- 在 `repositories/base.py` 中定义 `TaskRepository` 抽象接口（ABC）：6 个方法签名
- 实现 `MemoryTaskRepository`：用 Python 列表存数据，用于快速验证逻辑

#### 为什么这样做

**为什么需要 ABC（抽象基类）**：ABC 就是"合同"——它规定继承者必须实现哪些方法。如果你写 `class NewRepo(TaskRepository)` 但忘了实现 `get_all()`，Python 在实例化时直接报 `TypeError`，不会等到运行时才发现。这就是"用代码约束防止遗漏"。

**为什么先做内存版而非直接写 JSON**：分两步走。先把"增删改查逻辑对不对"验证清楚（内存版，几秒写完），再处理"文件 I/O 的各种异常情况"（JSON 版，更复杂）。如果合在一起，出了问题你不知道是逻辑错还是 I/O 错。

**接口的 6 个方法为什么这样定**：它们是 CRUD（增删改查）的最小完备集——每个真实存储都必须能做的操作。`count()` 是实用方法（列表命令可能想显示"共 X 条"）。没有加"批量操作"是因为当前不需要——接口要小而精，需要时再加，这叫接口隔离原则。

#### 完成标准

```python
from todo_app.repositories.memory_repo import MemoryTaskRepository
from todo_app.models.task import Task

repo = MemoryTaskRepository()
t = repo.add(Task(title="Buy milk"))
# → t.id == "TASK-0001", repo.count() == 1

t2 = repo.get_by_id("TASK-0001")
# → t2 is not None, t2.title == "Buy milk"

repo.delete("TASK-0001")  # → True
repo.delete("TASK-0001")  # → False（重复删除）
# repo.update(task) 给不存在的 id → 抛 TaskNotFoundError
```

#### 关键函数骨架

```python
# ── repositories/base.py ──
from abc import ABC, abstractmethod
from todo_app.models.task import Task

class TaskRepository(ABC):
    """
    存储抽象接口 —— Service 只依赖这个接口，不依赖 JSON 或 SQLite。

    为什么用 ABC：
    - @abstractmethod 强制子类实现所有方法
    - 子类缺方法时实例化会报 TypeError（不是运行时才发现）
    """

    @abstractmethod
    def get_all(self) -> list[Task]: ...
    @abstractmethod
    def get_by_id(self, task_id: str) -> Task | None: ...
    @abstractmethod
    def add(self, task: Task) -> Task: ...
    @abstractmethod
    def update(self, task: Task) -> Task: ...
    @abstractmethod
    def delete(self, task_id: str) -> bool: ...
    @abstractmethod
    def count(self) -> int: ...


# ── repositories/memory_repo.py ──
from todo_app.repositories.base import TaskRepository
from todo_app.models.task import Task, generate_task_id
from todo_app.exceptions import TaskNotFoundError

class MemoryTaskRepository(TaskRepository):
    """
    纯内存实现 —— 仅用于跑通链路和测试。

    内部用 list[Task] 存数据，_next_id 自增生成 TASK-0001 格式 ID。
    进程重启数据丢失——这是预期行为，阶段 5 用 JSON 持久化。
    """
    # 内部: self._tasks: list[Task]  |  self._next_id: int

    # METHOD: get_all() → 按 created_at 倒序返回
    # 用 sorted(..., key=lambda t: t.created_at, reverse=True)

    # METHOD: get_by_id(task_id) → Task | None
    # 用 next((t for t in self._tasks if t.id == task_id), None)

    # METHOD: add(task) → Task
    # 若 task.id 为空 → generate_task_id(self._next_id) 自增
    # append 到 self._tasks

    # METHOD: update(task) → Task
    # 遍历找索引 → 替换 → 找不到抛 TaskNotFoundError

    # METHOD: delete(task_id) → bool
    # 列表推导式过滤 → len 对比前后变化

    # METHOD: count() → int
    # return len(self._tasks)
```

**使用到的 Python 知识**：
- `next(gen, default)` —— 从生成器取第一个值，空时返回 default。比 `for...break...else` 写 4 行简洁
- `sorted(..., key=lambda t: t.created_at, reverse=True)` —— 按任务的创建时间倒序排列

#### 测试方法

```python
from todo_app.repositories.memory_repo import MemoryTaskRepository
from todo_app.models.task import Task

repo = MemoryTaskRepository()
t = repo.add(Task(title="Hello"))
assert t.id == "TASK-0001"
assert repo.count() == 1
assert repo.get_by_id("TASK-0001") is not None
assert repo.delete("TASK-0001") is True
assert repo.delete("TASK-0001") is False  # 重复删除
```

---

### 🔹 阶段 3：DTO 层 + 业务逻辑层（Service）

#### 要做什么
- 定义 3 个 DTO：`CreateTaskDTO`、`UpdateTaskDTO`、`TaskResponseDTO`
- 实现 `TaskService` 的 7 个方法，全部通过 `TaskRepository` 接口操作数据
- Service 不做输入校验——Pydantic 已在 DTO 构造时完成

#### 为什么这样做

**CreateTaskDTO 和 UpdateTaskDTO 为什么字段不同**：
- `CreateTaskDTO` 没有 `task_id`（创建时 id 由系统分配）
- `UpdateTaskDTO` 有 `task_id`（得知道改谁）+ 所有字段可选（只改用户指定的）
- 这是"为不同场景设计不同的输入结构"——不让创建接口接收不该有的字段，也不让更新接口必须填全所有字段

**UpdateTaskDTO 中 `None` 的意思**：
- `title: str | None = None` —— None = "用户没传这个参数，别改它"
- 如果用户真的想把标题清空？传空字符串 `""`（会触发 min_length=1 报错，因为标题不能为空）
- 实现关键：Service 中调用 `dto.model_dump(exclude_none=True)` —— 只拿到用户实际传了值的字段

**TaskResponseDTO 的 `is_completed` 为什么独立存在**：
它是一个"计算字段"——不是从 `Task` 直接取的，而是从 `status == COMPLETED` 推导出来的。放在响应 DTO 里，命令层就不需要拿到 `Task` 对象判断状态了。

#### 完成标准

```python
from todo_app.repositories.memory_repo import MemoryTaskRepository
from todo_app.services.task_service import TaskService
from todo_app.dto.task_create import CreateTaskDTO
from todo_app.dto.task_update import UpdateTaskDTO
from todo_app.exceptions import TaskNotFoundError

svc = TaskService(repo=MemoryTaskRepository())

# 添加
r = svc.add_task(CreateTaskDTO(title="Test", priority=2))
assert r.title == "Test"
assert r.priority == 2
assert not r.is_completed

# 完成
r2 = svc.complete_task(r.id)
assert r2.is_completed

# 不存在 ID
try:
    svc.complete_task("NONEXIST")
except TaskNotFoundError:
    print("正确抛了异常")

# 部分更新
r3 = svc.update_task(UpdateTaskDTO(task_id=r.id, title="New Title"))
assert r3.title == "New Title"
assert r3.description == r.description  # 没传的字段没变
```

#### 关键函数骨架

```python
# ── dto/task_create.py ──
from pydantic import BaseModel, Field

class CreateTaskDTO(BaseModel):
    """
    创建任务的输入。

    校验规则（Pydantic 构造时自动执行）：
    - title: 必填，1-200 字符
    - description: 可选，最长 2000
    - priority: 可选，0-3
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: int = Field(default=0, ge=0, le=3)


# ── dto/task_update.py ──
from pydantic import BaseModel, Field

class UpdateTaskDTO(BaseModel):
    """
    更新任务的输入。

    所有字段（除 task_id）默认为 None —— 表示"不修改"。
    只有用户显式传入的字段才会被更新。
    """
    task_id: str = Field(..., min_length=1)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: int | None = Field(default=None, ge=0, le=3)


# ── dto/task_response.py ──
from pydantic import BaseModel
from todo_app.models.task import Task, TaskStatus

class TaskResponseDTO(BaseModel):
    """
    任务输出——给命令层渲染用。

    is_completed 是便捷字段：从 status 推导而来。
    命令层不需要自己判断 TaskStatus 枚举。
    """
    id: str
    title: str
    description: str | None
    status: str              # TaskStatus.value → "pending" / "completed"
    priority: int
    created_at: str
    completed_at: str | None
    is_completed: bool

    @classmethod
    def from_task(cls, task: Task) -> "TaskResponseDTO":
        """从领域模型构建输出 DTO。"""
        ...


# ── services/task_service.py ──
from todo_app.repositories.base import TaskRepository
from todo_app.dto.task_create import CreateTaskDTO
from todo_app.dto.task_update import UpdateTaskDTO
from todo_app.dto.task_response import TaskResponseDTO
from todo_app.exceptions import TaskNotFoundError

class TaskService:·
    """
    业务逻辑层。

    设计原则：
    - 构造函数只接受 TaskRepository 接口——不依赖具体存储
    - 所有方法的输入是 DTO，输出也是 DTO——隔离内外
    - 不写 validate_xxx() —— Pydantic 在 DTO 构造时已完成校验
    """

    def __init__(self, repo: TaskRepository):
        self.repo = repo

    # ── 7 个方法 ──

    # METHOD: add_task(dto: CreateTaskDTO) → TaskResponseDTO
    # 流程: dto → Task → repo.add → from_task

    # METHOD: list_tasks(*, include_completed=True) → list[TaskResponseDTO]
    # 流程: repo.get_all → 可选过滤 COMPLETED → [from_task]

    # METHOD: get_task_detail(task_id) → TaskResponseDTO
    # 流程: repo.get_by_id → None → raise TaskNotFoundError → from_task

    # METHOD: complete_task(task_id) → TaskResponseDTO
    # 流程: get → task.mark_completed() → repo.update → from_task

    # METHOD: uncomplete_task(task_id) → TaskResponseDTO
    # 流程: get → task.mark_pending() → repo.update → from_task

    # METHOD: delete_task(task_id) → bool
    # 流程: repo.delete → False → raise TaskNotFoundError

    # METHOD: update_task(dto: UpdateTaskDTO) → TaskResponseDTO
    # 关键: dto.model_dump(exclude_none=True) → 只拿用户填了值的字段
    #      for field, value in updates.items():
    #          if field != "task_id": setattr(task, field, value)
    #      repo.update(task) → from_task
```

**使用到的 Python 知识**：
- `setattr(obj, "attr_name", value)` —— 动态设置对象属性，等价于 `obj.attr_name = value`。这样写能用一个循环处理所有字段的更新，不用逐个 if-else
- `model_dump(exclude_none=True)` —— Pydantic 方法，只导出非 None 字段

#### 测试方法

```python
from todo_app.repositories.memory_repo import MemoryTaskRepository
from todo_app.services.task_service import TaskService
from todo_app.dto.task_create import CreateTaskDTO

svc = TaskService(MemoryTaskRepository())
r = svc.add_task(CreateTaskDTO(title="Test"))
assert r.title == "Test"
assert not r.is_completed
```

---

### 🔹 阶段 4：命令行框架 + add / list 命令 + 国际化初始化

#### 要做什么
- 创建 `main.py`：Typer 应用 + 全局回调做依赖注入
- 实现 `commands/add.py`（纯文本输出）
- 实现 `commands/list.py`（纯文本输出，阶段 6 用 Rich 重写）
- 创建 `i18n/en.py`（英文文本常量）
- 通过 `--lang` 全局参数实现语言切换机制（中文翻译在阶段 8 补全）

#### 为什么这样做

**为什么用全局回调做依赖注入**：`@app.callback` 是 Typer 中"所有子命令执行前都会先运行"的函数。在这里创建 Settings → Repository → Service 并塞进 `ctx.obj`，每个子命令函数就能直接从 `ctx.obj["service"]` 取出 Service。这样做的好处：
- 组件的创建集中在一处（需要替换 JSON/SQLite 时只改这里）
- 子命令函数不需要知道自己用的是哪种 Repository
- 测试时 `CliRunner` 可以覆盖 `ctx.obj` 注入 Mock

**为什么用 `ctx.obj` 这个字典而非全局变量**：
全局变量在测试时会被污染（多个测试共享）。`ctx.obj` 是每个 Typer 调用的独立上下文，测试隔离。

**为什么用 Annotated 语法**：
`Annotated[str, typer.Argument(help="...")]` 告诉 Typer：这是一个字符串类型的**位置参数**，帮助文本是 "..."。`Annotated[int, typer.Option("-p", min=0, max=3)]` 告诉 Typer：这是一个整数类型的**可选参数**，短参数名 `-p`，范围 0-3。传了非整数（比如 `-p abc`）Typer 会自动报错。

#### 完成标准

```bash
uv run todo --help
# → 显示所有命令和全局参数

uv run todo add "Buy milk"
# → Task 'Buy milk' added (ID: TASK-0001)

uv run todo add ""
# → Error: title — String should have at least 1 character（Pydantic 自动拦截）

uv run todo add "Another" -d "Some description" -p 3
uv run todo list
# → 列出两条：TASK-0001 [ ] Buy milk
#            TASK-0002 [ ] Another
```

#### 关键函数骨架

```python
# ── main.py ──
import typer
from typing import Annotated
from todo_app.config import Settings
from todo_app.i18n import get_texts
from todo_app.repositories.memory_repo import MemoryTaskRepository
from todo_app.services.task_service import TaskService

# Typer 应用 — 无参数运行自动显示帮助
app = typer.Typer(
    name="todo",
    help="Todo CLI — Manage your tasks from the terminal.",
    no_args_is_help=True,
)

@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    lang: Annotated[str, typer.Option("--lang", help="Language (en/zh)")] = "en",
    debug: Annotated[bool, typer.Option("--debug", help="Debug mode")] = False,
) -> None:
    """
    全局回调 — 所有子命令执行前运行。

    "依赖组装工厂"：
    1. 读配置（Settings 自动读 .env）
    2. 创建存储（阶段 5 换成 JsonTaskRepository）
    3. 创建服务
    4. 注入 Typer 上下文 → 命令函数通过 ctx.obj 获取
    """
    settings = Settings()
    effective_lang = lang if lang != "en" else settings.language

    ctx.ensure_object(dict)
    ctx.obj["service"] = TaskService(repo=MemoryTaskRepository())  # 阶段 5 换 JSON
    ctx.obj["texts"] = get_texts(effective_lang)

# 注册子命令 — Typer 显式注册风格
from todo_app.commands.add import add as add_cmd
from todo_app.commands.list import list_tasks as list_cmd

app.command(name="add")(add_cmd)
app.command(name="list")(list_cmd)

if __name__ == "__main__":
    app()


# ── commands/add.py ──
import typer
from typing import Annotated
from pydantic import ValidationError as PydanticError
from todo_app.dto.task_create import CreateTaskDTO
from todo_app.exceptions import StorageError

def add(
    ctx: typer.Context,
    title: Annotated[str, typer.Argument(help="Task title")],
    description: Annotated[str | None, typer.Option("-d", "--description")] = None,
    priority: Annotated[int, typer.Option("-p", "--priority", min=0, max=3)] = 0,
) -> None:
    """添加新任务。

    示例:
        todo add "Buy milk"
        todo add "Report" -d "Due Friday" -p 2
    """
    service = ctx.obj["service"]
    t = ctx.obj["texts"]

    try:
        # CreateTaskDTO 构造时 Pydantic 自动校验
        dto = CreateTaskDTO(title=title, description=description, priority=priority)
        result = service.add_task(dto)
        typer.echo(t["task"]["added"].format(title=result.title, id=result.id))
    except PydanticError as e:
        # Pydantic 校验失败 → 从 e.errors() 提取具体字段和原因
        for err in e.errors():
            field = ".".join(str(x) for x in err["loc"])
            typer.secho(f"Error: {field} — {err['msg']}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except StorageError:
        typer.secho(t["error"]["storage"], fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


# ── commands/list.py（纯文本版，阶段 6 用 Rich 重写）──
def list_tasks(
    ctx: typer.Context,
    show_all: Annotated[bool, typer.Option("-a", "--all")] = False,
) -> None:
    """列出任务。默认隐藏已完成的。"""
    service = ctx.obj["service"]
    t = ctx.obj["texts"]

    try:
        tasks = service.list_tasks(include_completed=show_all)
    except StorageError:
        typer.secho(t["error"]["storage"], fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not tasks:
        typer.echo(t["prompt"]["no_tasks"])
        return

    for task in tasks:
        icon = t["status"]["done"] if task.is_completed else t["status"]["pending"]
        typer.echo(f"  {task.id}  {icon}  {task.title}")
```
**注意**：函数名是 `list_tasks` 而不是 `list`——避免覆盖 Python 内置的 `list` 类型。通过 `app.command(name="list")(list_tasks)` 让 CLI 命令名保持 `list`。

```python
# ── i18n/en.py ──
TEXTS = {
    "task": {
        "added": "Task '{title}' added (ID: {id})",
        "completed": "Task {id} marked as done.",
        "reopened": "Task {id} reopened.",
        "deleted": "Task {id} deleted.",
        "updated": "Task {id} updated.",
    },
    "error": {
        "storage": "Data file error. Check logs/ for details.",
        "not_found": "Task {id} not found.",
    },
    "status": {"pending": "[ ]", "done": "[✓]"},
    "prompt": {
        "no_tasks": "No tasks yet. Use 'todo add' to create one.",
        "confirm_delete": "Delete task {id}?",
    },
    "table": {
        "header_id": "ID",
        "header_title": "Title",
        "header_status": "Status",
    },
}

# ── i18n/__init__.py ──
from . import en

_LANG_MAP = {"en": en.TEXTS}   # zh 在阶段 8 加入

def get_texts(lang: str) -> dict:
    """根据语言代码返回对应的文本字典。未知语言回退英文。"""
    return _LANG_MAP.get(lang, en.TEXTS)
```

**国际化设计的要点**：
- 所有用户可见文字都从 `TEXTS` 字典取值，不硬编码在命令函数中
- `TEXTS` 的 key 结构是嵌套字典（`task.added`、`error.storage` 等），按功能域分，后期加语言不会混乱
- `"Task '{title}' added (ID: {id})"` 中的 `{title}` 和 `{id}` 是 Python 的 `str.format()` 占位符

#### 测试方法

```bash
uv run todo --help                  # 帮助信息
uv run todo add "Buy milk"         # 添加
uv run todo add ""                 # 空标题 → 报错
uv run todo add "Another" -d "desc" -p 2
uv run todo list                   # 两条
```

---

### 🔹 阶段 5：JSON 持久化

#### 要做什么
- 实现 `JsonTaskRepository`：继承 `TaskRepository`，读写 `~/.todo/tasks.json`
- JSON 内部结构：`{"tasks": [...], "meta": {"next_index": 5}}`
- 原子写入（写临时文件 → 重命名 → 清理）
- JSON 损坏容错
- `main.py` 中将 MemoryRepo 替换为 JsonRepo

#### 为什么这样做

**JSON 为什么分 tasks 和 meta**：
- `tasks`：存任务数组
- `meta.next_index`：存下一个要用的序号。如果只靠 `len(tasks)` 推算，删除任务后序号会重复——任务 ID 应该是唯一且递增的

**什么是原子写入，为什么需要**：如果直接 `open(file, "w").write(data)` 然后中途断电，你的数据文件就只剩半截 JSON。原子写入的步骤：
1. 写数据到临时文件 `tasks.json.tmp`
2. `shutil.move(tmp, real)` —— 同一文件系统上的 move 是原子操作（直接改文件名指针，不会出现"写了一半"的状态）
3. finally 清理残留临时文件

**JSON 损坏容错为什么重要**：用户可能手动编辑了 JSON、磁盘出问题、不是所有场景你都控制得了。`_load_data()` 中捕获 `FileNotFoundError`（首次运行）和 `JSONDecodeError`（文件坏了），返回空结构，记录警告日志。程序不崩溃比"完美恢复数据"更重要。

#### 完成标准

```bash
uv run todo add "Persist test"
cat ~/.todo/tasks.json               # → 看到完整 JSON 结构
# 关掉终端，重新打开
uv run todo list                     # → 数据还在
# 破坏文件
echo "garbage" > ~/.todo/tasks.json
uv run todo list                     # → 不崩溃，显示 "No tasks yet"
```

#### 关键函数骨架

```python
# ── repositories/json_repo.py ──
import json, tempfile, shutil
from pathlib import Path
from todo_app.repositories.base import TaskRepository
from todo_app.models.task import Task, generate_task_id
from todo_app.exceptions import StorageError, TaskNotFoundError
from todo_app.logger import get_logger

logger = get_logger(__name__)

class JsonTaskRepository(TaskRepository):
    """
    JSON 文件持久化。

    内部文件结构:
        {"tasks": [{task_dict}, ...], "meta": {"next_index": 5}}

    为什么 _load_data / _save_data 是私有方法：
    - 外部只需要 get_all/add/delete 等，不需要知道 JSON 长什么样
    - 未来改成 SQLite 时，这些私有方法会被完全替换，公开方法签名不变
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    # ── 私有方法 ──

    # METHOD: _load_data() → dict
    # FileNotFoundError → 返回 {"tasks": [], "meta": {"next_index": 1}}
    # JSONDecodeError → logger.warning + 返回空结构
    # OSError → raise StorageError

    # METHOD: _save_data(data: dict) → None
    # 原子写入三步：
    #   1. tempfile.mktemp 生成临时文件名
    #   2. json.dump(data, f, indent=2, ensure_ascii=False)
    #   3. shutil.move(tmp, real)
    #   4. finally: tmp.unlink() 清理残留

    # ── 公开方法 ──

    # METHOD: get_all() → list[Task]
    # _load_data → [Task.model_validate(t) for t in data["tasks"]]
    # sorted(key=lambda t: t.created_at, reverse=True)

    # METHOD: add(task) → Task
    # _load_data → 若 task.id 为空 → generate_task_id
    # data["tasks"].append(task.model_dump())  # Pydantic 序列化
    # _save_data

    # METHOD: update(task) → Task
    # _load_data → 遍历 data["tasks"] 找匹配 id → 替换 → _save_data
    # 找不到 → TaskNotFoundError

    # METHOD: delete(task_id) → bool
    # _load_data → 过滤 → 比较长度 → _save_data

    # METHOD: count() → int
    # len(self._load_data()["tasks"])
```

**原子写入代码模板（可直接参考）**：

```python
def _save_data(self, data: dict) -> None:
    self.file_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mktemp(dir=str(self.file_path.parent), suffix=".tmp"))
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        shutil.move(str(tmp), str(self.file_path))  # 原子替换
    except OSError as e:
        logger.exception("Failed to save task data")
        raise StorageError("Could not save task data.") from e
    finally:
        if tmp.exists():
            tmp.unlink()  # 清理残留临时文件
```

**`main.py` 中的替换**（看这里理解"接口的价值"）：

```python
# 替换前（阶段 4）
ctx.obj["service"] = TaskService(repo=MemoryTaskRepository())

# 替换后（阶段 5）
from todo_app.repositories.json_repo import JsonTaskRepository
ctx.obj["service"] = TaskService(repo=JsonTaskRepository(settings.data_file))
# ↑ 只改了一行！Service 层的 7 个方法、所有命令函数，一个字没动。
# 这就是 Repository 接口的意义——换存储实现不影响业务逻辑。
```

#### 测试方法

```bash
uv run todo add "test"
cat ~/.todo/tasks.json
echo "garbage" > ~/.todo/tasks.json
uv run todo list   # 应不崩溃
```

---

### 🔹 阶段 6：Rich 表格 + show 命令

#### 要做什么
- 用 Rich `Table` 重写 `list`：固定列宽、彩色状态、长文本折叠
- 实现 `show`：用 Rich `Panel` + 内嵌表格展示详情

#### 为什么这样做

**为什么需要 Rich 而不是手动格式化**：手动对齐表格列（用 `ljust()` `rjust()`）在遇到中文、emoji、长文本时全面崩溃。Rich 的 `Table` 组件自带列宽控制、对齐、文本折叠——这些是企业级 CLI 工具（如 `docker ps`、`kubectl get pods`）的标准。

**关键参数含义**：
- `overflow="fold"` —— 超宽内容自动换行，不截断
- `no_wrap=True` —— 该列绝不换行，超出截断（适合 ID 列）
- `justify="center"` —— 列内文字居中（适合状态图标）

#### 完成标准

```bash
uv run todo add "A very long task title that should be folded in the table"
uv run todo add "Short task"
uv run todo list
# → 彩色表格，长标题折叠，[✓] 绿色 / [ ] 红色
uv run todo show TASK-0001
# → Panel 展示所有字段：标题、描述、状态、优先级、时间
```

#### 关键函数骨架

```python
# ── commands/list.py（Rich 重写版）──
from rich.console import Console
from rich.table import Table
from rich.text import Text

def list_tasks(ctx, show_all=False) -> None:
    # ... 获取 tasks，空列表处理同阶段 4 ...

    console = Console()
    table = Table(title="My Tasks", title_style="bold white")
    # add_column 关键参数：name, style, width, overflow, justify, no_wrap
    table.add_column("ID", style="cyan", width=12, no_wrap=True)
    table.add_column("Title", width=40, overflow="fold")    # 超长折叠
    table.add_column("Status", width=8, justify="center")

    for task in tasks:
        color = "green bold" if task.is_completed else "red bold"
        icon = "[✓]" if task.is_completed else "[ ]"
        table.add_row(
            task.id,
            Text(task.title, style=color, overflow="fold"),
            Text(icon, style=color),
        )

    console.print(table)


# ── commands/show.py ──
from rich.console import Console
from rich.panel import Panel
from rich.table import Table as InnerTable

def show(ctx, task_id) -> None:
    # ... 获取 task，异常处理同阶段 4 ...

    # InnerTable(show_header=False, box=None) → 无表头无边框（用于详情布局）
    inner = InnerTable(show_header=False, box=None, padding=(0, 1))
    inner.add_column("Label", style="bold cyan", width=15)
    inner.add_column("Value", style="white")
    inner.add_row("Title", task.title)
    inner.add_row("Description", task.description or "N/A")
    inner.add_row("Status", "Done" if task.is_completed else "Pending")
    inner.add_row("Priority", str(task.priority))
    inner.add_row("Created", task.created_at)
    inner.add_row("Completed", task.completed_at or "Not yet")

    # Panel 包裹内嵌表格
    console = Console()
    console.print(Panel(inner, title=f"Task {task.id}", border_style="blue"))
```

#### 测试方法

```bash
uv run todo add "A very long task title that should be folded in the table display"
uv run todo add "Short task"
uv run todo list               # 检查列对齐
uv run todo show TASK-0001     # 检查 Panel
```

---

### 🔹 阶段 7：done / delete / edit 命令

#### 要做什么
- `done`：Toggle 行为（完成 ↔ 重新打开）
- `delete`：默认 `typer.confirm()` 确认，`-f` 跳过
- `edit`：部分更新

#### 为什么这样做

**done 为什么是 Toggle**：比"只能完成"和"只能取消"更方便——一次命令在两个状态间切换，而不是两个命令。减少用户记忆负担。

**delete 为什么默认确认**：删除是不可逆操作。`typer.confirm(text, default=False)` 弹出 `y/N` 交互，默认选 N（安全默认），用户明确按 y 才执行。`-f` 参数给脚本自动化场景留后路。

**edit 的部分更新怎么实现**：`UpdateTaskDTO` 中所有字段都是 `Optional`（None = 不修改），Service 中用 `model_dump(exclude_none=True)` 只取用户实际填了值的字段，然后用 `setattr` 逐个更新。这就是为什么 DTO 的字段类型是 `str | None` —— None 不是"把标题改成空"，而是"我没传标题参数"。

#### 完成标准

```bash
uv run todo done TASK-0001         # → 标记完成
uv run todo done TASK-0001         # → 重新打开（Toggle）
uv run todo delete TASK-0001       # → y/N 确认，选 n 取消
uv run todo delete TASK-0001 -f    # → 直接删除
uv run todo edit TASK-0002 -t "New title" -p 3  # → 只改 title 和 priority
```

#### 关键函数骨架

```python
# ── commands/done.py ──
def done(ctx, task_id) -> None:
    """Toggle: 未完成 → 完成，已完成 → 重新打开。"""
    # current = service.get_task_detail(task_id)
    # if current.is_completed:
    #     service.uncomplete_task(task_id)
    # else:
    #     service.complete_task(task_id)


# ── commands/delete.py ──
import typer

def delete_task(ctx, task_id, force=False) -> None:
    """删除任务。"""
    # if not force:
    #     confirmed = typer.confirm(f"Delete {task_id}?", default=False)
    #     if not confirmed: raise typer.Abort()   # 用户取消
    # service.delete_task(task_id)

# 关键 API：
#   typer.confirm(text, default=False) → y/N 交互，返回 bool
#   typer.Abort() → 静默退出（等价 sys.exit(0)）


# ── commands/edit.py ──
from pydantic import ValidationError as PydanticError
from todo_app.dto.task_update import UpdateTaskDTO

def edit(ctx, task_id, title=None, description=None, priority=None) -> None:
    """部分更新。只改用户指定的字段。"""
    # 检查至少提供了一个修改项
    # dto = UpdateTaskDTO(task_id=..., title=..., description=..., priority=...)
    #   → Pydantic 自动校验
    # service.update_task(dto)
```

#### 测试方法

```bash
uv run todo add "Toggle test"
uv run todo done TASK-0001        # → 完成
uv run todo done TASK-0001        # → 重新打开
uv run todo delete TASK-0001      # → 按 n 取消
uv run todo delete TASK-0001 -f   # → 直接删除
uv run todo add "Edit test"
uv run todo edit TASK-0002 -t "Renamed" -p 3
uv run todo show TASK-0002        # → 验证
```

---

### 🔹 阶段 8：日志 + 国际化中文 + 错误处理收尾

#### 要做什么
- 实现 `logger.py`：`RotatingFileHandler` 按大小轮转
- 补充 `i18n/zh.py`：翻译所有 key
- `main.py` 回调中接入日志
- 排查所有异常捕获路径

#### 为什么这样做

**为什么需要 RotatingFileHandler**：`app.log` 不加限制会无限增长到几 GB。`maxBytes=10*1024*1024`（10MB）告诉它：超过 10MB 就把当前日志重命名为 `app.log.1`，新建一个 `app.log`。`backupCount=5` 确保只保留 5 个备份。这是生产环境的标准做法。

**为什么日志分两个文件**：`app.log` 记录所有级别（DEBUG+），方便排查问题；`error.log` 只记录 ERROR+，运维时一眼就能看到"有没有出错"。这是"日志分级存储"的标准模式。

#### 完成标准

```bash
uv run todo --debug add "test"    # 控制台输出 DEBUG 日志
ls logs/                          # → app.log + error.log
uv run todo --lang zh list        # → 全中文界面
# 任何文件 I/O 失败不崩溃，错误写入 error.log
```

#### 关键函数骨架

```python
# ── logger.py ──
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")

def setup_logging(level: str = "INFO") -> None:
    """初始化日志。

    三个 handler（级别从低到高）：
    - DEBUG    详细的诊断信息（--debug 开启）
    - INFO     关键操作记录（添加、删除等）
    - WARNING  可恢复的问题（JSON 损坏回退）
    - ERROR    操作失败

    输出目标：
    - app_handler  → logs/app.log   (DEBUG+, 10MB × 5)
    - err_handler  → logs/error.log (ERROR+, 10MB × 5)
    - console      → stderr (WARNING+, --debug 时 DEBUG+)
    """
    LOG_DIR.mkdir(exist_ok=True)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # RotatingFileHandler(path, maxBytes=10*1024*1024, backupCount=5)
    # ... 配置三个 handler，设置 level + 格式 + 加入 root logger

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


# ── i18n/zh.py ──
TEXTS = {
    "task": {
        "added": "任务「{title}」已添加 (ID: {id})",
        "completed": "任务 {id} 已完成。",
        "reopened": "任务 {id} 已重新打开。",
        "deleted": "任务 {id} 已删除。",
        "updated": "任务 {id} 已更新。",
    },
    "error": {
        "storage": "数据文件错误，请查看 logs/ 目录。",
        "not_found": "未找到任务 {id}。",
    },
    "status": {"pending": "[ ]", "done": "[✓]"},
    "prompt": {
        "no_tasks": "暂无任务，使用 'todo add' 添加一个。",
        "confirm_delete": "确认删除任务 {id}？",
    },
    "table": {
        "header_id": "编号",
        "header_title": "标题",
        "header_status": "状态",
    },
}


# ── i18n/__init__.py（更新）──
from . import en, zh

_LANG_MAP = {"en": en.TEXTS, "zh": zh.TEXTS}

def get_texts(lang: str) -> dict:
    return _LANG_MAP.get(lang, en.TEXTS)


# ── main.py 回调中加入日志 ──
@app.callback(invoke_without_command=True)
def main_callback(ctx, lang, debug):
    setup_logging("DEBUG" if debug else settings.log_level)
    logger.info("Todo CLI starting (lang=%s, debug=%s)", effective_lang, debug)
    # ... 其余不变
```

#### 测试方法

```bash
uv run todo --debug add "test"    # 控制台有 DEBUG 输出
cat logs/app.log                  # 有操作记录
cat logs/error.log                # 为空（没出错）
uv run todo --lang zh add "测试"   # 中文输出
uv run todo --lang zh list         # 中文表头
```

---

### 🔹 阶段 9：测试覆盖

#### 要做什么
- Task 模型测试：序列化往返、空标题拦截、状态切换
- JsonTaskRepository 测试：CRUD + JSON 损坏容错
- TaskService 测试：业务逻辑 + 异常传播
- CLI 端到端测试：Typer CliRunner

#### 为什么这样做

**为什么要分层测试**：
- 模型测试不依赖文件系统——跑得飞快（毫秒级）
- Service 测试用 `MemoryTaskRepository`——不依赖文件，隔离可控
- Repository 测试用 `tmp_path`——真实文件 I/O 但每个测试独享临时文件
- CLI 测试用 `CliRunner`——不启动真实终端，验证输入输出

**覆盖率看什么不看什么**：不看数字（覆盖率 100% 不代表测得好），看关键路径——增删改查每个操作的主流程 + 异常路径（空标题、不存在 ID、文件损坏）。

#### 关键代码骨架

```python
# ── tests/conftest.py ──
import pytest
from pathlib import Path
from todo_app.repositories.memory_repo import MemoryTaskRepository
from todo_app.repositories.json_repo import JsonTaskRepository
from todo_app.services.task_service import TaskService

@pytest.fixture
def memory_repo():
    """Service 层测试用——不依赖文件系统。"""
    return MemoryTaskRepository()

@pytest.fixture
def json_repo(tmp_path: Path):
    """Repo 层测试用——tmp_path 是 pytest 内置 fixture，自动创建+清理。"""
    return JsonTaskRepository(tmp_path / "test.json")

@pytest.fixture
def service(memory_repo):
    """注入内存 repo 的 Service——隔离存储，只测业务逻辑。"""
    return TaskService(repo=memory_repo)


# ── tests/test_models/test_task.py ──
import pytest
from pydantic import ValidationError as PydanticError
from todo_app.models.task import Task, TaskStatus

def test_empty_title_blocked():
    """Pydantic 自动拦截空标题——不需要手写校验。"""
    with pytest.raises(PydanticError):
        Task(title="")

def test_model_dump_roundtrip():
    """序列化 → 反序列化往返一致。"""
    original = Task(title="Buy milk", priority=2)
    restored = Task.model_validate(original.model_dump())
    assert restored.title == "Buy milk"
    assert restored.priority == 2

def test_mark_completed():
    """完成操作同时更新 status + completed_at。"""
    task = Task(title="Test")
    task.mark_completed()
    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None


# ── tests/test_repositories/test_json_repo.py ──
def test_add_and_get(json_repo):
    task = json_repo.add(Task(title="Hello"))
    assert task.id == "TASK-0001"
    assert json_repo.count() == 1

def test_corrupted_json_safe(json_repo):
    """手动破坏 JSON → 不崩溃，返回空列表。"""
    json_repo.file_path.write_text("garbage{{{", encoding="utf-8")
    assert json_repo.get_all() == []


# ── tests/test_services/test_task_service.py ──
from todo_app.dto.task_create import CreateTaskDTO
from todo_app.exceptions import TaskNotFoundError

def test_add_and_complete(service):
    r = service.add_task(CreateTaskDTO(title="Test"))
    assert not r.is_completed
    r2 = service.complete_task(r.id)
    assert r2.is_completed

def test_complete_nonexistent(service):
    with pytest.raises(TaskNotFoundError):
        service.complete_task("NONEXIST")


# ── tests/test_commands/test_add.py ──
from typer.testing import CliRunner
from todo_app.main import app

runner = CliRunner()

def test_add_and_list(tmp_path):
    """端到端：用环境变量指向临时目录，验证完整流程。"""
    env = {"TODO_DATA_DIR": str(tmp_path)}
    r = runner.invoke(app, ["add", "Test task"], env=env)
    assert r.exit_code == 0
    assert "Test task" in r.stdout
    # 验证持久化
    r2 = runner.invoke(app, ["list"], env=env)
    assert "Test task" in r2.stdout

def test_empty_title_rejected(tmp_path):
    r = runner.invoke(app, ["add", ""], env={"TODO_DATA_DIR": str(tmp_path)})
    assert r.exit_code != 0
```

#### 测试方法

```bash
uv run pytest -v
# 理想输出：XX passed in X.XXs
```

---

## 6. 测试策略

| 测试层级 | 测什么 | 用什么 | 速度 |
|----------|--------|--------|------|
| 模型测试 | Task 创建、校验、序列化、状态切换 | 纯 Python，无依赖 | 极快 |
| Repository 测试 | JSON CRUD、原子写入、损坏容错 | `tmp_path` 夹具 | 快 |
| Service 测试 | 业务逻辑、异常传播 | `MemoryRepo` 注入 | 极快 |
| CLI 测试 | 端到端输入输出 | `CliRunner` | 快 |

---

## 7. 常见误区

| 误区 | 为什么错 | 正确做法 |
|------|----------|----------|
| 在 Service 中手写 `validate_title()` | 双重校验——已经在 DTO 中通过 Field 校验了 | 信任 Pydantic，Service 只处理业务逻辑 |
| Pydantic 模型不用 `Field` 参数 | 把 Pydantic 当"升级版 dataclass"用，弃掉校验能力 | `Field(min_length=1, max_length=200)` |
| 命令层直接调 Repository | 绕过 Service，业务逻辑散落各处 | 命令层只调 Service |
| 把 `model_dump()` 的 dict 传给外部 | 破坏了"Repo 只返回 Task 对象"的约定 | Repo 内部用 model_dump/model_validate，外部用 Task 对象 |
| `try...except` 后 `pass` | 吞掉异常，问题无法追踪 | 记录日志 + 给用户友好提示 |
| `Settings` 不用 `frozen=True` | 配置在运行时被意外修改无法发现 | `frozen=True` 让配置只读 |
| 测试等到最后写 | 代码耦合太紧写不了 | 写完模块就写测试 |

---

> **开始编码吧！**
>
> 按阶段 1 → 9 的顺序推进。每阶段：
> 1. 阅读 **为什么这样做** 理解设计意图
> 2. 参考 **关键函数骨架** 编写代码
> 3. 执行 **测试方法** 验证功能
> 4. 跑通验收标准后再进入下一阶段
>
> 遇到不懂的概念回到第 1 节的"概念讲解"查阅。
>
> 做完这个项目，你将真正理解：分层架构、Repository 模式、依赖注入、DTO、状态机、原子操作、国际化——这些不是八股文，而是每一个能写在简历上的"真实项目经验"的核心。
