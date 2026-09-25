"""Every bundled locale template must be well-formed.

Walks every locale resource file shipped with the package and asserts that
each template line expands cleanly, so malformed slots, unbalanced braces
and broken groups are caught before they reach a deployed voice assistant.
"""
import os
import unittest

from ovos_spec_tools.expansion import expand

PACKAGE_ROOT = os.path.join(os.path.dirname(__file__), "..",
                            "ovos_plugin_common_play")
EXTENSIONS = (".voc", ".intent", ".dialog", ".entity", ".rx")


def iter_template_lines():
    """Yield (path, line_number, line) for every template line in the package."""
    for dirpath, _, files in os.walk(PACKAGE_ROOT):
        if "locale" not in dirpath.split(os.sep):
            continue
        for name in sorted(files):
            if not name.endswith(EXTENSIONS):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8") as f:
                for number, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        yield path, number, line


class TestLocaleTemplates(unittest.TestCase):
    def test_templates_are_well_formed(self):
        failures = []
        checked = 0
        for path, number, line in iter_template_lines():
            checked += 1
            try:
                expand(line)
            except Exception as e:
                rel = os.path.relpath(path, PACKAGE_ROOT)
                failures.append(f"{rel}:{number}: {line!r} -> {e}")
        self.assertGreater(checked, 0, "no locale template lines found")
        self.assertEqual(failures, [],
                         "malformed locale templates:\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()


class TestNoJunkPlayWord(unittest.TestCase):
    """No Play.voc line is the junk word bork, or one word written twice.

    `bork` was a placeholder in en-US Play.voc. #215 removed it there, and the
    auto-translated locales had each carried a copy: six of the sixteen still
    shipped it, in four different capitalisations, and pl-pl shipped it with
    the final k dropped. A user saying "bork noget" matched Play in da-DK.

    da-dk also shipped `spillespil` and `startstart`, two words glued together
    rather than words.

    The rule is narrow so it cannot fire on real morphology. de-de's `starte`
    is the correct German imperative and merely begins with the English
    `start`, so a prefix rule is wrong; only an exact doubling of the whole
    token counts. A multi-word line of one repeated word is a different defect
    with its own check in ovos-localize, and is not asserted here.
    """

    def _play_voc_lines(self):
        for path, number, line in iter_template_lines():
            if os.path.basename(path) == "Play.voc":
                yield path, number, line

    def test_no_line_is_the_junk_word(self):
        for path, number, line in self._play_voc_lines():
            self.assertNotEqual(
                line.strip().casefold(), "bork",
                f"{path}:{number} ships the junk word bork")

    def test_no_line_is_one_token_written_twice(self):
        for path, number, line in self._play_voc_lines():
            token = line.strip()
            if " " in token:
                continue
            half, rest = len(token) // 2, len(token) % 2
            self.assertFalse(
                rest == 0 and half > 1
                and token[:half].casefold() == token[half:].casefold(),
                f"{path}:{number} is {token!r}, one word written twice")

