# MutterBoard

An on-screen keyboard for Linux that aims to mimic physical keyboard behavior as closely as possible.

📘 Chinese documentation: [README.zh-CN.md](./README.zh-CN.md)

---

## Overview

MutterBoard is a GTK3 virtual keyboard that injects real key events through `uinput`. It is designed for touch devices, temporary keyboard replacement, and accessibility-oriented desktop workflows.

Compared with simpler virtual keyboards, MutterBoard focuses on:

- Modifier-key semantics
- Shortcut usability
- State synchronization (e.g., CapsLock indicator)
- Multi-touch support (independent touch point tracking)

---

## Features

- **Hardware-like modifier behavior**
  - Supports Shift/Ctrl/Alt/Super press/release handling.
  - Supports one-shot/latch behavior for modifiers (e.g., tap Shift once to lock it).
- **Shortcut friendly**
  - Combination keys can be sent to the focused window (e.g., `Ctrl+C`, `Ctrl+V`).
- **Double-Shift shortcut trigger**
  - Double tapping either Shift key emits a configurable shortcut (default: `LEFTSHIFT,SPACE`). Can be enabled/disabled via config.
- **Fast sequential taps**
  - Regular keys are emitted on press (tap-first strategy), so quick consecutive taps remain reliable even in single-pointer touch stacks (common with XWayland).
- **Global top-layer window**
  - Keeps minimize/maximize/close decorations, uses NORMAL window type (with draggable titlebar) and repeatedly raises itself with sticky + keep-above hints to reduce IME overlap risk.
- **Long-press repeat**
  - Regular keys repeat while held (delay 420ms, interval 70ms).
- **Space cursor mode**
  - Long-press Space to enter cursor mode; the key label changes to `◀ Space ▶` with a highlighted border and text.
  - Slide horizontally to send Left/Right; slide vertically to send Up/Down.
  - Trigger threshold adapts dynamically to sliding speed for more natural control.
- **CapsLock handling**
  - CapsLock key toggles internal state, sends the key event, and updates the header indicator.
  - Header indicator is a button‑style label matching other controls; it turns accent‑colored when CapsLock is on.
  - CapsLock state is saved and restored on next launch.
- **Dynamic key labels with Shift**
  - Symbol keys update labels while Shift is active (e.g., `1` → `!`).
- **Multi-touch support**
  - Each touch point is tracked independently, allowing multiple keys to be pressed simultaneously without interference.
  - Touch motion is used for Space cursor mode, enhancing the touchpad experience.
- **Customizable UI**
  - Themes: `Dark`, `Light`, `Midnight`
  - Reduced key opacity for better readability of background content when using translucent themes.
  - Hover/prelight does not alter key background opacity; only click feedback and latched states change visuals.
  - Adjustable opacity and font size from header controls.
- **Persistent settings**
  - Saves theme, opacity, font size, window size, double‑Shift shortcut, and CapsLock state.

---

## Screenshots

<img width="2414" height="849" alt="MutterBoard screenshot" src="https://github.com/user-attachments/assets/45d70608-855d-4919-b325-4c95ecbaeb11" />

---

## Dependencies

Required runtime components:

- Linux
- Python 3.9+
- GTK 3 via PyGObject (`python3-gi` / `python3-gobject`)
- `uinput` kernel module + Python binding (`python3-uinput` / `python-uinput`)

Optional but useful on some distros:

- `steam-devices` (helps input‑device permissions in some environments)

---

## Installation

### Debian / Ubuntu

```bash
sudo apt install python3-gi python3-uinput steam-devices
```

### Fedora

```bash
sudo dnf install python3-gobject python3-uinput steam-devices
```

### Arch Linux (AUR example)

```bash
yay -S python-uinput steam-devices
```

---

## Usage

```bash
python3 mutterboard.py
```

### Optional: Create desktop shortcut

```bash
mkdir -p ~/.local/share/applications/
cat > ~/.local/share/applications/mutterboard.desktop <<EOF
[Desktop Entry]
Exec=bash -c 'python3 /path/to/mutterboard.py'
Icon=preferences-desktop-keyboard
Name=MutterBoard
Terminal=false
Type=Application
Categories=Utility;
NoDisplay=false
EOF
chmod +x ~/.local/share/applications/mutterboard.desktop
```

---

## Configuration

Config file:

```text
~/.config/mutterboard/settings.conf
```

Example:

```ini
[DEFAULT]
theme = Dark
opacity = 0.96
font_size = 18
width = 0
height = 0
double_shift_shortcut_enabled = true
double_shift_shortcut = LEFTSHIFT,SPACE
capslock_on = false
```

Settings notes:

- `theme`: `Dark` / `Light` / `Midnight`
- `opacity`: clamped by app (about `0.35` to `1.0`)
- `font_size`: clamped by app (about `10` to `48`)
- `width` / `height`: persisted window size
- `double_shift_shortcut_enabled`: enable/disable double‑Shift shortcut (`true` by default)
- `double_shift_shortcut`: comma‑separated key tokens (e.g., `LEFTSHIFT,SPACE`)
- `capslock_on`: internal CapsLock state (saved automatically)

---

## Possible Issues / Troubleshooting

1. **Error: `no such device`**

   `uinput` module may not be loaded:

   ```bash
   sudo modprobe uinput
   ```

2. **Stops working after reboot**

   Enable module autoload:

   ```bash
   echo 'uinput' | sudo tee /etc/modules-load.d/uinput.conf
   ```

3. **Permission denied for key injection**

   Reload udev rules and re‑log in:

   ```bash
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```

4. **`steam-devices` package not found (Fedora, etc.)**

   Ensure related repositories are enabled (for Fedora, RPM Fusion is commonly required).

5. **Desktop/compositor compatibility differences**

   Input injection behavior may vary depending on distro, desktop environment, and compositor implementation. On XWayland in particular, multi‑touch pointer semantics can differ from native Wayland, so gesture‑style interactions may be interpreted as single‑pointer sequences.

---

## PR

Contributions are welcome.

Before opening a PR, please:

- Keep `README.md` (EN) and `README.zh-CN.md` (ZH) consistent.
- Explain motivation, behavior changes, and potential risks.
- Attach screenshots/recording for UI behavior changes.
- Update configuration/troubleshooting docs if config behavior changes.

---

## License

This project is licensed under **GNU LGPL v2.1**. See [LICENSE](./LICENSE).
