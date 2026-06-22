# get_texts() 工厂函数
from . import en

_LANG_MAP = {"en": en.TEXTS}

def get_texts(lang: str) -> dict[str, dict[str, str]]:
    """根据语言代码返回对应的文本字典。未知语言回退英文。"""
    return _LANG_MAP.get(lang, en.TEXTS)