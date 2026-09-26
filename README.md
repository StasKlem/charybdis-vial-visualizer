# Charybdis Vial Visualizer

Create an interactive, self-contained HTML reference card from a Vial `.vil` export for a BastardKB Charybdis 4×6.

The visualizer reads the active macOS Universal Layout Ortho `.keylayout` file, so each key displays the character it actually types in English and Russian. It also shows layers, layer-taps, mod-taps, combos, and a compact view for quick reference.

## Requirements

- Python 3.9 or newer
- A Vial `.vil` export
- Universal Layout Ortho installed in the standard macOS location:
  `~/Library/Keyboard Layouts/Universal.bundle/Contents/Resources/Universal Layout Ortho.keylayout`

No third-party Python packages are required.

## Usage

```sh
python3 visualize_vial.py path/to/keymap.vil -o keymap.html
open keymap.html
```

To use another `.keylayout` file:

```sh
python3 visualize_vial.py path/to/keymap.vil \
  --keylayout path/to/Universal\ Layout\ Ortho.keylayout \
  -o keymap.html
```

The generated page lets you switch layers, EN/RU mode, Shift, the top row, and compact view. Selecting a key reveals its original Vial keycode. The page remains useful when JavaScript is unavailable: it includes flat reference sheets for every layer.

## Validation

```sh
python3 -m unittest discover -s . -p 'test_*.py'
```

## Scope

The visualizer supports the Charybdis 4×6 Vial matrix and ordinary keycodes, nested modifiers, layer taps, mod taps, layer switching, and combos. It does not execute macros, tap dance, firmware-defined custom keycodes, dead keys, or macOS keyboard-layout actions.

## Russian documentation

See [README.ru.md](README.ru.md).

