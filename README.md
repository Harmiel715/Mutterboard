# MutterBoard (formerly vboard)

更接近原生硬件键盘行为的 Wayland 屏幕键盘（当前仍保持与原项目一致的可用范围：非 wlroots 场景）。

## 本次重点
- 组合键行为重做为“接近硬件键盘”模型：
  - 修饰键按下会发送 key-down，释放会发送 key-up。
  - 支持任意组合传递到焦点窗口（如 `Ctrl+C` / `Ctrl+V`）。
- 支持粘滞修饰键（单击锁定，下一次输入后自动释放），兼容单指操作。
- 支持 Shift 双击触发快捷键（默认 `LEFTSHIFT,SPACE`，可改）。
- 支持长按连发（含首次延迟和重复周期）。
- Shift 激活时，符号键位会动态显示为转换后的字符（如 `1 -> !`）。
- 外观优化：圆角、分层背景、键位高亮、更清晰的视觉反馈。
- 增加可拖动手柄，窗口拖动更方便。

## 兼容性说明（保持原硬限制）
- 仍保持原脚本可用范围，不主动扩展到 wlroots。
- 使用 `GDK_BACKEND=x11`，目标仍是原先可正常使用的 Wayland 会话类型。

## 运行
```bash
python3 mutterboard.py
```

兼容入口仍可用：
```bash
python3 vboard.py
```

## 依赖
请按发行版安装对应包（命名可能不同）：
- `python3-gi`
- `python3-uinput` / `python-uinput`
- `steam-devices`（某些发行版环境需要）

## 配置
配置文件：`~/.config/mutterboard/settings.conf`

示例：
```ini
[DEFAULT]
bg_color = 18,18,21
opacity = 0.94
text_color = #F5F5F7
double_shift_shortcut = LEFTSHIFT,SPACE
```

`double_shift_shortcut` 可写任意逗号分隔组合，例如：
- `LEFTCTRL,SPACE`
- `LEFTALT,LEFTSHIFT,SPACE`

## 备注
- 当前布局仍以 US QWERTY 为主。
- 后续若要扩展 compositor 兼容范围，可以在此版本基础上继续推进。
