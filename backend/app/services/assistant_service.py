from .nlp_service import parse_text


def parse_assistant_request(db, text: str, language: str | None = None):
    return parse_text(db, text, language)
