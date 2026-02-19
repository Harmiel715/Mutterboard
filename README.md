# MutterBoard

更接近原生硬件键盘行为的 Wayland 屏幕键盘（当前仍保持非 wlroots 场景范围）。

## 本次重点
- 组合键行为重做为“接近硬件键盘”模型：
  - 修饰键按下发送 key-down，释放发送 key-up。
  - 支持任意组合传递到焦点窗口（如 `Ctrl+C` / `Ctrl+V`）。
- 支持粘滞修饰键（单击锁定，下一次输入后自动释放），并保留 Shift 双击快捷键。
- 新增 CapsLock 状态提示（`Caps: On/Off`），方便随时确认是否大写锁定。
- 修复快速连续点按场景（例如上一键未完全释放时按下一键）导致漏字母的问题。
- Shift 激活时，符号键位动态显示转换字符（如 `1 -> !`）。
- 主题系统重做（Dark / Light / Midnight），提升深浅色对比和可读性。
- 新增字体大小调节（A+ / A-），可按个人视觉习惯调整。
- 界面贴边优化：移除额外拖动条，减少多余空隙，主体内容更贴近窗口边界。

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

## 配置
配置文件：`~/.config/mutterboard/settings.conf`

示例：
```ini
[DEFAULT]
theme = Dark
opacity = 0.96
font_size = 15
capslock_on = false
double_shift_shortcut = LEFTSHIFT,SPACE
```

`double_shift_shortcut` 可写任意逗号分隔组合，例如：
- `LEFTCTRL,SPACE`
- `LEFTALT,LEFTSHIFT,SPACE`

## 备注
- 当前布局仍以 US QWERTY 为主。
- 后续若要扩展 compositor 兼容范围，可以在此版本基础上继续推进。


## 项目关系
MutterBoard 现作为独立项目继续维护，不再作为 fork 网络中的延续分支。

特别感谢原始项目 **vboard** 提供的基础思路与早期实现。