import configparser
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import gi
import uinput

os.environ.setdefault("GDK_BACKEND", "x11")

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402


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
class SpaceTrackingState:
    long_press_source: Optional[int] = None
    cursor_mode: bool = False
    last_x: float = 0.0
    last_y: float = 0.0
    last_time: float = 0.0
    accum_x: float = 0.0
    accum_y: float = 0.0


@dataclass
class TouchState:
    key_code: int
    button: Gtk.Button
    repeat_state: Optional[RepeatState] = None
    space_tracking: Optional[SpaceTrackingState] = None


@dataclass
class ModifierState:
    pressed: bool = False
    latched: bool = False
    used_in_combo: bool = False


class KeyboardEngine:
    def __init__(self) -> None:
        self.device = uinput.Device(list(KEY_MAPPING.keys()))
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
    MOUSE_TOUCH_ID = -1

    def __init__(self) -> None:
        super().__init__(title="MutterBoard", name="toplevel")
        self._configure_window()
        self._configure_storage()

        self.engine = KeyboardEngine()
        self.modifiers: Dict[int, ModifierState] = {key: ModifierState() for key in MODIFIER_KEYS}
        self.modifier_buttons: Dict[int, Gtk.Button] = {}
        self.regular_buttons: Dict[str, Gtk.Button] = {}
        self.button_to_key: Dict[Gtk.Button, int] = {}
        self.touch_states: Dict[int, TouchState] = {}
        self.repeat_states: Dict[int, RepeatState] = {}
        self.active_keys: Set[int] = set()
        self.key_rects: List[tuple[Gtk.Button, int, Gdk.Rectangle]] = []
        self.space_button: Optional[Gtk.Button] = None
        self.space_button_default_label = "Space"
        self.caps_indicator_button: Optional[Gtk.Button] = None

        self.space_long_press_ms = 300

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
        self._update_caps_indicator()
        self.apply_css()

        self.connect("configure-event", self.on_resize)
        self.connect("size-allocate", self._on_size_allocate)
        self.connect("event", self.on_window_event)
        self.connect("destroy", lambda _: self.save_settings())

    def _configure_window(self) -> None:
        self.set_border_width(0)
        self.set_resizable(True)
        self.set_keep_above(True)
        self.stick()
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

        self.settings_buttons: List[Gtk.Widget] = []
        self.header_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.header.pack_start(self.header_controls)

        self._create_header_button("☰", self.toggle_controls)
        self._create_header_button("+", self.change_opacity, True)
        self._create_header_button("-", self.change_opacity, False)
        self.opacity_btn = self._create_header_button(self.opacity)
        self._create_header_button("A+", self.change_font_size, 1)
        self._create_header_button("A-", self.change_font_size, -1)
        self.font_btn = self._create_header_button(f"{self.font_size}px")

        # CapsLock 指示器按钮
        self.caps_indicator_button = Gtk.Button(label="Caps: Off")
        self.caps_indicator_button.set_name("caps-indicator")
        self.caps_indicator_button.set_can_focus(False)
        self.caps_indicator_button.set_focus_on_click(False)
        self.caps_indicator_button.set_sensitive(False)  # 不可点击，仅用于显示
        self.header_controls.pack_start(self.caps_indicator_button, False, False, 0)

        self.theme_combobox = Gtk.ComboBoxText()
        self.theme_combobox.append_text("Theme")
        for name in THEMES:
            self.theme_combobox.append_text(name)
        self.theme_combobox.set_active(0)
        if self.theme_name in THEMES:
            self.theme_combobox.set_active(list(THEMES.keys()).index(self.theme_name) + 1)
        self.theme_combobox.set_name("combobox")
        self.theme_combobox.connect("changed", self.change_theme)
        self.header_controls.pack_start(self.theme_combobox, False, False, 0)

    def _build_keyboard(self, parent: Gtk.Box) -> None:
        grid = Gtk.Grid()
        grid.set_name("grid")
        grid.set_row_spacing(2)
        grid.set_column_spacing(2)
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        parent.pack_start(grid, True, True, 0)

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
                self.button_to_key[button] = key_code

                if key_code == uinput.KEY_SPACE:
                    self.space_button = button
                    self.space_button_default_label = shown

                grid.attach(button, col, row_index, width, 1)
                col += width

                if key_code in MODIFIER_KEYS:
                    self.modifier_buttons[key_code] = button
                else:
                    self.regular_buttons[label] = button

    def _on_size_allocate(self, _widget, _allocation) -> None:
        GLib.idle_add(self._update_key_rects)

    def _update_key_rects(self) -> bool:
        self.key_rects.clear()
        for button, key_code in self.button_to_key.items():
            if button.get_window() is None:
                continue
            translated = button.translate_coordinates(self, 0, 0)
            if translated is None:
                continue
            x, y = translated
            alloc = button.get_allocation()
            rect = Gdk.Rectangle()
            rect.x = x
            rect.y = y
            rect.width = alloc.width
            rect.height = alloc.height
            self.key_rects.append((button, key_code, rect))
        return False

    def _find_key_at(self, x: float, y: float) -> tuple[Optional[Gtk.Button], Optional[int]]:
        for button, key_code, rect in self.key_rects:
            if rect.x <= x <= rect.x + rect.width and rect.y <= y <= rect.y + rect.height:
                return button, key_code
        return None, None

    def _balanced_row_widths(self, row: List[str], target_width: int) -> List[int]:
        widths = [KEY_WIDTHS.get(label, 2) for label in row]
        deficit = target_width - sum(widths)
        idx = 0
        while deficit > 0 and widths:
            widths[idx % len(widths)] += 1
            idx += 1
            deficit -= 1
        return widths

    def _create_header_button(self, label: str, callback=None, callback_arg=None) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.set_name("headbar-button")
        if callback is not None:
            if callback_arg is None:
                button.connect("clicked", callback)
            else:
                button.connect("clicked", callback, callback_arg)
        self.header_controls.pack_start(button, False, False, 0)
        self.settings_buttons.append(button)
        return button

    def _theme(self) -> Dict[str, str]:
        return THEMES.get(self.theme_name, THEMES["Dark"])

    def apply_css(self) -> None:
        theme = self._theme()
        self.set_opacity(float(self.opacity))
        provider = Gtk.CssProvider()
        css = f"""
        #toplevel {{ background-color: rgb({theme['bg']}); }}
        #root {{ background-color: rgb({theme['bg']}); margin: 0; padding: 0; }}
        headerbar {{
            background-color: rgb({theme['bg']});
            border: 0;
            box-shadow: none;
            min-height: 54px;
        }}
        headerbar button {{
            background-image: none;
            background-color: rgb({theme['key']});
            border: 1px solid rgb({theme['key_border']});
            min-height: 46px;
            min-width: 52px;
            border-radius: 8px;
            margin: 4px 0;  /* 垂直居中，避免贴顶 */
        }}
        /* 不可用按钮（如 Caps 指示器）样式与普通按钮一致 */
        headerbar button:disabled {{
            background-image: none;
            background-color: rgb({theme['key']});
            border: 1px solid rgb({theme['key_border']});
        }}
        headerbar .titlebutton {{
            min-width: 56px;
            min-height: 46px;
            background-color: rgb({theme['key']});
        }}
        #combobox button.combo {{
            background-image: none;
            background-color: rgb({theme['key']});
            border: 1px solid rgb({theme['key_border']});
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
            border: 1px solid rgb({theme['key_border']});
            background-image: none;
            background-color: rgb({theme['key']});
            box-shadow: none;
            outline: none;
            min-height: 48px;
            margin: 0;
            padding: 0;
        }}
        .key-button label {{ color: {theme['text']}; font-weight: 600; font-size: {self.font_size}px; }}
        /* CapsLock 指示器按钮样式，与 header 其他按钮一致 */
        #caps-indicator {{
            background-image: none;
            background-color: rgb({theme['key']});
            border: 1px solid rgb({theme['key_border']});
            border-radius: 8px;
            min-height: 46px;
            min-width: 85px;          /* 宽度适配文本 */
            margin: 4px 0;             /* 与普通按钮一致 */
            padding: 0 8px;
            color: {theme['text']};
            font-size: {max(self.font_size - 2, 11)}px;
            font-weight: 700;
        }}
        /* CapsLock 开启时的蓝色文字 */
        #caps-indicator.caps-on {{
            color: rgba({theme['accent']}, 1.0);
        }}
        #caps-indicator.caps-on label {{
            color: rgba({theme['accent']}, 1.0);
        }}
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
        for button in self.settings_buttons[1:]:
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
        if self.caps_indicator_button is None:
            return
        self.caps_indicator_button.set_label("Caps: On" if self.capslock_on else "Caps: Off")
        style = self.caps_indicator_button.get_style_context()
        if self.capslock_on:
            style.add_class("caps-on")
        else:
            style.remove_class("caps-on")

    def _draw_caps_indicator(self, area: Gtk.DrawingArea, cr) -> bool:
        alloc = area.get_allocation()
        radius = min(alloc.width, alloc.height) / 2
        cr.set_source_rgba(0.28, 0.63, 1.0, 1.0)
        cr.arc(alloc.width / 2, alloc.height / 2, radius, 0, 6.283185307179586)
        cr.fill()
        return False

    def on_window_event(self, _widget, event) -> bool:
        etype = event.get_event_type()
        if etype in (
            Gdk.EventType.BUTTON_PRESS,
            Gdk.EventType.BUTTON_RELEASE,
            Gdk.EventType.TOUCH_BEGIN,
            Gdk.EventType.TOUCH_END,
            Gdk.EventType.TOUCH_UPDATE,
            Gdk.EventType.TOUCH_CANCEL,
        ):
            return self._handle_input_event(event)
        return False

    def _handle_input_event(self, event) -> bool:
        etype = event.get_event_type()

        if etype in (Gdk.EventType.BUTTON_PRESS, Gdk.EventType.BUTTON_RELEASE):
            button = event.get_button()[1] if isinstance(event.get_button(), tuple) else event.get_button()
            if button != 1:
                return False
            touch_id = self.MOUSE_TOUCH_ID
        else:
            seq = event.get_event_sequence()
            touch_id = hash(seq) if seq is not None else self.MOUSE_TOUCH_ID

        coords = event.get_coords()
        if coords is None:
            return False
        x, y = coords

        if etype in (Gdk.EventType.BUTTON_PRESS, Gdk.EventType.TOUCH_BEGIN):
            self._on_input_begin(touch_id, x, y)
            return True
        if etype in (Gdk.EventType.BUTTON_RELEASE, Gdk.EventType.TOUCH_END, Gdk.EventType.TOUCH_CANCEL):
            self._on_input_end(touch_id)
            return True
        if etype == Gdk.EventType.TOUCH_UPDATE:
            self._on_input_update(touch_id, x, y, event.time)
            return True
        return False

    def _on_input_begin(self, touch_id: int, x: float, y: float) -> None:
        if touch_id in self.touch_states:
            self._on_input_end(touch_id)

        button, key_code = self._find_key_at(x, y)
        if button is None or key_code is None:
            return

        touch_state = TouchState(key_code=key_code, button=button)
        self.touch_states[touch_id] = touch_state
        self.active_keys.add(key_code)

        if key_code == uinput.KEY_CAPSLOCK:
            self._flash_regular_key(button)
            self.capslock_on = not self.capslock_on
            self.engine.tap_key(uinput.KEY_CAPSLOCK)
            self._update_caps_indicator()
            self.touch_states.pop(touch_id, None)
            self.active_keys.discard(key_code)
            return

        self._paint_key_by_state(key_code)

        if key_code in MODIFIER_KEYS:
            self._on_modifier_press(key_code)
            self._update_shift_labels()
            return

        if key_code == uinput.KEY_SPACE:
            self._begin_space_tracking(touch_id)
            return

        for state in self.modifiers.values():
            if state.pressed:
                state.used_in_combo = True

        self.engine.tap_key(key_code)
        self._start_repeat(touch_id, key_code)

    def _on_input_end(self, touch_id: int) -> None:
        touch_state = self.touch_states.get(touch_id)
        if touch_state is None:
            return

        key_code = touch_state.key_code
        has_same_key = any(state.key_code == key_code for state in self.touch_states.values())
        if not has_same_key:
            self.active_keys.discard(key_code)

        if key_code == uinput.KEY_CAPSLOCK:
            return

        if key_code in MODIFIER_KEYS:
            self._on_modifier_release(key_code)
            self.touch_states.pop(touch_id, None)
            self._paint_key_by_state(key_code)
            self._update_shift_labels()
            return

        if key_code == uinput.KEY_SPACE:
            self._finish_space_tracking(touch_id)
            self.touch_states.pop(touch_id, None)
            self._paint_key_by_state(key_code)
            self._release_one_shot_modifiers()
            self._update_shift_labels()
            return

        self._cancel_repeat(touch_id)
        self.touch_states.pop(touch_id, None)
        self._paint_key_by_state(key_code)
        self._release_one_shot_modifiers()
        self._update_shift_labels()

    def _on_input_update(self, touch_id: int, x: float, y: float, event_time_ms: int) -> None:
        touch_state = self.touch_states.get(touch_id)
        if touch_state is None:
            return
        if touch_state.key_code == uinput.KEY_SPACE and touch_state.space_tracking is not None:
            self._on_space_motion(touch_id, x, y, event_time_ms)

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

    def _paint_key_by_state(self, key_code: int) -> None:
        button = self.modifier_buttons.get(key_code)
        if button is None:
            label = KEY_MAPPING.get(key_code)
            if label is None:
                return
            plain_label = label[:-2] if label.endswith("_L") or label.endswith("_R") else label
            button = self.regular_buttons.get(plain_label)
        if button is None:
            return
        is_pressed = any(state.key_code == key_code for state in self.touch_states.values())
        self._paint_pressed(button, is_pressed)

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

    def _start_repeat(self, touch_id: int, key_code: int) -> None:
        if key_code in MODIFIER_KEYS or key_code == uinput.KEY_SPACE:
            return
        self._cancel_repeat(touch_id)
        state = RepeatState()
        state.delay_source = GLib.timeout_add(420, self._repeat_delay_done, touch_id)
        self.repeat_states[touch_id] = state

        touch_state = self.touch_states.get(touch_id)
        if touch_state is not None:
            touch_state.repeat_state = state

    def _repeat_delay_done(self, touch_id: int) -> bool:
        touch_state = self.touch_states.get(touch_id)
        state = self.repeat_states.get(touch_id)
        if touch_state is None or state is None:
            return False
        state.repeat_source = GLib.timeout_add(70, self._repeat_tick, touch_id)
        state.delay_source = None
        return False

    def _repeat_tick(self, touch_id: int) -> bool:
        touch_state = self.touch_states.get(touch_id)
        if touch_state is None:
            self._cancel_repeat(touch_id)
            return False
        self.engine.tap_key(touch_state.key_code)
        return True

    def _cancel_repeat(self, touch_id: int) -> None:
        state = self.repeat_states.pop(touch_id, None)
        if state is None:
            return
        if state.delay_source:
            GLib.source_remove(state.delay_source)
        if state.repeat_source:
            GLib.source_remove(state.repeat_source)

    def _begin_space_tracking(self, touch_id: int) -> None:
        touch_state = self.touch_states.get(touch_id)
        if touch_state is None:
            return
        tracking = SpaceTrackingState()
        touch_state.space_tracking = tracking
        tracking.long_press_source = GLib.timeout_add(self.space_long_press_ms, self._enter_space_cursor_mode, touch_id)

    def _finish_space_tracking(self, touch_id: int) -> None:
        touch_state = self.touch_states.get(touch_id)
        tracking = touch_state.space_tracking if touch_state is not None else None
        moved = bool(tracking and tracking.cursor_mode)
        self._cancel_space_long_press(touch_id)
        self._set_space_cursor_visual(any(s.space_tracking and s.space_tracking.cursor_mode for s in self.touch_states.values()))
        if not moved:
            self.engine.tap_key(uinput.KEY_SPACE)

    def _cancel_space_long_press(self, touch_id: int) -> None:
        touch_state = self.touch_states.get(touch_id)
        tracking = touch_state.space_tracking if touch_state is not None else None
        if tracking is not None and tracking.long_press_source is not None:
            GLib.source_remove(tracking.long_press_source)
            tracking.long_press_source = None

    def _enter_space_cursor_mode(self, touch_id: int) -> bool:
        touch_state = self.touch_states.get(touch_id)
        if touch_state is None or touch_state.space_tracking is None or touch_state.key_code != uinput.KEY_SPACE:
            return False
        touch_state.space_tracking.cursor_mode = True
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

    def _on_space_motion(self, touch_id: int, x: float, y: float, event_time_ms: int) -> None:
        touch_state = self.touch_states.get(touch_id)
        if touch_state is None or touch_state.space_tracking is None:
            return
        tracking = touch_state.space_tracking

        if tracking.last_time == 0.0:
            tracking.last_x = x
            tracking.last_y = y
            tracking.last_time = event_time_ms / 1000.0
            return

        dx = x - tracking.last_x
        dy = y - tracking.last_y
        dt = max((event_time_ms / 1000.0) - tracking.last_time, 0.001)
        tracking.last_x = x
        tracking.last_y = y
        tracking.last_time = event_time_ms / 1000.0

        if not tracking.cursor_mode:
            return

        tracking.accum_x += dx
        tracking.accum_y += dy
        speed = ((dx * dx + dy * dy) ** 0.5) / dt
        step_threshold = max(8.0, 28.0 - min(speed / 120.0, 16.0))
        self._emit_cursor_moves(tracking, step_threshold)

    def _emit_cursor_moves(self, tracking: SpaceTrackingState, step_threshold: float) -> None:
        if abs(tracking.accum_x) >= abs(tracking.accum_y):
            steps = int(abs(tracking.accum_x) / step_threshold)
            if steps > 0:
                key = uinput.KEY_RIGHT if tracking.accum_x > 0 else uinput.KEY_LEFT
                for _ in range(steps):
                    self.engine.tap_key(key)
                tracking.accum_x -= step_threshold * steps if tracking.accum_x > 0 else -step_threshold * steps
                tracking.accum_y = 0.0
        else:
            steps = int(abs(tracking.accum_y) / step_threshold)
            if steps > 0:
                key = uinput.KEY_DOWN if tracking.accum_y > 0 else uinput.KEY_UP
                for _ in range(steps):
                    self.engine.tap_key(key)
                tracking.accum_y -= step_threshold * steps if tracking.accum_y > 0 else -step_threshold * steps
                tracking.accum_x = 0.0

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
            self.double_shift_shortcut_enabled = self.config.getboolean(
                "DEFAULT", "double_shift_shortcut_enabled", fallback=self.double_shift_shortcut_enabled
            )
            shortcut = self.config.get("DEFAULT", "double_shift_shortcut", fallback="LEFTSHIFT,SPACE")
            self.double_shift_shortcut = self._parse_shortcut(shortcut)
            self.capslock_on = self.config.getboolean("DEFAULT", "capslock_on", fallback=self.capslock_on)
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
            "capslock_on": str(self.capslock_on),
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
