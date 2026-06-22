"""I18n factory — returns text dict for a given language code."""
from . import en, zh

_LANG_MAP = {
    "en": en.TEXTS,
    "zh": zh.TEXTS,
}


def get_texts(lang: str) -> dict[str, dict[str, str]]:
    """Return the text dictionary for the given language code.

    Falls back to English for unknown language codes.
    """
    return _LANG_MAP.get(lang, en.TEXTS)
