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
