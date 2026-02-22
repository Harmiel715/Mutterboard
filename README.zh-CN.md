# QingBoard

一个面向 Linux 的屏幕键盘项目，目标是尽可能贴近实体键盘行为。

📘 English documentation: [README.md](./README.md)

---

## 简介

QingBoard 使用 GTK3 构建界面，通过 `uinput` 注入真实按键事件，适用于触摸设备、临时替代物理键盘、以及无障碍输入等桌面场景。

相比只做“按钮点击”的简化屏幕键盘，QingBoard 更关注：

- 修饰键语义准确性
- 组合键可用性
- 状态同步（例如 CapsLock 指示）
- 多点触控支持（触摸点独立跟踪）

---

## 特性

- **硬件级修饰键行为**
  - 支持 Shift/Ctrl/Alt/Super 的按下与释放语义。
  - 支持修饰键一次性锁定（latch）与自动释放逻辑（例如轻触 Shift 一次即可锁定）。
- **组合键友好**
  - 常见快捷键可透传到当前焦点窗口（如 `Ctrl+C`、`Ctrl+V`）。
- **Shift 双击快捷键触发**
  - 双击任一 Shift 键可触发可配置快捷键（默认：`LEFTSHIFT,SPACE`），可通过配置文件启用/关闭。
- **快速连续点击稳定性**
  - 普通键改为“按下即发送（tap-first）”，在 XWayland 等单指针触摸栈下也能稳定处理快速连续点击。
- **全局顶层窗口**
  - 在保留最小化/最大化/关闭装饰按钮的前提下，使用 NORMAL 类型窗口（带标题栏，可拖动）并周期性提升层级，尽量降低被输入法候选窗遮挡概率。
- **长按连发**
  - 普通键支持按住自动重复（延迟 420ms，间隔 70ms）。
- **Space 光标模式**
  - 长按 Space 进入光标模式，按键标签切换为 `◀ Space ▶` 并高亮边框/文字。
  - 进入后水平滑动触发 Left/Right，垂直滑动触发 Up/Down。
  - 触发阈值根据滑动速度动态调整，实现更自然的控制。
- **CapsLock 处理**
  - CapsLock 键切换内部状态，发送按键事件，并更新顶部栏指示器。
  - 顶部栏指示器采用按钮样式，与其他控制按钮外观一致；CapsLock 开启时文字变为强调色。
  - CapsLock 状态会保存并在下次启动时恢复。
- **Shift 动态符号标签**
  - Shift 激活时，数字/符号键标签动态切换（如 `1` → `!`）。
- **多点触控支持**
  - 每个触摸点独立跟踪，支持同时按下多个按键，互不干扰。
  - 触摸移动用于空格光标模式，增强触摸板体验。
- **可定制界面**
  - 主题：`Dark`、`Light`、`Midnight`
  - 降低按键背景透明度，让半透明时后方内容更易辨认。
  - 鼠标悬停/预选不会改变按键背景透明度，仅点击反馈和粘滞键状态会改变按键视觉。
  - 标题栏支持透明度与字号调节。
- **设置持久化**
  - 自动保存主题、透明度、字号、窗口尺寸、双击 Shift 快捷键、CapsLock 状态。

---

## 截图

<img width="2414" height="849" alt="QingBoard 截图" src="https://github.com/user-attachments/assets/45d70608-855d-4919-b325-4c95ecbaeb11" />

---

## 依赖项

运行时依赖：

- Linux
- Python 3.9+
- GTK 3（PyGObject：`python3-gi` / `python3-gobject`）
- `uinput` 内核模块 + Python 绑定（`python3-uinput` / `python-uinput`）

可选依赖（部分发行版有帮助）：

- `steam-devices`（在某些环境中有助于输入设备权限）

---

## 安装

### Debian / Ubuntu

```bash
sudo apt install python3-gi python3-uinput steam-devices
```

### Fedora

```bash
sudo dnf install python3-gobject python3-uinput steam-devices
```

### Arch Linux（AUR 示例）

```bash
yay -S python-uinput steam-devices
```

---

## 使用

```bash
python3 qingboard.py
```

### 可选：创建桌面快捷方式

```bash
mkdir -p ~/.local/share/applications/
cat > ~/.local/share/applications/qingboard.desktop <<EOF
[Desktop Entry]
Exec=bash -c 'python3 /path/to/qingboard.py'
Icon=preferences-desktop-keyboard
Name=QingBoard
Terminal=false
Type=Application
Categories=Utility;
NoDisplay=false
EOF
chmod +x ~/.local/share/applications/qingboard.desktop
```

---

## 配置

配置文件：

```text
~/.config/qingboard/settings.conf
```

示例：

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

字段说明：

- `theme`：`Dark` / `Light` / `Midnight`
- `opacity`：程序会限制范围（约 `0.35` 到 `1.0`）
- `font_size`：程序会限制范围（约 `10` 到 `48`）
- `width` / `height`：窗口大小（退出时持久化）
- `double_shift_shortcut_enabled`：是否启用 Shift 双击快捷键触发（默认 `true`）
- `double_shift_shortcut`：双击 Shift 触发的组合键（逗号分隔，例如 `LEFTSHIFT,SPACE`）
- `capslock_on`：内部 CapsLock 状态（自动保存）

---

## 可能会有的问题（排查）

1. **报错：`no such device`**

   可能是 `uinput` 模块未加载：

   ```bash
   sudo modprobe uinput
   ```

2. **重启后失效**

   可设置开机自动加载：

   ```bash
   echo 'uinput' | sudo tee /etc/modules-load.d/uinput.conf
   ```

3. **权限不足，无法注入按键**

   刷新 udev 规则并重新登录：

   ```bash
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```

4. **找不到 `steam-devices` 包（如 Fedora）**

   请确认相关仓库已启用（Fedora 通常需要 RPM Fusion）。

5. **桌面环境 / 合成器兼容性差异**

   按键注入行为可能因发行版、桌面环境、合成器实现不同而存在差异。尤其在 XWayland 下，多指触控语义可能与原生 Wayland 不同，部分手势会被当作单指序列处理。

---

## PR

欢迎提交 PR。

提交前建议：

- 保持 `README.md`（英文）与 `README.zh-CN.md`（中文）内容同步。
- 说明改动背景、行为变化与风险点。
- 若涉及 UI 改动，附截图或录屏。
- 若修改配置行为，同步更新配置与问题排查文档。

---

本项目最初受 [vboard](https://github.com/mdev588/vboard) 启发，感谢其提供的早期思路。经过完全重构后，QingBoard 已独立发展，与 vboard 在代码和功能上已有显著差异。

---

## 许可证

本项目采用 **GNU LGPL v2.1** 许可证，详见 [LICENSE](./LICENSE)。
