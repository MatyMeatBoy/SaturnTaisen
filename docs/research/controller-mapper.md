# Controller mapper by physical inputs

A tool independent of the game, with its own Saturn, Genesis 3, and Genesis 6 layouts. Build: `python tools/build_controller_mapper.py`; local executable at `local/build/controller-mapper/Mapear M30.exe`, with its DLLs alongside. It needs no discs, BIOS, PC resources, Python, or compilers on the machine where it's used.

The user selects the device and layout, leaves everything at rest, and presses Start. The diagram highlights each physical position. Buttons, axis halves with their rest value, and hat crosses are recorded, without assuming SDL normalization. Releasing before the next step is required; duplicate inputs and hat diagonals are rejected. Repeat/Skip let the user correct or declare missing buttons. Back/Select is a PC extra and is not presented as an original Saturn button.

Saving the report creates a JSON in a reports folder next to the EXE, with a fallback in AppData if it can't write there. It contains the layout, observed name/GUID/VID/PID, declared mode, existing SDL mapping, and actions→physical inputs. It does not send data, does not capture serial numbers, and does not apply bindings to the game. The identity is preserved if the device disconnects after completing the walkthrough, so the report is not lost.

Tests: synthetic core for layouts, release, duplicates, opposite axes, and JSON; startup/UI with no toolchain in PATH; full walkthrough with a virtual SDL joystick, four hats, and ten buttons, saving and parsing the JSON. The virtual test does not prove the M30's physical mapping: that report will be completed by the owner.

To reuse mappings, distinguish observed identity from commercial name: a generic XInput device can hide the actual model. Check the report against the exact backend/mode before switching from Auto, and respect user overrides.
