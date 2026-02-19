# MutterBoard

MutterBoard 是一个面向 Linux 的屏幕键盘项目，目标是尽可能接近硬件键盘行为：
- 修饰键按下/抬起语义正确；
- 组合键可传递到焦点窗口（如 `Ctrl+C` / `Ctrl+V`）；
- 支持 Shift 双击快捷键、长按连发、CapsLock 状态提示。

> 兼容范围保持与原脚本一致：当前仍以非 wlroots 场景为主。

## 运行环境
- Linux
- Python 3.9+
- GTK 3（PyGObject）
- uinput（内核模块 + Python 绑定）
- Wayland 会话（当前项目保持既有可用范围，未扩展 wlroots）

## 依赖包
不同发行版包名略有差异，核心依赖如下：
- `python3-gi`（GTK 绑定）
- `python3-uinput` / `python-uinput`（uinput Python 绑定）
- `steam-devices`（某些发行版中用于输入设备权限）

示例安装：

### Debian / Ubuntu
```bash
sudo apt install python3-gi python3-uinput steam-devices
```

### Fedora
```bash
sudo dnf install python3-gobject python3-uinput steam-devices
```

### Arch Linux
```bash
yay -S python-uinput steam-devices
```

## uinput 与权限
如出现 `no such device`：
```bash
sudo modprobe uinput
```

开机自动加载：
```bash
echo 'uinput' | sudo tee /etc/modules-load.d/uinput.conf
```

如出现权限问题，可重新加载 udev 规则：
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## 运行
```bash
python3 mutterboard.py
```

兼容入口：
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
font_size = 18
capslock_on = false
double_shift_shortcut = LEFTSHIFT,SPACE
```

## 特性说明
- 主题：Dark / Light / Midnight
- 字号：支持大范围调整（标题栏 A+ / A-）
- CapsLock 状态可视化：`Caps: On / Off`
- Shift 激活时符号键动态显示（如 `1 -> !`）

## 致谢
本项目已作为独立项目维护。

感谢原始项目 **vboard** 提供的早期思路与实现基础。
