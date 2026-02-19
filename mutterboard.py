import configparser
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import gi
import uinput

os.environ.setdefault("GDK_BACKEND", "x11")

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402  # Imported after gi.require_version / 在 gi.require_version 之后导入


KEY_MAPPING: Dict[int, str] = {
    uinput.KEY_ESC: "Esc",
    uinput.KEY_1: "1",
    uinput.KEY_2: "2",
    uinput.KEY_3: "3",
    uinput.KEY_4: "4",
    uinput.KEY_5: "5",
    uinput.KEY_6: "6",
    uinput.KEY_7: "7",
    uinput.KEY_8: "8",
    uinput.KEY_9: "9",
    uinput.KEY_0: "0",
    uinput.KEY_MINUS: "-",
    uinput.KEY_EQUAL: "=",
    uinput.KEY_BACKSPACE: "Backspace",
    uinput.KEY_TAB: "Tab",
    uinput.KEY_Q: "Q",
    uinput.KEY_W: "W",
    uinput.KEY_E: "E",
    uinput.KEY_R: "R",
    uinput.KEY_T: "T",
    uinput.KEY_Y: "Y",
    uinput.KEY_U: "U",
    uinput.KEY_I: "I",
    uinput.KEY_O: "O",
    uinput.KEY_P: "P",
    uinput.KEY_LEFTBRACE: "[",
    uinput.KEY_RIGHTBRACE: "]",
    uinput.KEY_ENTER: "Enter",
    uinput.KEY_LEFTCTRL: "Ctrl_L",
    uinput.KEY_A: "A",
    uinput.KEY_S: "S",
    uinput.KEY_D: "D",
    uinput.KEY_F: "F",
    uinput.KEY_G: "G",
    uinput.KEY_H: "H",
    uinput.KEY_J: "J",
    uinput.KEY_K: "K",
    uinput.KEY_L: "L",
    uinput.KEY_SEMICOLON: ";",
    uinput.KEY_APOSTROPHE: "'",
    uinput.KEY_GRAVE: "`",
    uinput.KEY_LEFTSHIFT: "Shift_L",
    uinput.KEY_BACKSLASH: "\\",
    uinput.KEY_Z: "Z",
    uinput.KEY_X: "X",
    uinput.KEY_C: "C",
    uinput.KEY_V: "V",
    uinput.KEY_B: "B",
    uinput.KEY_N: "N",
    uinput.KEY_M: "M",
    uinput.KEY_COMMA: ",",
    uinput.KEY_DOT: ".",
    uinput.KEY_SLASH: "/",
    uinput.KEY_RIGHTSHIFT: "Shift_R",
    uinput.KEY_LEFTALT: "Alt_L",
    uinput.KEY_RIGHTALT: "Alt_R",
    uinput.KEY_SPACE: "Space",
    uinput.KEY_CAPSLOCK: "CapsLock",
    uinput.KEY_RIGHTCTRL: "Ctrl_R",
    uinput.KEY_LEFTMETA: "Super_L",
    uinput.KEY_RIGHTMETA: "Super_R",
    uinput.KEY_LEFT: "←",
    uinput.KEY_RIGHT: "→",
    uinput.KEY_UP: "↑",
    uinput.KEY_DOWN: "↓",
    uinput.KEY_HOME: "Home",
    uinput.KEY_END: "End",
}

# Reverse lookup for UI label -> linux key code / UI 标签到 Linux 键码的反向映射
LABEL_TO_KEY = {label: code for code, label in KEY_MAPPING.items()}
MODIFIER_KEYS = {
    uinput.KEY_LEFTSHIFT,
    uinput.KEY_RIGHTSHIFT,
    uinput.KEY_LEFTCTRL,
    uinput.KEY_RIGHTCTRL,
    uinput.KEY_LEFTALT,
    uinput.KEY_RIGHTALT,
    uinput.KEY_LEFTMETA,
    uinput.KEY_RIGHTMETA,
}
SHIFT_KEYS = {uinput.KEY_LEFTSHIFT, uinput.KEY_RIGHTSHIFT}

