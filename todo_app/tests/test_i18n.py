"""Tests for the i18n language factory and dictionary parity."""
from typing import Any, cast

from todo_app.i18n import get_texts
from todo_app.i18n.en import TEXTS as EN_TEXTS
from todo_app.i18n.zh import TEXTS as ZH_TEXTS


class TestGetTexts:
    """Tests for get_texts() factory function."""

    def test_en_returns_english(self) -> None:
        texts = get_texts("en")
        assert texts is EN_TEXTS
        assert texts["task"]["added"] == "Task '{title}' added (ID: {id})"

    def test_zh_returns_chinese(self) -> None:
        texts = get_texts("zh")
        assert texts is ZH_TEXTS
        assert texts["task"]["added"] == "任务 '{title}' 已添加 (ID: {id})"

    def test_unknown_falls_back_to_english(self) -> None:
        texts = get_texts("fr")
        assert texts is EN_TEXTS

    def test_empty_string_falls_back_to_english(self) -> None:
        texts = get_texts("")
        assert texts is EN_TEXTS

    def test_returns_dict_of_dicts(self) -> None:
        texts = get_texts("en")
        assert isinstance(texts, dict)
        assert isinstance(texts["task"], dict)


class TestDictionaryParity:
    """Verify that zh.py has exactly the same keys as en.py."""

    @staticmethod
    def _all_keys(d: dict[str, Any], prefix: str = "") -> list[str]:
        """Recursively collect dotted key paths from a nested dict."""
        keys: list[str] = []
        for k, v in d.items():
            full = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.extend(
                    TestDictionaryParity._all_keys(cast(dict[str, Any], v), full)
                )
            else:
                keys.append(full)
        return keys

    def test_zh_has_all_en_keys(self) -> None:
        en_keys = set(self._all_keys(EN_TEXTS))
        zh_keys = set(self._all_keys(ZH_TEXTS))
        missing = en_keys - zh_keys
        assert not missing, f"zh.py is missing keys: {missing}"

    def test_en_has_all_zh_keys(self) -> None:
        """Ensure en.py isn't missing any keys that zh.py has."""
        en_keys = set(self._all_keys(EN_TEXTS))
        zh_keys = set(self._all_keys(ZH_TEXTS))
        extra = zh_keys - en_keys
        assert not extra, f"zh.py has extra keys (not in en.py): {extra}"

    def test_all_string_values_are_format_ready(self) -> None:
        """Verify all leaf values are valid Python format strings."""
        import string

        def check_values(d: dict[str, Any]) -> None:
            for v in d.values():
                if isinstance(v, dict):
                    check_values(cast(dict[str, Any], v))
                else:
                    string.Formatter().parse(v)

        check_values(EN_TEXTS)
        check_values(ZH_TEXTS)

    def test_zh_values_are_different_from_en(self) -> None:
        """Sanity check: Chinese strings should differ from English."""
        assert EN_TEXTS["task"]["added"] != ZH_TEXTS["task"]["added"]
        assert EN_TEXTS["error"]["storage"] != ZH_TEXTS["error"]["storage"]


class TestTextUsagePatterns:
    """Verify that text patterns are usable with the expected format keys."""

    def test_task_added_accepts_title_and_id(self) -> None:
        result = EN_TEXTS["task"]["added"].format(title="Test", id="TASK-0001")
        assert "Test" in result
        assert "TASK-0001" in result

    def test_task_deleted_accepts_title_and_id(self) -> None:
        result = EN_TEXTS["task"]["deleted"].format(title="Foo", id="TASK-0099")
        assert "Foo" in result
        assert "TASK-0099" in result

    def test_confirm_delete_accepts_title_and_id(self) -> None:
        result = EN_TEXTS["prompt"]["confirm_delete"].format(title="Bar", id="TASK-0042")
        assert "Bar" in result
        assert "TASK-0042" in result

    def test_error_not_found_accepts_id(self) -> None:
        result = EN_TEXTS["error"]["not_found"].format(id="TASK-0001")
        assert "TASK-0001" in result
