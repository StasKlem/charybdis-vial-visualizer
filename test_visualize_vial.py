import unittest
from pathlib import Path

from visualize_vial import Layout, build, describe


class Rendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = Layout(Path.home() / "Library/Keyboard Layouts/Universal.bundle/Contents/Resources/Universal Layout Ortho.keylayout")

    def test_brackets_both_languages(self):
        for ru in (False, True):
            for key, character in [("KC_9", "("), ("KC_0", ")"), ("LALT(KC_DOT)", "["), ("LALT(KC_SLASH)", "]"), ("LSFT(LALT(KC_DOT))", "{"), ("LSFT(LALT(KC_SLASH))", "}")]:
                self.assertEqual(describe(key, self.layout, ru)["text"], character)

    def test_ortho_outputs_are_not_us_outputs(self):
        self.assertEqual(describe("KC_7", self.layout)["text"], "?")
        self.assertEqual(describe("LSFT(KC_7)", self.layout, True)["text"], "7")
        self.assertEqual(describe("KC_COMMA", self.layout, True)["text"], "б")
        self.assertEqual(describe("KC_R", self.layout, True)["text"], "к")

    def test_holds_and_unknown_codes(self):
        self.assertEqual(describe("LT3(KC_SPACE)", self.layout)["hold"], "Удержание: SYM")
        self.assertEqual(describe("LGUI_T(KC_A)", self.layout)["hold"], "Удержание: ⌘")
        self.assertEqual(describe("LGUI(KC_C)", self.layout)["text"], "⌘C")
        self.assertEqual(describe("USER99", self.layout)["kind"], "unknown")

    def test_transparency_inherits_base(self):
        data = {"layout": [[["KC_A"] * 6 for _ in range(10)] for _ in range(4)], "combo": []}
        data["layout"][3][0][0] = "KC_TRNS"
        cell = next(cell for cell in build(data, self.layout)["views"]["00"][3] if (cell["r"], cell["c"]) == (0, 0))
        self.assertEqual(cell["text"], "a")
        self.assertEqual(cell["source"], 0)
        self.assertTrue(cell["inherited"])


if __name__ == "__main__":
    unittest.main()
