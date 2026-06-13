# 设置类：从 .env 读配置（数据目录、语言、日志级别）
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """应用配置类，从环境变量或 .env 文件加载配置项。

    配置项以 `TODO_` 为前缀，支持通过 `.env` 文件或系统环境变量覆盖默认值。
    实例创建后不可变（frozen=True），确保配置在整个应用中保持一致。

    Attributes:
        data_dir (Path): 数据存储目录的路径。默认值为用户家目录下的 `.todo` 文件夹。
            可通过环境变量 `TODO_DATA_DIR` 覆盖。
        language (str): 应用界面语言。默认为 `"en"`（英语）。可通过 `TODO_LANGUAGE` 覆盖。
        log_level (str): 日志记录级别。默认为 `"INFO"`。可通过 `TODO_LOG_LEVEL` 覆盖。

    Properties:
        data_file (Path): 只读属性，返回任务存储文件的完整路径，即 `data_dir / "tasks.json"`。

    Configuration Sources (优先级从高到低):
        1. 系统环境变量（如 `TODO_DATA_DIR=/custom/data`）
        2. `.env` 文件中的变量（需与类字段名匹配，可加前缀）
        3. 代码中定义的默认值

    Examples:
        方式一：直接使用默认配置
        >>> settings = Settings()
        >>> settings.data_dir
        PosixPath('/home/user/.todo')
        >>> settings.data_file
        PosixPath('/home/user/.todo/tasks.json')

        方式二：通过 `.env` 文件覆盖配置（文件内容示例）
        ```
        TODO_DATA_DIR=/tmp/myapp_data
        TODO_LANGUAGE=zh
        TODO_LOG_LEVEL=DEBUG
        ```

        方式三：通过系统环境变量（优先级高于 `.env`）
        ```bash
        export TODO_DATA_DIR=/custom/path
        python your_app.py
        ```

    Note:
        - 如果 `.env` 文件中存在未在 `Settings` 类中定义的变量，将被忽略（`extra="ignore"`）。
        - 由于 `frozen=True`，配置实例的字段不可修改，任何赋值尝试都会引发 `TypeError`。
    """
    model_config = SettingsConfigDict(
        env_prefix="TODO_",
        env_file=".env",
        extra="ignore",
        frozen=True
    )
    data_dir: Path = Path.home() / ".todo"
    language: str = "en"
    log_level: str = "INFO"

    @property
    def data_file(self) -> Path:
        """数据文件完整路径。@property 不受 frozen=True 限制。"""
        return self.data_dir / "tasks.json"

    