DEFAULT_LAYOUT = [
    ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
    ["CapsLock", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
    ["Shift_L", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift_R", "↑"],
    ["Ctrl_L", "Super_L", "Alt_L", "Space", "Alt_R", "Super_R", "Ctrl_R", "←", "→", "↓"],
]

KEY_WIDTHS = {
    "`": 1,
    "Space": 12,
    "CapsLock": 3,
    "Shift_L": 4,
    "Shift_R": 4,
    "Backspace": 3,
    "\\": 3,
    "Enter": 4,
}

SYMBOL_LABELS = {
    "`": "~",
    "1": "!",
    "2": "@",
    "3": "#",
    "4": "$",
    "5": "%",
    "6": "^",
    "7": "&",
    "8": "*",
    "9": "(",
    "0": ")",
    "-": "_",
    "=": "+",
    "[": "{",
    "]": "}",
    "\\": "|",
    ";": ":",
    "'": '"',
    ",": "<",
    ".": ">",
    "/": "?",
}

# Friendly config tokens accepted in settings.conf / settings.conf 中接受的简写别名
CONFIG_TOKEN_ALIASES = {
    "SHIFT": "LEFTSHIFT",
    "CTRL": "LEFTCTRL",
    "ALT": "LEFTALT",
    "SUPER": "LEFTMETA",
    "META": "LEFTMETA",
    "WIN": "LEFTMETA",
}

THEMES = {
    "Dark": {
        "bg": "22,23,28",
        "key": "54,56,66",
        "key_border": "112,115,132",
        "accent": "102,163,255",
        "text": "#F4F6FF",
    },
    "Light": {
        "bg": "245,246,250",
        "key": "255,255,255",
        "key_border": "178,186,204",
        "accent": "66,108,235",
        "text": "#151822",
    },
    "Midnight": {
        "bg": "15,18,32",
        "key": "36,44,75",
        "key_border": "89,101,150",
        "accent": "121,205,255",
        "text": "#EAF6FF",
    },
}


@dataclass
class RepeatState:
    delay_source: Optional[int] = None
    repeat_source: Optional[int] = None


@dataclass
class ModifierState:
    pressed: bool = False
    latched: bool = False
    used_in_combo: bool = False


class KeyboardEngine:
    def __init__(self) -> None:
        # Create one virtual input device with all supported keys / 创建包含全部支持键位的虚拟输入设备
        self.device = uinput.Device(list(KEY_MAPPING.keys()))
        # Track currently held keys to avoid duplicate press/release / 跟踪当前按下键，避免重复按下或抬起
        self.down_keys: Set[int] = set()

    def set_key_state(self, key_code: int, pressed: bool) -> None:
        is_down = key_code in self.down_keys
        if pressed and not is_down:
            self.device.emit(key_code, 1)
            self.down_keys.add(key_code)
        elif not pressed and is_down:
            self.device.emit(key_code, 0)
            self.down_keys.discard(key_code)

    def tap_key(self, key_code: int) -> None:
        self.device.emit(key_code, 1)
        self.device.emit(key_code, 0)


class MutterBoard(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="MutterBoard", name="toplevel")
        self._configure_window()
        self._configure_storage()

        self.engine = KeyboardEngine()
        # Runtime key-state containers / 运行期按键状态容器
        self.modifiers: Dict[int, ModifierState] = {key: ModifierState() for key in MODIFIER_KEYS}
        self.modifier_buttons: Dict[int, Gtk.Button] = {}
        self.regular_buttons: Dict[str, Gtk.Button] = {}
        self.repeat_states: Dict[int, RepeatState] = {}
        self.active_keys: Set[int] = set()
        self.space_button: Optional[Gtk.Button] = None
        self.space_button_default_label = "Space"
        self.caps_indicator_label: Optional[Gtk.Label] = None
        self.caps_sync_source: Optional[int] = None

        self.space_long_press_ms = 300
        self.space_cursor_mode = False
        self.space_long_press_source: Optional[int] = None
        self.space_last_x = 0.0
        self.space_last_y = 0.0
        self.space_last_motion_at = 0.0
        self.space_accum_x = 0.0
        self.space_accum_y = 0.0

        # Double-Shift shortcut state / Shift 双击快捷键状态
        self.last_shift_tap_at = 0.0
        self.double_shift_timeout_ms = 380
        self.double_shift_shortcut_enabled = True
        self.double_shift_shortcut = [uinput.KEY_LEFTSHIFT, uinput.KEY_SPACE]
        self.capslock_on = False

        self.theme_name = "Dark"
        self.opacity = "0.96"
        self.font_size = 18
        self.width = 0
        self.height = 0

        self._load_settings()
        self._build_ui()
        self._setup_capslock_sync()
        self._sync_capslock_from_system()
        self.apply_css()

        self.connect("configure-event", self.on_resize)
        self.connect("destroy", lambda _: self.save_settings())

    def _configure_window(self) -> None:
        self.set_border_width(0)
        self.set_resizable(True)
        self.set_keep_above(True)
        self.stick()
        # Keep normal window type so minimize/maximize controls are consistently available.
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_decorated(True)
        self.set_skip_taskbar_hint(False)
        self.set_skip_pager_hint(False)
        self.set_focus_on_map(False)
        self.set_can_focus(False)
        self.set_accept_focus(False)
        self.set_default_icon_name("preferences-desktop-keyboard")
        self.connect("realize", self._on_window_realize)

    def _configure_storage(self) -> None:
        self.config_dir = os.path.expanduser("~/.config/mutterboard")
        self.config_file = os.path.join(self.config_dir, "settings.conf")
        self.config = configparser.ConfigParser()

    def _build_ui(self) -> None:
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.set_name("root")
        self.add(root)

        self._build_header()
        self._build_keyboard(root)

    def _build_header(self) -> None:
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.set_decoration_layout(":minimize,maximize,close")
        self.set_titlebar(self.header)

        self.settings_buttons: List[Gtk.Button] = []
        self._create_header_button("☰", self.toggle_controls)
        self._create_header_button("+", self.change_opacity, True)
        self._create_header_button("-", self.change_opacity, False)
        self.opacity_btn = self._create_header_button(self.opacity)
        self._create_header_button("A+", self.change_font_size, 1)
        self._create_header_button("A-", self.change_font_size, -1)
        self.font_btn = self._create_header_button(f"{self.font_size}px")

        self.theme_combobox = Gtk.ComboBoxText()
        self.theme_combobox.append_text("Theme")
        for name in THEMES:
            self.theme_combobox.append_text(name)
        self.theme_combobox.set_active(0)
        if self.theme_name in THEMES:
            self.theme_combobox.set_active(list(THEMES.keys()).index(self.theme_name) + 1)
        self.theme_combobox.set_name("combobox")
        self.theme_combobox.connect("changed", self.change_theme)
        self.header.add(self.theme_combobox)

        # Always-visible CapsLock indicator in header; not part of collapsible controls.
        self.caps_indicator_label = Gtk.Label(label="Caps: Off")
        self.caps_indicator_label.set_name("caps-indicator")
        self.header.pack_end(self.caps_indicator_label)

    def _build_keyboard(self, parent: Gtk.Box) -> None:
        grid = Gtk.Grid()
        grid.set_name("grid")
        grid.set_row_spacing(2)
        grid.set_column_spacing(2)
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        parent.pack_start(grid, True, True, 0)

        # Normalize every row width to keep alignment / 归一化每一行宽度以保持对齐
        row_widths = [sum(KEY_WIDTHS.get(label, 2) for label in row) for row in DEFAULT_LAYOUT]
        target_width = max(row_widths)

        for row_index, row in enumerate(DEFAULT_LAYOUT):
            widths = self._balanced_row_widths(row, target_width)
            col = 0
            for label, width in zip(row, widths):
                key_code = LABEL_TO_KEY[label]
                shown = label[:-2] if label.endswith("_L") or label.endswith("_R") else label
                button = Gtk.Button(label=shown)
                button.set_name("key")
                button.get_style_context().add_class("key-button")
                button.set_can_focus(False)
                button.set_focus_on_click(False)
                button.connect("pressed", self.on_button_press, key_code)
                button.connect("released", self.on_button_release, key_code)

                if key_code == uinput.KEY_SPACE:
                    # Space key also receives pointer motion for cursor mode / Space 键额外接收指针移动用于光标模式
                    self.space_button = button
                    self.space_button_default_label = shown
                    button.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
                    button.connect("motion-notify-event", self.on_space_motion)

                grid.attach(button, col, row_index, width, 1)
                col += width

                if key_code in MODIFIER_KEYS:
                    self.modifier_buttons[key_code] = button
                else:
                    self.regular_buttons[label] = button

    def _balanced_row_widths(self, row: List[str], target_width: int) -> List[int]:
        widths = [KEY_WIDTHS.get(label, 2) for label in row]
        deficit = target_width - sum(widths)
        idx = 0
        while deficit > 0 and widths:
            widths[idx % len(widths)] += 1
            idx += 1
            deficit -= 1
        return widths

    def _setup_capslock_sync(self) -> None:
        self.keymap = Gdk.Keymap.get_default()
        if self.keymap is not None:
            self.keymap.connect("state-changed", self._on_keymap_state_changed)

    def _on_keymap_state_changed(self, _keymap: Gdk.Keymap) -> None:
        self._sync_capslock_from_system()

    def _sync_capslock_from_system(self) -> bool:
        if getattr(self, "keymap", None) is None:
            return False
        self.capslock_on = self.keymap.get_caps_lock_state()
        self._update_caps_indicator()
        return False

    def _schedule_capslock_sync(self, expected_previous: bool) -> None:
        if self.caps_sync_source is not None:
            GLib.source_remove(self.caps_sync_source)
            self.caps_sync_source = None

        attempts = {"count": 0}

        def _poll() -> bool:
            self._sync_capslock_from_system()
            attempts["count"] += 1
            if self.capslock_on != expected_previous or attempts["count"] >= 12:
                self.caps_sync_source = None
                return False
            return True

        self.caps_sync_source = GLib.timeout_add(60, _poll)

    def _create_header_button(self, label: str, callback=None, callback_arg=None) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.set_name("headbar-button")
        if callback is not None:
            if callback_arg is None:
                button.connect("clicked", callback)
            else:
                button.connect("clicked", callback, callback_arg)
        self.header.add(button)
        self.settings_buttons.append(button)
        return button

    def _theme(self) -> Dict[str, str]:
        return THEMES.get(self.theme_name, THEMES["Dark"])

    def apply_css(self) -> None:
        theme = self._theme()
        provider = Gtk.CssProvider()
        css = f"""
        #toplevel {{ background-color: rgba({theme['bg']}, {self.opacity}); }}
        #root {{ background-color: rgba({theme['bg']}, {self.opacity}); margin: 0; padding: 0; }}
        headerbar {{
            background-color: rgba({theme['bg']}, {self.opacity});
            border: 0;
            box-shadow: none;
            min-height: 54px;
        }}
        headerbar button {{
            background-image: none;
            background-color: rgba({theme['key']}, 0.72);
            border: 1px solid rgba({theme['key_border']}, 0.88);
            min-height: 46px;
            min-width: 52px;
            border-radius: 8px;
        }}
        headerbar .titlebutton {{
            min-width: 56px;
            min-height: 46px;
            background-color: rgba({theme['key']}, 0.72);
        }}
        #combobox button.combo {{
            background-image: none;
            background-color: rgba({theme['key']}, 0.72);
            border: 1px solid rgba({theme['key_border']}, 0.88);
            min-height: 46px;
            min-width: 90px;
            border-radius: 8px;
        }}
        headerbar button label, #combobox button.combo label {{
            color: {theme['text']};
            font-size: {max(self.font_size - 1, 12)}px;
            font-weight: 600;
        }}
        #grid {{ margin: 0; padding: 0; }}
        .key-button,
        button.key-button,
        .key-button:hover,
        button.key-button:hover,
        .key-button:focus,
        button.key-button:focus,
        .key-button:checked,
        button.key-button:checked,
        .key-button:active,
        button.key-button:active,
        .key-button:backdrop {{
            border-radius: 8px;
            border: 1px solid rgba({theme['key_border']}, 0.9);
            background-image: none;
            background-color: rgba({theme['key']}, 0.82);
            box-shadow: none;
            outline: none;
            min-height: 48px;
            margin: 0;
            padding: 0;
        }}
        .key-button label {{ color: {theme['text']}; font-weight: 600; font-size: {self.font_size}px; }}
        #caps-indicator {{
            color: {theme['text']};
            font-size: {max(self.font_size - 2, 11)}px;
            font-weight: 700;
            padding: 0 8px;
        }}
        #caps-indicator.on {{ color: rgba({theme['accent']}, 1.0); }}
        .key-button.pressed,
        .key-button.pressed:hover,
        .key-button.pressed:focus,
        .key-button.pressed:active {{
            background-color: rgba({theme['accent']}, 0.28);
            border-color: rgba({theme['accent']}, 1.0);
        }}
        .key-button.cursor-mode {{
            background-color: rgba({theme['accent']}, 0.24);
            border-color: rgba({theme['accent']}, 1.0);
        }}
        .key-button.cursor-mode label {{
            color: rgba({theme['accent']}, 1.0);
            font-weight: 700;
        }}
        """
        provider.load_from_data(css.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def toggle_controls(self, _button=None) -> None:
        for button in self.settings_buttons:
            if button.get_label() != "☰":
                button.set_visible(not button.get_visible())
        self.theme_combobox.set_visible(not self.theme_combobox.get_visible())

    def change_opacity(self, _button, increase: bool) -> None:
        delta = 0.02 if increase else -0.02
        self.opacity = str(round(min(1.0, max(0.35, float(self.opacity) + delta)), 2))
        self.opacity_btn.set_label(self.opacity)
        self.apply_css()

    def change_font_size(self, _button, delta: int) -> None:
        self.font_size = min(48, max(10, self.font_size + delta * 2))
        self.font_btn.set_label(f"{self.font_size}px")
        self.apply_css()

    def change_theme(self, _widget) -> None:
        selected = self.theme_combobox.get_active_text()
        if selected in THEMES:
            self.theme_name = selected
            self.apply_css()

    def _update_caps_indicator(self) -> None:
        indicator = self.caps_indicator_label
        if indicator is None:
            return
        indicator.set_text("Caps: On" if self.capslock_on else "Caps: Off")
        style = indicator.get_style_context()
        if self.capslock_on:
            style.add_class("on")
        else:
            style.remove_class("on")

    def on_button_press(self, widget: Gtk.Button, key_code: int) -> None:
        self.active_keys.add(key_code)

        if key_code == uinput.KEY_CAPSLOCK:
            self._flash_regular_key(widget)
            self.engine.tap_key(uinput.KEY_CAPSLOCK)
            # Poll keymap state for a short period to avoid transient indicator flicker.
            self._schedule_capslock_sync(self.capslock_on)
            return

        if key_code in MODIFIER_KEYS:
            self._paint_pressed(widget, True)
            self._on_modifier_press(key_code)
            self._update_shift_labels()
            return

        if key_code == uinput.KEY_SPACE:
            self._paint_pressed(widget, True)
            self._begin_space_tracking()
            return

        for state in self.modifiers.values():
            if state.pressed:
                state.used_in_combo = True

        # Emit normal key immediately on press. This is more robust on environments
        # where touch is effectively single-pointer (common under XWayland), because
        # output no longer depends on receiving a second concurrent touch release.
        self._flash_regular_key(widget)
        self.engine.tap_key(key_code)
        self._start_repeat(key_code)

    def on_button_release(self, widget: Gtk.Button, key_code: int) -> None:
        self.active_keys.discard(key_code)
        if key_code in MODIFIER_KEYS or key_code == uinput.KEY_SPACE:
            self._paint_pressed(widget, False)

        if key_code == uinput.KEY_CAPSLOCK:
            return

        if key_code in MODIFIER_KEYS:
            self._on_modifier_release(key_code)
            self._update_shift_labels()
            return

        if key_code == uinput.KEY_SPACE:
            self._finish_space_tracking()
            self._release_one_shot_modifiers()
            self._update_shift_labels()
            return

        self._cancel_repeat(key_code)
        self._release_one_shot_modifiers()
        self._update_shift_labels()

    def _on_modifier_press(self, key_code: int) -> None:
        state = self.modifiers[key_code]
        state.pressed = True
        state.used_in_combo = False

        if key_code in SHIFT_KEYS:
            opposite = uinput.KEY_RIGHTSHIFT if key_code == uinput.KEY_LEFTSHIFT else uinput.KEY_LEFTSHIFT
            self._force_release_modifier(opposite)

        self.engine.set_key_state(key_code, True)
        self._paint_modifier(key_code, True)

    def _on_modifier_release(self, key_code: int) -> None:
        state = self.modifiers[key_code]
        state.pressed = False

        if state.used_in_combo:
            if not state.latched:
                self.engine.set_key_state(key_code, False)
                self._paint_modifier(key_code, False)
            state.used_in_combo = False
            return

        if state.latched:
            state.latched = False
            self.engine.set_key_state(key_code, False)
            self._paint_modifier(key_code, False)
        else:
            state.latched = True
            self._paint_modifier(key_code, True)

        if key_code in SHIFT_KEYS:
            self._handle_shift_double_tap()

    def _release_one_shot_modifiers(self) -> None:
        for key_code, state in self.modifiers.items():
            if state.latched and not state.pressed:
                state.latched = False
                self.engine.set_key_state(key_code, False)
                self._paint_modifier(key_code, False)

    def _handle_shift_double_tap(self) -> None:
        if not self.double_shift_shortcut_enabled:
            self.last_shift_tap_at = 0.0
            return

        now = time.monotonic()
        elapsed_ms = (now - self.last_shift_tap_at) * 1000
        if self.last_shift_tap_at > 0 and elapsed_ms <= self.double_shift_timeout_ms:
            for shift_key in SHIFT_KEYS:
                self._force_release_modifier(shift_key)
            self._emit_shortcut(self.double_shift_shortcut)
            self.last_shift_tap_at = 0.0
            return
        self.last_shift_tap_at = now

    def _emit_shortcut(self, combo: List[int]) -> None:
        mods = [code for code in combo if code in MODIFIER_KEYS]
        normals = [code for code in combo if code not in MODIFIER_KEYS]

        for key in mods:
            self.engine.set_key_state(key, True)
        if normals:
            for key in normals:
                self.engine.tap_key(key)
        else:
            for key in mods:
                self.engine.tap_key(key)
        for key in reversed(mods):
            self.engine.set_key_state(key, False)

    def _force_release_modifier(self, key_code: int) -> None:
        state = self.modifiers[key_code]
        state.pressed = False
        state.latched = False
        state.used_in_combo = False
        self.engine.set_key_state(key_code, False)
        self._paint_modifier(key_code, False)

    def _paint_modifier(self, key_code: int, active: bool) -> None:
        button = self.modifier_buttons.get(key_code)
        if button is not None:
            self._paint_pressed(button, active)

    def _paint_pressed(self, button: Gtk.Button, active: bool) -> None:
        style = button.get_style_context()
        if active:
            style.add_class("pressed")
        else:
            style.remove_class("pressed")

    def _flash_regular_key(self, button: Gtk.Button) -> None:
        self._paint_pressed(button, True)

        def _clear() -> bool:
            self._paint_pressed(button, False)
            return False

        GLib.timeout_add(110, _clear)

    def _update_shift_labels(self) -> None:
        shift_active = any(self.modifiers[k].pressed or self.modifiers[k].latched for k in SHIFT_KEYS)
        for plain, symbol in SYMBOL_LABELS.items():
            button = self.regular_buttons.get(plain)
            if button is not None:
                button.set_label(symbol if shift_active else plain)

    def _start_repeat(self, key_code: int) -> None:
        if key_code in MODIFIER_KEYS or key_code == uinput.KEY_SPACE:
            return
        self._cancel_repeat(key_code)
        state = RepeatState()
        # Delay before first repeat, then switch to fixed repeat tick / 首次连发前延迟，然后进入固定节拍连发
        state.delay_source = GLib.timeout_add(420, self._repeat_delay_done, key_code)
        self.repeat_states[key_code] = state

    def _repeat_delay_done(self, key_code: int) -> bool:
        state = self.repeat_states.get(key_code)
        if state is None or key_code not in self.active_keys:
            return False
        state.repeat_source = GLib.timeout_add(70, self._repeat_tick, key_code)
        state.delay_source = None
        return False

    def _repeat_tick(self, key_code: int) -> bool:
        if key_code not in self.active_keys:
            self._cancel_repeat(key_code)
            return False
        self.engine.tap_key(key_code)
        return True

    def _cancel_repeat(self, key_code: int) -> None:
        state = self.repeat_states.pop(key_code, None)
        if state is None:
            return
        if state.delay_source:
            GLib.source_remove(state.delay_source)
        if state.repeat_source:
            GLib.source_remove(state.repeat_source)

    def _begin_space_tracking(self) -> None:
        # Long-press Space enters cursor mode, short tap sends space / 长按 Space 进入光标模式，短按发送空格
        self._cancel_space_long_press()
        self.space_cursor_mode = False
        self._set_space_cursor_visual(False)
        self.space_accum_x = 0.0
        self.space_accum_y = 0.0
        self.space_last_motion_at = 0.0
        self.space_long_press_source = GLib.timeout_add(self.space_long_press_ms, self._enter_space_cursor_mode)

    def _finish_space_tracking(self) -> None:
        moved = self.space_cursor_mode
        self._cancel_space_long_press()
        self.space_cursor_mode = False
        self._set_space_cursor_visual(False)
        self.space_accum_x = 0.0
        self.space_accum_y = 0.0
        self.space_last_motion_at = 0.0
        if not moved:
            self.engine.tap_key(uinput.KEY_SPACE)

    def _cancel_space_long_press(self) -> None:
        if self.space_long_press_source is not None:
            GLib.source_remove(self.space_long_press_source)
            self.space_long_press_source = None

    def _enter_space_cursor_mode(self) -> bool:
        if uinput.KEY_SPACE not in self.active_keys:
            return False
        self.space_cursor_mode = True
        self._set_space_cursor_visual(True)
        return False

    def _set_space_cursor_visual(self, active: bool) -> None:
        if self.space_button is None:
            return
        style = self.space_button.get_style_context()
        if active:
            self.space_button.set_label("◀ Space ▶")
            style.add_class("cursor-mode")
        else:
            self.space_button.set_label(self.space_button_default_label)
            style.remove_class("cursor-mode")

    def on_space_motion(self, _widget: Gtk.Button, event: Gdk.EventMotion) -> bool:
        if uinput.KEY_SPACE not in self.active_keys:
            return False

        if self.space_last_motion_at == 0.0:
            self.space_last_x = event.x
            self.space_last_y = event.y
            self.space_last_motion_at = event.time / 1000.0
            return True

        dx = event.x - self.space_last_x
        dy = event.y - self.space_last_y
        dt = max((event.time / 1000.0) - self.space_last_motion_at, 0.001)
        self.space_last_x = event.x
        self.space_last_y = event.y
        self.space_last_motion_at = event.time / 1000.0

        if not self.space_cursor_mode:
            return True

        self.space_accum_x += dx
        self.space_accum_y += dy
        speed = ((dx * dx + dy * dy) ** 0.5) / dt
        step_threshold = max(8.0, 28.0 - min(speed / 120.0, 16.0))
        self._emit_cursor_moves(step_threshold)
        return True

    def _emit_cursor_moves(self, step_threshold: float) -> None:
        # Use dominant axis to reduce accidental diagonal noise / 使用主导轴减少对角误触
        if abs(self.space_accum_x) >= abs(self.space_accum_y):
            steps = int(abs(self.space_accum_x) / step_threshold)
            if steps > 0:
                key = uinput.KEY_RIGHT if self.space_accum_x > 0 else uinput.KEY_LEFT
                for _ in range(steps):
                    self.engine.tap_key(key)
                self.space_accum_x -= step_threshold * steps if self.space_accum_x > 0 else -step_threshold * steps
                self.space_accum_y = 0.0
        else:
            steps = int(abs(self.space_accum_y) / step_threshold)
            if steps > 0:
                key = uinput.KEY_DOWN if self.space_accum_y > 0 else uinput.KEY_UP
                for _ in range(steps):
                    self.engine.tap_key(key)
                self.space_accum_y -= step_threshold * steps if self.space_accum_y > 0 else -step_threshold * steps
                self.space_accum_x = 0.0

    def _on_window_realize(self, *_args) -> None:
        self._raise_window_topmost()
        GLib.timeout_add(1500, self._raise_window_topmost)

    def _raise_window_topmost(self) -> bool:
        self.set_keep_above(True)
        self.stick()
        gdk_window = self.get_window()
        if gdk_window is not None:
            gdk_window.raise_()
        return True

    def _parse_shortcut(self, raw: str) -> List[int]:
        # Parse comma-separated tokens from config into uinput key codes / 将配置中的逗号分隔字符串解析为 uinput 键码
        result: List[int] = []
        for part in raw.split(","):
            token = part.strip().upper().replace("KEY_", "")
            token = CONFIG_TOKEN_ALIASES.get(token, token)
            key_code = getattr(uinput, f"KEY_{token}", None)
            if key_code is not None:
                result.append(key_code)
        return result or [uinput.KEY_LEFTSHIFT, uinput.KEY_SPACE]

    def _shortcut_to_config(self, combo: List[int]) -> str:
        name_map = {
            uinput.KEY_LEFTSHIFT: "LEFTSHIFT",
            uinput.KEY_RIGHTSHIFT: "RIGHTSHIFT",
            uinput.KEY_LEFTCTRL: "LEFTCTRL",
            uinput.KEY_RIGHTCTRL: "RIGHTCTRL",
            uinput.KEY_LEFTALT: "LEFTALT",
            uinput.KEY_RIGHTALT: "RIGHTALT",
            uinput.KEY_LEFTMETA: "LEFTMETA",
            uinput.KEY_RIGHTMETA: "RIGHTMETA",
            uinput.KEY_SPACE: "SPACE",
        }
        return ",".join(name_map.get(key, str(key)) for key in combo)

    def _load_settings(self) -> None:
        try:
            os.makedirs(self.config_dir, exist_ok=True)
        except PermissionError:
            return

        if not os.path.exists(self.config_file):
            return

        try:
            self.config.read(self.config_file)
            self.theme_name = self.config.get("DEFAULT", "theme", fallback=self.theme_name)
            self.opacity = self.config.get("DEFAULT", "opacity", fallback=self.opacity)
            self.font_size = self.config.getint("DEFAULT", "font_size", fallback=self.font_size)
            self.width = self.config.getint("DEFAULT", "width", fallback=0)
            self.height = self.config.getint("DEFAULT", "height", fallback=0)
            # Keep feature enabled by default unless explicitly disabled in config / 默认启用，除非配置中显式关闭
            self.double_shift_shortcut_enabled = self.config.getboolean(
                "DEFAULT", "double_shift_shortcut_enabled", fallback=self.double_shift_shortcut_enabled
            )
            shortcut = self.config.get("DEFAULT", "double_shift_shortcut", fallback="LEFTSHIFT,SPACE")
            self.double_shift_shortcut = self._parse_shortcut(shortcut)
        except configparser.Error:
            return

        self.font_size = min(48, max(10, self.font_size))
        if self.width > 0 and self.height > 0:
            self.set_default_size(self.width, self.height)

    def on_resize(self, *_args) -> None:
        self.width, self.height = self.get_size()

    def save_settings(self) -> None:
        self.config["DEFAULT"] = {
            "theme": self.theme_name,
            "opacity": self.opacity,
            "font_size": str(self.font_size),
            "width": str(self.width),
            "height": str(self.height),
            "double_shift_shortcut_enabled": str(self.double_shift_shortcut_enabled).lower(),
            "double_shift_shortcut": self._shortcut_to_config(self.double_shift_shortcut),
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as fp:
                self.config.write(fp)
        except OSError:
            pass


if __name__ == "__main__":
    win = MutterBoard()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.toggle_controls()
    Gtk.main()
