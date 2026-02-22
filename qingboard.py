 
# QingBoard 屏幕键盘主程序
# QingBoard on‑screen keyboard main program
# 基于 GTK3 和 uinput，实现硬件级修饰键语义、多点触控、空格光标模式等
# Based on GTK3 and uinput, providing hardware‑level modifier semantics, multi‑touch, space cursor mode, etc.

import configparser
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union

import gi
import uinput

# 设置 GDK 后端为 X11，确保在 Wayland 下也能正常工作（如果支持）
# Set GDK backend to X11 to improve compatibility under Wayland (if supported)
os.environ.setdefault("GDK_BACKEND", "x11")

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk

gi.require_version("Pango", "1.0")
from gi.repository import Pango


# ------------------------- 常量与映射 -------------------------
# Constants and mappings
# -------------------------

# uinput 键码 -> 显示标签的映射，用于查找和显示
# uinput key code to display label mapping, used for lookup and display
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

# 标签到键码的反向映射，用于布局构建
# Reverse mapping from label to key code, used for layout construction
LABEL_TO_KEY = {label: code for code, label in KEY_MAPPING.items()}

# 修饰键集合
# Set of modifier keys
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

# 仅 Shift 键，用于双按检测
# Only Shift keys, used for double‑tap detection
SHIFT_KEYS = {uinput.KEY_LEFTSHIFT, uinput.KEY_RIGHTSHIFT}

