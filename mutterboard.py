import configparser
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import gi
import uinput

os.environ.setdefault("GDK_BACKEND", "x11")

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gdk, Gtk


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
    "Space": 12,
    "CapsLock": 3,
    "Shift_L": 4,
    "Shift_R": 4,
    "Backspace": 5,
    "\\": 4,
    "Enter": 5,
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
        self.device = uinput.Device(list(KEY_MAPPING.keys()))
        self.down_keys: Set[int] = set()

    def set_key_state(self, key_code: int, pressed: bool) -> None:
        currently_down = key_code in self.down_keys
        if pressed and not currently_down:
            self.device.emit(key_code, 1)
            self.down_keys.add(key_code)
        elif not pressed and currently_down:
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
        self.modifiers: Dict[int, ModifierState] = {key: ModifierState() for key in MODIFIER_KEYS}
        self.modifier_buttons: Dict[int, Gtk.Button] = {}
        self.regular_buttons: Dict[str, Gtk.Button] = {}
        self.repeat_states: Dict[int, RepeatState] = {}
        self.active_keys: Set[int] = set()

        self.last_shift_tap_at = 0.0
        self.double_shift_timeout_ms = 380
        self.double_shift_shortcut = [uinput.KEY_LEFTSHIFT, uinput.KEY_SPACE]

        self.colors = [
            ("Black", "18,18,21"), ("Blue", "32,53,97"), ("Purple", "74,45,108"), ("Gray", "44,44,52"),
            ("Green", "23,82,67"), ("Orange", "144,83,26"), ("Red", "123,38,45"), ("White", "235,235,238"),
        ]
        self.bg_color = "18,18,21"
        self.opacity = "0.94"
        self.text_color = "#F5F5F7"
        self.width = 0
        self.height = 0

        self._load_settings()
        self._build_ui()
        self.apply_css()

        self.connect("configure-event", self.on_resize)
        self.connect("destroy", lambda _: self.save_settings())

    def _configure_window(self) -> None:
        self.set_border_width(6)
        self.set_resizable(True)
        self.set_keep_above(True)
        self.set_focus_on_map(False)
        self.set_can_focus(False)
        self.set_accept_focus(False)
        self.set_default_icon_name("preferences-desktop-keyboard")

    def _configure_storage(self) -> None:
        self.config_dir = os.path.expanduser("~/.config/mutterboard")
        self.config_file = os.path.join(self.config_dir, "settings.conf")
        self.config = configparser.ConfigParser()

    def _build_ui(self) -> None:
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        root.set_name("root")
        self.add(root)

        self._build_header(root)
        self._build_drag_handle(root)
        self._build_keyboard(root)

    def _build_header(self, parent: Gtk.Box) -> None:
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.set_decoration_layout(":minimize,maximize,close")
        self.set_titlebar(self.header)

        self.settings_buttons: List[Gtk.Button] = []
        self._create_header_button("☰", self.toggle_controls)
        self._create_header_button("+", self.change_opacity, True)
        self._create_header_button("-", self.change_opacity, False)
        self.opacity_btn = self._create_header_button(self.opacity)

        self.color_combobox = Gtk.ComboBoxText()
        self.color_combobox.append_text("Theme")
        for label, _ in self.colors:
            self.color_combobox.append_text(label)
        self.color_combobox.set_active(0)
        self.color_combobox.set_name("combobox")
        self.color_combobox.connect("changed", self.change_color)
        self.header.add(self.color_combobox)

    def _build_drag_handle(self, parent: Gtk.Box) -> None:
        self.drag_handle = Gtk.EventBox()
        self.drag_handle.set_name("drag-handle")
        self.drag_handle.set_visible_window(True)
        self.drag_handle.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        drag_label = Gtk.Label(label="⋮⋮  Drag")
        drag_label.set_name("drag-label")
        self.drag_handle.add(drag_label)
        self.drag_handle.connect("button-press-event", self.on_drag_press)
        parent.pack_start(self.drag_handle, False, False, 0)

    def _build_keyboard(self, parent: Gtk.Box) -> None:
        grid = Gtk.Grid()
        grid.set_name("grid")
        grid.set_row_spacing(4)
        grid.set_column_spacing(4)
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        parent.pack_start(grid, True, True, 0)

        for row_index, row in enumerate(DEFAULT_LAYOUT):
            col = 0
            for label in row:
                key_code = LABEL_TO_KEY[label]
                shown = label[:-2] if label.endswith("_L") or label.endswith("_R") else label
                button = Gtk.Button(label=shown)
                button.set_name("key")
                button.connect("pressed", self.on_button_press, key_code)
                button.connect("released", self.on_button_release, key_code)
                button.connect("leave-notify-event", self.on_button_leave, key_code)

                width = KEY_WIDTHS.get(label, 2)
                grid.attach(button, col, row_index, width, 1)
                col += width

                if key_code in MODIFIER_KEYS:
                    self.modifier_buttons[key_code] = button
                else:
                    self.regular_buttons[label] = button

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

    def apply_css(self) -> None:
        provider = Gtk.CssProvider()
        css = f"""
        #toplevel {{ background: transparent; }}
        #root {{
            background-color: rgba({self.bg_color}, {self.opacity});
            border-radius: 12px;
            padding: 4px;
        }}
        #drag-handle {{
            background-color: rgba(255,255,255,0.07);
            border-radius: 8px;
            padding: 4px;
        }}
        #drag-label {{ color: {self.text_color}; font-size: 12px; }}
        headerbar {{
            background-color: rgba({self.bg_color}, {self.opacity});
            border: 0;
            box-shadow: none;
        }}
        headerbar button label, #combobox button.combo label {{ color: {self.text_color}; }}
        #key {{
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.08);
            background-image: none;
            background-color: rgba(255,255,255,0.08);
            min-height: 44px;
        }}
        #key:hover {{ border-color: rgba(0,202,203,0.95); }}
        #key label {{ color: {self.text_color}; font-weight: 600; }}
        #key.pressed {{
            background-color: rgba(0,202,203,0.3);
            border-color: rgba(0,202,203,0.95);
        }}
        """
        provider.load_from_data(css.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def on_drag_press(self, _widget, event) -> None:
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

    def toggle_controls(self, _button=None) -> None:
        for button in self.settings_buttons:
            if button.get_label() != "☰":
                button.set_visible(not button.get_visible())
        self.color_combobox.set_visible(not self.color_combobox.get_visible())

    def change_opacity(self, _button, increase: bool) -> None:
        delta = 0.02 if increase else -0.02
        self.opacity = str(round(min(1.0, max(0.35, float(self.opacity) + delta)), 2))
        self.opacity_btn.set_label(self.opacity)
        self.apply_css()

    def change_color(self, _widget) -> None:
        selected = self.color_combobox.get_active_text()
        for name, color in self.colors:
            if name == selected:
                self.bg_color = color
                break
        light_bg = self.bg_color in {"235,235,238"}
        self.text_color = "#18181A" if light_bg else "#F5F5F7"
        self.apply_css()

    def on_button_press(self, widget: Gtk.Button, key_code: int) -> None:
        self.active_keys.add(key_code)
        self._paint_pressed(widget, True)

        if key_code in MODIFIER_KEYS:
            self._on_modifier_press(key_code)
            self._update_shift_labels()
            return

        for mod_code, state in self.modifiers.items():
            if state.pressed:
                state.used_in_combo = True

        self.engine.set_key_state(key_code, True)
        self._start_repeat(key_code)

    def on_button_release(self, widget: Gtk.Button, key_code: int) -> None:
        self.active_keys.discard(key_code)
        self._paint_pressed(widget, False)

        if key_code in MODIFIER_KEYS:
            self._on_modifier_release(key_code)
            self._update_shift_labels()
            return

        self._cancel_repeat(key_code)
        self.engine.set_key_state(key_code, False)

        self._release_one_shot_modifiers()
        self._update_shift_labels()

    def on_button_leave(self, widget: Gtk.Button, _event, key_code: int) -> None:
        if key_code in self.active_keys:
            self.on_button_release(widget, key_code)

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

        # No combo happened while pressed -> toggle sticky(latched) state.
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

    def _update_shift_labels(self) -> None:
        shift_active = any(self.modifiers[key].pressed or self.modifiers[key].latched for key in SHIFT_KEYS)
        for plain, symbol in SYMBOL_LABELS.items():
            button = self.regular_buttons.get(plain)
            if button is not None:
                button.set_label(symbol if shift_active else plain)

    def _start_repeat(self, key_code: int) -> None:
        if key_code in MODIFIER_KEYS:
            return
        self._cancel_repeat(key_code)
        state = RepeatState()
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

    def _load_settings(self) -> None:
        try:
            os.makedirs(self.config_dir, exist_ok=True)
        except PermissionError:
            return

        if not os.path.exists(self.config_file):
            return

        try:
            self.config.read(self.config_file)
            self.bg_color = self.config.get("DEFAULT", "bg_color", fallback=self.bg_color)
            self.opacity = self.config.get("DEFAULT", "opacity", fallback=self.opacity)
            self.text_color = self.config.get("DEFAULT", "text_color", fallback=self.text_color)
            self.width = self.config.getint("DEFAULT", "width", fallback=0)
            self.height = self.config.getint("DEFAULT", "height", fallback=0)
            shortcut = self.config.get("DEFAULT", "double_shift_shortcut", fallback="LEFTSHIFT,SPACE")
            self.double_shift_shortcut = self._parse_shortcut(shortcut)
        except configparser.Error:
            return

        if self.width > 0 and self.height > 0:
            self.set_default_size(self.width, self.height)

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

    def on_resize(self, *_args) -> None:
        self.width, self.height = self.get_size()

    def save_settings(self) -> None:
        self.config["DEFAULT"] = {
            "bg_color": self.bg_color,
            "opacity": self.opacity,
            "text_color": self.text_color,
            "width": str(self.width),
            "height": str(self.height),
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
