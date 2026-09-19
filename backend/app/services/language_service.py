SUPPORTED_LANGUAGES = {"en": "English", "hi": "Hindi", "te": "Telugu", "mixed": "Mixed"}


def language_label(code: str) -> str:
    return SUPPORTED_LANGUAGES.get(code, "English")
