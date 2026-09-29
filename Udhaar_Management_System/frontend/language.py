from language_data import TRANSLATIONS

current_language = "English"

def set_language(lang: str):
    global current_language
    if lang in TRANSLATIONS:
        current_language = lang

def get_language() -> str:
    return current_language

def t(key: str, lang: str = None) -> str:
    l = lang or current_language
    lang_dict = TRANSLATIONS.get(l, TRANSLATIONS["English"])
    return lang_dict.get(key, key)