# 默认键盘布局（二维列表）
# Default keyboard layout (2D list)
DEFAULT_LAYOUT = [
    ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
    ["CapsLock", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
    ["Shift_L", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift_R", "↑"],
    ["Ctrl_L", "Super_L", "Alt_L", "Space", "Alt_R", "Super_R", "Ctrl_R", "←", "→", "↓"],
]

# 按键宽度（列数），用于网格布局
# Key width (in columns) for grid layout
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

# 带 Shift 时的符号映射（用于更新按键标签）
# Symbol mapping when Shift is active (used to update key labels)
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

# 配置文件中键名的别名映射
# Alias mapping for key names in configuration file
CONFIG_TOKEN_ALIASES = {
    "SHIFT": "LEFTSHIFT",
    "CTRL": "LEFTCTRL",
    "ALT": "LEFTALT",
    "SUPER": "LEFTMETA",
    "META": "LEFTMETA",
    "WIN": "LEFTMETA",
}

# 预定义主题（RGB 值或颜色字符串）
# Predefined themes (RGB values or color strings)
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

# 鼠标事件模拟的触摸点 ID（非触摸设备）
# Touch point ID for mouse events (non‑touch devices)
MOUSE_TOUCH_ID = -1


# ------------------------- 状态定义 -------------------------
# State definitions
# -------------------------

@dataclass
class RepeatState:
    """按键重复状态（按触摸点独立） | Key repeat state (independent per touch point)"""
    delay_source: Optional[int] = None   # 延迟超时源 | Delay timeout source ID
    repeat_source: Optional[int] = None  # 重复定时器源 | Repeat timer source ID


@dataclass
class ModifierState:
    """修饰键全局状态 | Global modifier state"""
    pressed: bool = False          # 是否有物理按下（至少一个触摸点） | Physically pressed (at least one touch point)
    latched: bool = False          # 是否处于锁存状态（单按后锁住） | Latched (after a single tap)
    used_in_combo: bool = False    # 是否在组合键中被使用（用于决定释放行为） | Used in a combination (affects release behavior)


@dataclass
class TouchState:
    """单个触摸点的状态 | State of a single touch point"""
    key_code: int                   # 当前按下的键码 | Currently pressed key code
    press_time: float               # 按下时的时间戳（单调时钟） | Press timestamp (monotonic clock)


@dataclass
class SpaceTrackingState:
    """空格拖动状态（按触摸点独立） | Space drag state (independent per touch point)"""
    cursor_mode: bool = False       # 是否已进入光标模式 | Whether cursor mode is active
    accum_x: float = 0.0            # X 方向累积位移 | Accumulated X displacement
    accum_y: float = 0.0            # Y 方向累积位移 | Accumulated Y displacement
    last_x: float = 0.0             # 上次事件 X 坐标 | Last event X coordinate
    last_y: float = 0.0             # 上次事件 Y 坐标 | Last event Y coordinate
    last_motion_at: float = 0.0     # 上次移动事件的时间（秒） | Last motion event time (seconds)
    long_press_source: Optional[int] = None  # 长按超时源 | Long‑press timeout source ID


# ------------------------- 键盘引擎 -------------------------
# Keyboard engine
# -------------------------

class KeyboardEngine:
    """封装 uinput 设备，负责发送按键事件 | Wraps the uinput device, responsible for sending key events"""
    def __init__(self) -> None:
        # 创建 uinput 设备，支持所有定义的按键
        # Create uinput device supporting all defined keys
        self.device = uinput.Device(list(KEY_MAPPING.keys()))
        self.down_keys: Set[int] = set()  # 当前按下的键码集合（用于去重） | Currently pressed key codes (for deduplication)

    def set_key_state(self, key_code: int, pressed: bool) -> None:
        """设置按键状态（按下/释放），避免重复发送相同状态 | Set key state (press/release) without sending duplicate events"""
        is_down = key_code in self.down_keys
        if pressed and not is_down:
            self.device.emit(key_code, 1)  # 1 = 按下 | 1 = press
            self.down_keys.add(key_code)
        elif not pressed and is_down:
            self.device.emit(key_code, 0)  # 0 = 释放 | 0 = release
            self.down_keys.discard(key_code)

    def tap_key(self, key_code: int) -> None:
        """发送一次按键点击（按下后立即释放） | Send a single key tap (press then immediately release)"""
        self.device.emit(key_code, 1)
        self.device.emit(key_code, 0)


# ------------------------- 主窗口 -------------------------
# Main window
# -------------------------

class QingBoard(Gtk.Window):
    """主窗口类，包含 UI 构建、事件处理、修饰键逻辑、空格光标模式等 | Main window class, handles UI building, event processing, modifier logic, space cursor mode, etc."""
    def __init__(self) -> None:
        super().__init__(title="QingBoard", name="toplevel")
        self._configure_window()
        self._configure_storage()

        # ---------- 触控相关 ----------
        # Touch related
        self.touch_states: Dict[Union[int, Gdk.EventSequence], TouchState] = {}  # 触摸点 ID -> TouchState | Touch point ID -> TouchState
        self.key_rects: List[Tuple[int, Gdk.Rectangle]] = []   # (key_code, rect) 列表，用于命中测试 | List of (key_code, rect) for hit testing
        self.key_widgets: Dict[int, Gtk.Widget] = {}           # key_code -> 标签控件（用于视觉反馈） | key_code -> label widget (for visual feedback)
        self.space_tracking: Dict[Union[int, Gdk.EventSequence], SpaceTrackingState] = {} # 空格拖动状态 | Space drag state per touch point
        self.repeat_states: Dict[Union[int, Gdk.EventSequence], RepeatState] = {} # 重复状态 per touch point | Repeat state per touch point
        self.key_press_count: Dict[int, int] = {}               # key_code -> 当前按下的触摸点数量 | key_code -> number of currently pressed touch points

        # ---------- 引擎与修饰键 ----------
        # Engine and modifiers
        self.engine = KeyboardEngine()
        self.modifiers: Dict[int, ModifierState] = {key: ModifierState() for key in MODIFIER_KEYS}
        self.modifier_labels: Dict[int, Gtk.Widget] = {}       # 修饰键标签（快速视觉反馈） | Modifier key labels (for quick visual feedback)
        self.caps_indicator_button: Optional[Gtk.Button] = None
        self.regular_labels: Dict[str, Gtk.Widget] = {}        # 普通键标签（用于符号切换） | Regular key labels (for symbol switching)

        # ---------- 双 Shift 快捷键 ----------
        # Double‑Shift shortcut
        self.last_shift_tap_at = 0.0
        self.double_shift_timeout_ms = 380
        self.double_shift_shortcut_enabled = True
        self.double_shift_shortcut = [uinput.KEY_LEFTSHIFT, uinput.KEY_SPACE]

        # ---------- 配置参数 ----------
        # Configuration parameters
        self.theme_name = "Dark"
        self.opacity = "0.96"
        self.font_size = 18
        self.width = 0
        self.height = 0
        self.capslock_on = False
        self.space_long_press_ms = 300

        # 加载设置并构建 UI
        # Load settings and build UI
        self._load_settings()
        self._build_ui()
        self._update_caps_indicator()
        self.apply_css()

        # 添加事件掩码，接收触控和鼠标事件
        # Add event masks to receive touch and mouse events
        self.add_events(
            Gdk.EventMask.TOUCH_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.connect("event", self.on_window_event)
        self.connect("size-allocate", self._on_size_allocate)
        self.connect("configure-event", self.on_resize)
        self.connect("destroy", lambda _: self.save_settings())

    # ------------------------- 窗口初始化辅助 -------------------------
    # Window initialization helpers
    # -------------------------

    def _configure_window(self) -> None:
        """设置窗口基本属性 | Set basic window properties"""
        self.set_border_width(0)
        self.set_resizable(True)
        self.set_keep_above(True)          # 保留置顶 | Keep above other windows
        self.stick()                        # 保留跨工作区 | Stick across workspaces
        # 使用 NORMAL 类型，让窗口管理器提供标准标题栏行为（包括拖动）
        # Use NORMAL type so the window manager provides a standard titlebar (including dragging)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_decorated(True)            # 保留标题栏 | Keep titlebar
        self.set_skip_taskbar_hint(False)
        self.set_skip_pager_hint(False)
        self.set_focus_on_map(False)
        self.set_can_focus(False)
        self.set_accept_focus(False)
        self.set_default_icon_name("preferences-desktop-keyboard")
        self.connect("realize", self._on_window_realize)

    def _configure_storage(self) -> None:
        """设置配置文件路径 | Set configuration file path"""
        self.config_dir = os.path.expanduser("~/.config/qingboard")
        self.config_file = os.path.join(self.config_dir, "settings.conf")
        self.config = configparser.ConfigParser()

    # ------------------------- UI 构建 -------------------------
    # UI building
    # -------------------------

    def _build_ui(self) -> None:
        """构建整个界面（标题栏 + 键盘网格） | Build the entire UI (header bar + keyboard grid)"""
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.set_name("root")
        self.add(root)

        self._build_header()
        self._build_keyboard(root)

    def _build_header(self) -> None:
        """构建标题栏及其中的控制按钮 | Build the header bar with its control buttons"""
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

        # CapsLock 指示器按钮（不可点击，仅显示状态）
        # CapsLock indicator button (non‑clickable, only shows state)
        self.caps_indicator_button = Gtk.Button(label="Caps: Off")
        self.caps_indicator_button.set_name("caps-indicator")
        self.caps_indicator_button.set_can_focus(False)
        self.caps_indicator_button.set_focus_on_click(False)
        self.caps_indicator_button.set_sensitive(False)
        self.header_controls.pack_start(self.caps_indicator_button, False, False, 0)

        # 主题选择下拉框
        # Theme selection combobox
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

    def _create_header_button(self, label: str, callback=None, callback_arg=None) -> Gtk.Button:
        """创建标题栏按钮的辅助函数 | Helper to create a header bar button"""
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

    def _build_keyboard(self, parent: Gtk.Box) -> None:
        """构建键盘网格，使用 Gtk.Label 作为按键装饰 | Build the keyboard grid, using Gtk.Label as key decorations"""
        self.grid = Gtk.Grid()
        self.grid.set_name("grid")
        self.grid.set_row_spacing(2)
        self.grid.set_column_spacing(2)
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_homogeneous(True)
        parent.pack_start(self.grid, True, True, 0)

        # 计算每行的目标宽度，使所有行宽度一致
        # Calculate target width for each row, making all rows the same width
        row_widths = [sum(KEY_WIDTHS.get(label, 2) for label in row) for row in DEFAULT_LAYOUT]
        target_width = max(row_widths)

        for row_index, row in enumerate(DEFAULT_LAYOUT):
            # 调整每行中每个按键的宽度，使总和等于 target_width
            # Adjust widths of keys in the row so the total equals target_width
            widths = self._balanced_row_widths(row, target_width)
            col = 0
            for label, width in zip(row, widths):
                key_code = LABEL_TO_KEY[label]
                # 去掉左右后缀（如 "_L"、"_R"）以获得更干净的显示
                # Strip "_L"/"_R" suffixes for cleaner display
                shown = label[:-2] if label.endswith("_L") or label.endswith("_R") else label

                # 创建标签作为按键的视觉表现（不接收事件）
                # Create a label as the visual representation of the key (does not receive events)
                label_widget = Gtk.Label(label=shown)
                label_widget.set_name("key")
                label_widget.get_style_context().add_class("key-button")
                label_widget.set_can_focus(False)
                label_widget.set_size_request(0, 48)  # 设置最小高度，保持布局稳定 | Set minimum height for stable layout
                label_widget.set_ellipsize(Pango.EllipsizeMode.END)   # 允许文本缩略，支持窗口宽度压缩 | Allow text ellipsizing for window compression
                self.grid.attach(label_widget, col, row_index, width, 1)
                col += width

                # 记录该按键对应的控件
                # Record the widget for this key
                self.key_widgets[key_code] = label_widget
                if key_code in MODIFIER_KEYS:
                    self.modifier_labels[key_code] = label_widget
                else:
                    self.regular_labels[label] = label_widget

    def _balanced_row_widths(self, row: List[str], target_width: int) -> List[int]:
        """通过将多余宽度分配到前面的按键，使整行宽度达到 target_width | Distribute extra width to earlier keys to reach target_width"""
        widths = [KEY_WIDTHS.get(label, 2) for label in row]
        deficit = target_width - sum(widths)
        idx = 0
        while deficit > 0 and widths:
            widths[idx % len(widths)] += 1
            idx += 1
            deficit -= 1
        return widths

    # ------------------------- 触控事件处理 -------------------------
    # Touch event handling
    # -------------------------

    def _on_size_allocate(self, widget, allocation):
        """窗口尺寸变化时，延迟更新按键区域矩形（等待布局稳定） | Delay updating key rects after size allocation (wait for layout to settle)"""
        GLib.idle_add(self._update_key_rects)

    def _update_key_rects(self):
        """重新计算每个按键相对于窗口的坐标矩形 | Recalculate each key's rectangle relative to the window"""
        self.key_rects.clear()
        for key_code, widget in self.key_widgets.items():
            alloc = widget.get_allocation()
            res = widget.translate_coordinates(self, 0, 0)
            if res:
                x, y = res[-2], res[-1]
                rect = Gdk.Rectangle()
                rect.x, rect.y, rect.width, rect.height = x, y, alloc.width, alloc.height
                self.key_rects.append((key_code, rect))

    def on_window_event(self, widget, event) -> bool:
        """全局事件处理入口，分发触控/鼠标事件 | Global event handler, dispatches touch/mouse events"""
        etype = event.get_event_type()

        # 只处理我们感兴趣的事件类型
        # Only handle event types we care about
        if etype not in (
            Gdk.EventType.BUTTON_PRESS,
            Gdk.EventType.BUTTON_RELEASE,
            Gdk.EventType.TOUCH_BEGIN,
            Gdk.EventType.TOUCH_END,
            Gdk.EventType.TOUCH_UPDATE,
            Gdk.EventType.MOTION_NOTIFY,
        ):
            return False

        # 获取事件坐标
        # Get event coordinates
        coords = event.get_coords()
        if not coords:
            return False
        win_x, win_y = coords[-2], coords[-1]

        # 获取触摸点 ID
        # Get touch point ID
        touch_id = MOUSE_TOUCH_ID
        if etype in (Gdk.EventType.TOUCH_BEGIN, Gdk.EventType.TOUCH_END, Gdk.EventType.TOUCH_UPDATE):
            seq = event.sequence
            touch_id = seq if seq is not None else 0

        # 根据事件类型分发
        # Dispatch based on event type
        if etype in (Gdk.EventType.BUTTON_PRESS, Gdk.EventType.TOUCH_BEGIN):
            key_code = self._find_key_at(win_x, win_y)
            if key_code is None:
                return False

            # 命中了按键
            # Hit a key
            self._on_input_begin(touch_id, win_x, win_y, event.time)

            # 关键：在这里强行刷一下文字显示，这样当你点下 Shift 的那一秒，符号才会立刻跳出来
            # Critical: force label update here so that symbols appear immediately when Shift is pressed
            self._update_shift_labels()

            return True

        elif etype in (Gdk.EventType.BUTTON_RELEASE, Gdk.EventType.TOUCH_END):
            # 只有当这个触摸点是我们正在追踪的（起始在按键上），才拦截并处理
            # Only intercept if this touch point is being tracked (started on a key)
            if touch_id in self.touch_states:
                self._on_input_end(touch_id, event.time)
                self._update_shift_labels()
                return True
            return False

        elif etype in (Gdk.EventType.TOUCH_UPDATE, Gdk.EventType.MOTION_NOTIFY):
            # 同理，只处理追踪中的滑动事件（比如长按空格后的光标移动）
            # Similarly, only handle motion for tracked touch points (e.g., space cursor movement)
            if touch_id in self.touch_states:
                self._on_input_update(touch_id, win_x, win_y, event.time)
                return True
            return False

        return False

    def _find_key_at(self, x, y) -> Optional[int]:
        """根据窗口坐标查找按键，返回键码 | Find key at given window coordinates, return key code"""
        for key_code, rect in self.key_rects:
            if rect.x <= x <= rect.x + rect.width and rect.y <= y <= rect.y + rect.height:
                return key_code
        return None

    def _on_input_begin(self, touch_id: Union[int, Gdk.EventSequence], x: float, y: float, event_time: int) -> None:
        """触摸/鼠标按下处理 | Handle touch/mouse press"""
        # 如果该触摸点已存在，先结束它
        # If this touch point already exists, end it first
        if touch_id in self.touch_states:
            self._on_input_end(touch_id, event_time)

        key_code = self._find_key_at(x, y)
        if key_code is None:
            return

        # 记录触摸点状态
        # Record touch point state
        state = TouchState(key_code=key_code, press_time=time.monotonic())
        self.touch_states[touch_id] = state

        # 更新按键按压计数器
        # Update press counter for this key
        self.key_press_count[key_code] = self.key_press_count.get(key_code, 0) + 1

        # 特殊按键：CapsLock
        # Special key: CapsLock
        if key_code == uinput.KEY_CAPSLOCK:
            self.capslock_on = not self.capslock_on
            self.engine.tap_key(uinput.KEY_CAPSLOCK)
            self._update_caps_indicator()
            self._flash_regular_key(key_code)
            return

        # 修饰键
        # Modifier keys
        if key_code in MODIFIER_KEYS:
            self._on_modifier_press_touch(touch_id, key_code)
            self._update_shift_labels()
            return

        # 空格键
        # Space key
        if key_code == uinput.KEY_SPACE:
            for mod_state in self.modifiers.values():
                if mod_state.pressed:
                    mod_state.used_in_combo = True
            self._begin_space_tracking(touch_id)
            self._update_visual(key_code, True)
            return

        # 普通键
        # Regular keys
        for mod_state in self.modifiers.values():
            if mod_state.pressed:
                mod_state.used_in_combo = True

        # 当按下新的普通键时，取消所有其他普通键的重复
        # When a new regular key is pressed, cancel repeats of all other regular keys
        self._stop_all_other_repeats(key_code, touch_id)

        self.engine.tap_key(key_code)
        self._start_repeat(touch_id, key_code)
        if self.key_press_count[key_code] == 1:
            self._update_visual(key_code, True)

    def _stop_all_other_repeats(self, current_key: int, current_touch: Union[int, Gdk.EventSequence]) -> None:
        """取消所有其他触摸点上的普通键重复 | Cancel repeats on all other touch points that are pressing regular keys"""
        for tid, state in list(self.touch_states.items()):
            if tid != current_touch and state.key_code not in MODIFIER_KEYS and state.key_code != uinput.KEY_SPACE:
                self._cancel_repeat(tid)

    def _on_input_end(self, touch_id: Union[int, Gdk.EventSequence], event_time: int) -> None:
        """触摸/鼠标释放处理 | Handle touch/mouse release"""
        state = self.touch_states.pop(touch_id, None)
        if not state:
            return

        key_code = state.key_code

        # 减少计数器
        # Decrement press counter
        count = self.key_press_count.get(key_code, 0)
        if count > 0:
            new_count = count - 1
            self.key_press_count[key_code] = new_count
        else:
            new_count = 0

        if key_code == uinput.KEY_CAPSLOCK:
            return

        if key_code in MODIFIER_KEYS:
            self._on_modifier_release_touch(touch_id, key_code)
        elif key_code == uinput.KEY_SPACE:
            self._finish_space_tracking(touch_id)
            self._release_one_shot_modifiers()
            self._update_shift_labels()
            self._update_visual(key_code, False)
        else:
            self._cancel_repeat(touch_id)
            self._release_one_shot_modifiers()
            self._update_shift_labels()
            if new_count == 0:
                self._update_visual(key_code, False)

    def _on_input_update(self, touch_id: Union[int, Gdk.EventSequence], x: float, y: float, event_time: int) -> None:
        """触摸移动处理（目前仅用于空格拖动） | Handle touch motion (currently only for space dragging)"""
        state = self.touch_states.get(touch_id)
        if not state:
            return

        if state.key_code == uinput.KEY_SPACE:
            self._on_space_motion_touch(touch_id, x, y, event_time)

    # ------------------------- 视觉反馈 -------------------------
    # Visual feedback
    # -------------------------

    def _update_visual(self, key_code: int, pressed: bool) -> None:
        """更新指定按键的 pressed 样式类 | Update the 'pressed' style class for a key"""
        widget = self.key_widgets.get(key_code)
        if widget:
            style = widget.get_style_context()
            if pressed:
                style.add_class("pressed")
            else:
                style.remove_class("pressed")

    def _flash_regular_key(self, key_code: int) -> None:
        """让普通键闪烁一下 | Briefly flash a regular key"""
        self._update_visual(key_code, True)

        def _clear() -> bool:
            self._update_visual(key_code, False)
            return False

        GLib.timeout_add(110, _clear)

    def _paint_modifier(self, key_code: int, active: bool) -> None:
        """专门更新修饰键的 pressed 样式 | Update 'pressed' style for a modifier key"""
        widget = self.modifier_labels.get(key_code)
        if widget:
            style = widget.get_style_context()
            if active:
                style.add_class("pressed")
            else:
                style.remove_class("pressed")

    def _update_shift_labels(self) -> None:
        """根据 Shift 状态切换符号键的显示 | Update symbol key labels based on Shift state"""
        shift_active = any(self.modifiers[k].pressed or self.modifiers[k].latched for k in SHIFT_KEYS)
        for plain, symbol in SYMBOL_LABELS.items():
            widget = self.regular_labels.get(plain)
            if widget:
                widget.set_label(symbol if shift_active else plain)

    def _set_space_cursor_visual(self, touch_id: Union[int, Gdk.EventSequence], active: bool) -> None:
        """更新空格键的视觉样式（光标模式） | Update visual style of the Space key (cursor mode)"""
        widget = self.key_widgets.get(uinput.KEY_SPACE)
        if widget is None:
            return
        style = widget.get_style_context()
        if active:
            widget.set_label("◀ Space ▶")
            style.add_class("cursor-mode")
        else:
            widget.set_label("Space")
            style.remove_class("cursor-mode")

    def _update_caps_indicator(self) -> None:
        """更新标题栏中的 CapsLock 指示器 | Update the CapsLock indicator in the header bar"""
        if self.caps_indicator_button is None:
            return
        self.caps_indicator_button.set_label("Caps: On" if self.capslock_on else "Caps: Off")
        style = self.caps_indicator_button.get_style_context()
        if self.capslock_on:
            style.add_class("caps-on")
        else:
            style.remove_class("caps-on")

    # ------------------------- 修饰键逻辑 -------------------------
    # Modifier key logic
    # -------------------------

    def _on_modifier_press_touch(self, touch_id: Union[int, Gdk.EventSequence], key_code: int) -> None:
        """触摸点按下修饰键时的处理 | Handle modifier press for a touch point"""
        if not self.modifiers[key_code].pressed:
            self._on_modifier_press_global(key_code)

    def _on_modifier_press_global(self, key_code: int) -> None:
        """全局修饰键按下 | Global modifier press"""
        state = self.modifiers[key_code]
        state.pressed = True
        state.used_in_combo = False

        if key_code in SHIFT_KEYS:
            opposite = uinput.KEY_RIGHTSHIFT if key_code == uinput.KEY_LEFTSHIFT else uinput.KEY_LEFTSHIFT
            self._force_release_modifier(opposite)

        self.engine.set_key_state(key_code, True)
        self._paint_modifier(key_code, True)

    def _on_modifier_release_touch(self, touch_id: Union[int, Gdk.EventSequence], key_code: int) -> None:
        """触摸点释放修饰键时的处理 | Handle modifier release for a touch point"""
        still_pressed = any(
            s.key_code == key_code for tid, s in self.touch_states.items() if tid != touch_id
        )
        if not still_pressed:
            self._on_modifier_release_global(key_code)

    def _on_modifier_release_global(self, key_code: int) -> None:
        """全局修饰键释放 | Global modifier release"""
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

    def _force_release_modifier(self, key_code: int) -> None:
        """强制释放某个修饰键 | Force‑release a modifier key"""
        state = self.modifiers[key_code]
        state.pressed = False
        state.latched = False
        state.used_in_combo = False
        self.engine.set_key_state(key_code, False)
        self._paint_modifier(key_code, False)

    def _release_one_shot_modifiers(self) -> None:
        """释放所有锁存但未被按住的修饰键 | Release all latched modifiers that are not physically pressed"""
        for key_code, state in self.modifiers.items():
            if state.latched and not state.pressed:
                state.latched = False
                self.engine.set_key_state(key_code, False)
                self._paint_modifier(key_code, False)

    def _handle_shift_double_tap(self) -> None:
        """检测 Shift 双按，触发预设快捷键 | Detect double‑tap of Shift and trigger the configured shortcut"""
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
        """发送组合键 | Emit a key combination"""
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

    # ------------------------- 按键重复 -------------------------
    # Key repeat
    # -------------------------

    def _start_repeat(self, touch_id: Union[int, Gdk.EventSequence], key_code: int) -> None:
        """启动按键重复（仅普通键） | Start key repeat (regular keys only)"""
        if key_code in MODIFIER_KEYS or key_code == uinput.KEY_SPACE:
            return
        self._cancel_repeat(touch_id)
        state = RepeatState()
        state.delay_source = GLib.timeout_add(420, self._repeat_delay_done, touch_id, key_code)
        self.repeat_states[touch_id] = state

    def _repeat_delay_done(self, touch_id: Union[int, Gdk.EventSequence], key_code: int) -> bool:
        """延迟结束，开始周期性重复 | Delay finished, start periodic repeats"""
        if touch_id not in self.touch_states or self.touch_states[touch_id].key_code != key_code:
            return False
        state = self.repeat_states.get(touch_id)
        if state is None:
            return False
        state.repeat_source = GLib.timeout_add(70, self._repeat_tick, touch_id, key_code)
        state.delay_source = None
        return False

    def _repeat_tick(self, touch_id: Union[int, Gdk.EventSequence], key_code: int) -> bool:
        """重复周期触发，发送一次按键 | Repeat tick, send one key tap"""
        if touch_id not in self.touch_states or self.touch_states[touch_id].key_code != key_code:
            self._cancel_repeat(touch_id)
            return False
        self.engine.tap_key(key_code)
        return True

    def _cancel_repeat(self, touch_id: Union[int, Gdk.EventSequence]) -> None:
        """取消指定触摸点的重复 | Cancel repeat for the given touch point"""
        state = self.repeat_states.pop(touch_id, None)
        if state is None:
            return
        if state.delay_source:
            GLib.source_remove(state.delay_source)
        if state.repeat_source:
            GLib.source_remove(state.repeat_source)

    # ------------------------- 空格拖动 -------------------------
    # Space dragging (cursor mode)
    # -------------------------

    def _begin_space_tracking(self, touch_id: Union[int, Gdk.EventSequence]) -> None:
        """开始跟踪空格键的按下 | Start tracking a space press"""
        self._cancel_space_long_press(touch_id)
        tracking = SpaceTrackingState()
        tracking.long_press_source = GLib.timeout_add(
            self.space_long_press_ms, self._enter_space_cursor_mode, touch_id
        )
        self.space_tracking[touch_id] = tracking

    def _finish_space_tracking(self, touch_id: Union[int, Gdk.EventSequence]) -> None:
        """结束空格键的跟踪 | Finish tracking a space press"""
        tracking = self.space_tracking.pop(touch_id, None)
        if tracking is None:
            self.engine.tap_key(uinput.KEY_SPACE)
            return

        self._cancel_space_long_press(touch_id)
        if not tracking.cursor_mode:
            self.engine.tap_key(uinput.KEY_SPACE)

    def _cancel_space_long_press(self, touch_id: Union[int, Gdk.EventSequence]) -> None:
        """取消空格的长按定时器 | Cancel the space long‑press timer"""
        tracking = self.space_tracking.get(touch_id)
        if tracking and tracking.long_press_source is not None:
            GLib.source_remove(tracking.long_press_source)
            tracking.long_press_source = None

    def _enter_space_cursor_mode(self, touch_id: Union[int, Gdk.EventSequence]) -> bool:
        """长按超时，进入光标模式 | Long‑press timeout, enter cursor mode"""
        if touch_id not in self.touch_states or self.touch_states[touch_id].key_code != uinput.KEY_SPACE:
            return False
        tracking = self.space_tracking.get(touch_id)
        if tracking is None:
            return False
        tracking.cursor_mode = True
        self._set_space_cursor_visual(touch_id, True)
        return False

    def _on_space_motion_touch(self, touch_id: Union[int, Gdk.EventSequence], x: float, y: float, event_time: int) -> None:
        """空格移动事件处理 | Handle space motion events"""
        tracking = self.space_tracking.get(touch_id)
        if tracking is None or not tracking.cursor_mode:
            return

        if tracking.last_motion_at == 0.0:
            tracking.last_x = x
            tracking.last_y = y
            tracking.last_motion_at = event_time / 1000.0
            return

        dx = x - tracking.last_x
        dy = y - tracking.last_y
        dt = max((event_time / 1000.0) - tracking.last_motion_at, 0.001)
        tracking.last_x = x
        tracking.last_y = y
        tracking.last_motion_at = event_time / 1000.0

        tracking.accum_x += dx
        tracking.accum_y += dy
        speed = ((dx * dx + dy * dy) ** 0.5) / dt
        step_threshold = max(8.0, 28.0 - min(speed / 120.0, 16.0))
        self._emit_cursor_moves(tracking, step_threshold)

    def _emit_cursor_moves(self, tracking: SpaceTrackingState, step_threshold: float) -> None:
        """根据累积位移发送方向键 | Emit arrow keys based on accumulated displacement"""
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

    # ------------------------- 窗口管理 -------------------------
    # Window management
    # -------------------------

    def _on_window_realize(self, *_args) -> None:
        """窗口实现后，尝试置顶 | Try to raise window after realization"""
        self._raise_window_topmost()
        GLib.timeout_add(1500, self._raise_window_topmost)

    def _raise_window_topmost(self) -> bool:
        """将窗口置顶 | Raise window to top"""
        self.set_keep_above(True)
        self.stick()
        gdk_window = self.get_window()
        if gdk_window is not None:
            gdk_window.raise_()
        return True

    # ------------------------- 主题与样式 -------------------------
    # Theme and styling
    # -------------------------

    def _theme(self) -> Dict[str, str]:
        """返回当前主题的字典 | Return the current theme dictionary"""
        return THEMES.get(self.theme_name, THEMES["Dark"])

    def apply_css(self) -> None:
        """应用CSS样式 | Apply CSS styling"""
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
            min-width: 0;                      /* 允许按钮宽度压缩，配合窗口宽度调整 | Allow button width to compress */
            border-radius: 8px;
            margin: 4px 0;
        }}
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
        .key-button {{
            border-radius: 8px;
            border: 1px solid rgb({theme['key_border']});
            background-image: none;
            background-color: rgb({theme['key']});
            box-shadow: none;
            outline: none;
            min-height: 48px;
            min-width: 0;      /* 允许按键宽度压缩，支持窗口缩小 | Allow key width to compress */
            margin: 0;
            padding: 0;
            color: {theme['text']};
            font-weight: 600;
            font-size: {self.font_size}px;
        }}
        #caps-indicator {{
            background-image: none;
            background-color: rgb({theme['key']});
            border: 1px solid rgb({theme['key_border']});
            border-radius: 8px;
            min-height: 46px;
            min-width: 85px;
            margin: 4px 0;
            padding: 0 8px;
            color: {theme['text']};
            font-size: {max(self.font_size - 2, 11)}px;
            font-weight: 700;
        }}
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

    # ------------------------- 控制功能 -------------------------
    # Control functions
    # -------------------------

    def toggle_controls(self, _button=None) -> None:
        """切换标题栏额外控件的可见性 | Toggle visibility of extra header bar controls"""
        for button in self.settings_buttons[1:]:
            button.set_visible(not button.get_visible())
        self.theme_combobox.set_visible(not self.theme_combobox.get_visible())

    def change_opacity(self, _button, increase: bool) -> None:
        """调整窗口透明度 | Adjust window opacity"""
        delta = 0.02 if increase else -0.02
        self.opacity = str(round(min(1.0, max(0.35, float(self.opacity) + delta)), 2))
        self.opacity_btn.set_label(self.opacity)
        self.apply_css()

    def change_font_size(self, _button, delta: int) -> None:
        """调整字体大小 | Adjust font size"""
        self.font_size = min(48, max(10, self.font_size + delta * 2))
        self.font_btn.set_label(f"{self.font_size}px")
        self.apply_css()

    def change_theme(self, _widget) -> None:
        """切换主题 | Change theme"""
        selected = self.theme_combobox.get_active_text()
        if selected in THEMES:
            self.theme_name = selected
            self.apply_css()

    # ------------------------- 配置读写 -------------------------
    # Configuration I/O
    # -------------------------

    def _parse_shortcut(self, raw: str) -> List[int]:
        """将配置文件中的快捷键字符串解析为键码列表 | Parse a shortcut string from config into a list of key codes"""
        result: List[int] = []
        for part in raw.split(","):
            token = part.strip().upper().replace("KEY_", "")
            token = CONFIG_TOKEN_ALIASES.get(token, token)
            key_code = getattr(uinput, f"KEY_{token}", None)
            if key_code is not None:
                result.append(key_code)
        return result or [uinput.KEY_LEFTSHIFT, uinput.KEY_SPACE]

    def _shortcut_to_config(self, combo: List[int]) -> str:
        """将键码列表转换为配置文件中的字符串 | Convert a list of key codes to a config string"""
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
        """从配置文件加载设置 | Load settings from config file"""
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
        """窗口大小改变时记录尺寸 | Record window size on resize"""
        self.width, self.height = self.get_size()

    def save_settings(self) -> None:
        """保存当前设置到配置文件 | Save current settings to config file"""
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


# ------------------------- 程序入口 -------------------------
# Program entry point
# -------------------------

if __name__ == "__main__":
    win = QingBoard()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.toggle_controls()
    Gtk.main()
