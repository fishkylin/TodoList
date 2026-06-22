"""Application settings loaded from environment variables and .env file."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from env vars / .env file.

    All fields are prefixed with ``TODO_`` and support overrides via
    environment variables or a ``.env`` file.  The instance is frozen
    after creation so configuration stays consistent across the app.

    Attributes:
        data_dir: Data storage directory.  Defaults to ``~/.todo``.
            Override with ``TODO_DATA_DIR``.
        language: UI language.  Defaults to ``"en"``.
            Override with ``TODO_LANGUAGE``.
        log_level: Logging level.  Defaults to ``"INFO"``.
            Override with ``TODO_LOG_LEVEL``.

    Properties:
        data_file: Full path to the task JSON file (``data_dir / "tasks.json"``).

    Configuration precedence (highest to lowest):
        1. Environment variables (e.g. ``TODO_DATA_DIR=/custom/path``)
        2. ``.env`` file entries
        3. Class defaults

    Examples:
        Defaults::

            >>> s = Settings()
            >>> s.data_file
            PosixPath('/home/user/.todo/tasks.json')

        Custom via ``.env``::

            TODO_DATA_DIR=/tmp/myapp_data
            TODO_LANGUAGE=zh
            TODO_LOG_LEVEL=DEBUG
    """

    model_config = SettingsConfigDict(
        env_prefix="TODO_",
        env_file=".env",
        extra="ignore",
        frozen=True,
    )

    data_dir: Path = Path.home() / ".todo"
    language: str = "en"
    log_level: str = "INFO"

    @property
    def data_file(self) -> Path:
        """Full path to ``tasks.json``.  Not affected by ``frozen=True``."""
        return self.data_dir / "tasks.json"
