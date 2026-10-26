import json
from pathlib import Path
import tempfile
import unittest

from validate_translations import validate


class TranslationValidationTest(unittest.TestCase):
    def check(self, text, word="mielas", locale="en", file="words/levels/1/adjectives.json"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / file
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps([{"lt": [{"word": word}], locale: [{"word": text}]}]), encoding="utf-8")
            return validate(root)

    def test_combined_alternatives_are_rejected_in_every_language(self):
        for locale in ("en", "ru", "uk"):
            for text in ("dear, nice", "dear; nice"):
                with self.subTest(locale=locale, text=text):
                    self.assertTrue(self.check(text, locale=locale))

    def test_plain_multiword_translation_is_allowed(self):
        self.assertEqual([], self.check("here you are"))

    def test_exact_reviewed_exceptions_are_allowed(self):
        self.assertEqual([], self.check("you are (plural, polite)", "esate", file="words/levels/0/common.json"))
        for word, text in (("atvykstantis", "той, що прибуває"), ("išvykstantis", "той, що відбуває")):
            self.assertEqual([], self.check(text, word, "uk", "words/levels/2/adjectives.json"))

    def test_exception_does_not_allow_other_words_or_extra_alternatives(self):
        self.assertTrue(self.check("you are (plural, polite)"))
        self.assertTrue(self.check("you are (plural, polite), are", "esate", file="words/levels/0/common.json"))

    def test_invalid_json_and_missing_corpus_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertTrue(validate(root))
            path = root / "words/broken.json"
            path.parent.mkdir()
            path.write_text("[", encoding="utf-8")
            self.assertTrue(validate(root))


if __name__ == "__main__":
    unittest.main()
