"""Reject combined translation alternatives in the word bank."""
import json
from pathlib import Path
import sys

# Exceptions identify one sense, not an entire word or language.
EXCEPTIONS = {
    ("words/levels/0/common.json", "esate", "en", "you are (plural, polite)"),
    ("words/levels/2/adjectives.json", "atvykstantis", "uk", "той, що прибуває"),
    ("words/levels/2/adjectives.json", "išvykstantis", "uk", "той, що відбуває"),
}


def validate(root):
    errors = []
    files = sorted((root / "words").rglob("*.json"))
    if not files:
        return ["No word JSON files found"]
    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            entries = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(entries, list):
                raise ValueError("expected an array of entries")
            for index, entry in enumerate(entries, 1):
                headwords = [sense["word"] for sense in entry["lt"]]
                for locale in ("en", "ru", "uk"):
                    for sense in entry.get(locale, []):
                        text = sense["word"]
                        if not isinstance(text, str) or not text.strip():
                            raise ValueError(f"entry {index}: empty or invalid translation")
                        if any(mark in text for mark in ",;"):
                            allowed = len(headwords) == 1 and (relative, headwords[0], locale, text) in EXCEPTIONS
                            if not allowed:
                                errors.append(f"{relative}: entry {index}, {headwords}, {locale}: {text!r}: split alternatives into separate objects or review an explicit exception")
        except (ValueError, KeyError, TypeError) as error:
            errors.append(f"{relative}: {error}")
    return errors


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    errors = validate(root)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        sys.exit(1)
    print("Word translation validation passed")
