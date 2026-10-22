# Claude Desktop Sidebar

屏幕右侧的桌面侧边栏，适配 **Ubuntu 20.04 / GNOME Shell 3.36 / X11**。将系统状态、进程排行、TODO 和 QUICK NOTES 放在一列，使用 Claude 陶土橙配色和米白玻璃风格便签。

## 功能

- **SYSTEM OVERVIEW**：CPU、GPU、内存、存储和网络状态。
- **TOP PROCESSES**：CPU 与 GPU 进程排行。
- **TODO LIST**：添加、编辑、完成、删除待办。
- **QUICK NOTES**：添加、编辑、删除速记，点击复制内容。
- **侧斜卡片**：默认侧斜，先选中桌面，再悬停翻正；在其他应用内经过右侧不触发，编辑便签可继续交互。
- **按活动区显示**：勾选需要显示卡片的活动区；娱乐区可隐藏整列，切换有同步防闪现保护。
- **后台运行**：不占普通任务栏/Dock 图标，提供精确的启动、停止、重启和状态命令。

玻璃观感由半透明底色、圆角、边框和阴影实现，没有实时模糊。此包只安装侧边栏相关文件，不安装灵动岛、终端模板或 Dock 配色。

## 运行环境

目标是 GNOME Shell **3.36.x + X11**，不声明支持 GNOME 40+、Wayland 或其他桌面。Conky 布局来自高分屏环境，不同分辨率需要调整宽度、字号和位置。

Ubuntu 20.04 可用依赖：

```bash
sudo apt install conky-all gjs python3-gi gir1.2-gtk-3.0 \
  gnome-shell gnome-shell-extension-prefs fonts-ubuntu
```

离线测试还使用 Node.js。GPU 采样依赖已有的 `nvidia-smi`，当前主要适配 NVIDIA；无对应工具时显示回退值。CPU 温度读取 `coretemp`，不支持的设备可能显示默认值，不能当作实测温度。

## 安装

解压后进入 `claude-desktop-sidebar` 文件夹，在自己的普通桌面终端执行：

```bash
python3 tools/manage.py install --dry-run
python3 tools/manage.py install
```

安装命令不使用 sudo。它备份现有相关文件，保留已有笔记和活动区设置，创建用户级自启动项。第二块存储默认监控主目录所在分区；需要监控其他盘时加 `--data-mount "/挂载路径"`。

之后在 X11 按 **Alt+F2 → 输入 `r` → 回车** 重载 Shell，再运行：

```bash
python3 tools/manage.py enable
```

若已经使用完整的 **Claude Desktop Suite**，它已包含这套侧边栏，无需重复安装。本包复用同一个 `claude-desktop-effects@local` 扩展和同一套卡片数据位置，不是第二个并行控制器；已有完整桌面设置会保留。

## 设置与使用

打开“侧边栏设置”应用，或运行：

```bash
~/.local/bin/desktop-effects
```

在 **右侧卡片** 页设置角度、等待时间和翻转速度；取消“在所有活动区显示”，勾选需要保留卡片的编号。活动区按当前顺序从 1 开始编号。

新安装的示例配置只在 **活动区 2** 显示，侧斜 **72°**，移开等待 **200ms**，翻转 **259ms**；已有配置不覆盖。

为复用经过验证的动画与防闪现实现，附带的设置工具也保留了壁纸和顶栏页；**侧栏包新安装时这两项默认关闭**。它们是可选能力，不是侧边栏显示的必要条件。

后台组件管理：

```bash
python3 ~/.config/conky/minimal/scripts/widget_service.py status
python3 ~/.config/conky/minimal/scripts/widget_service.py start
python3 ~/.config/conky/minimal/scripts/widget_service.py stop
python3 ~/.config/conky/minimal/scripts/widget_service.py restart
```

只管理本套件的精确脚本和配置进程，不执行 `killall conky`。结束进程会停止显示，不会删除数据。

## 配置与位置

| 内容 | 路径 |
| --- | --- |
| 系统状态、进程卡片 | `~/.config/conky/minimal/system.conf`、`processes.conf` |
| 便签样式 | `~/.config/conky/minimal/scripts/claude-glass.css` |
| 便签布局 | `~/.config/conky/minimal/scripts/sidebar_layout.py` |
| 待办、速记 | `~/.config/conky/minimal/data/todo.json`、`notes.json` |
| 旋转与活动区配置 | `~/.config/claude-desktop-effects/settings.json` |
| 安装备份 | `~/.local/state/claude-desktop-sidebar/backups/` |
| 后台日志 | `~/.local/state/claude-desktop-sidebar/widgets.log` |

Conky 中的 `maximum_width`、`minimum_width`、`gap_x`、`gap_y` 和 `font` 控制状态卡片尺寸与位置；GTK 便签参考同列宽度与屏幕工作区域定位。仓库里的 `@DATA_MOUNT@` 在安装时替换为实际路径，不要把未经替换的 `.conf` 直接当作安装好的配置运行。

`sidebarWorkspaces: null` 表示全部活动区，`[2]` 表示仅第 2 个，`[]` 表示全部隐藏。

## 停用与恢复

```bash
python3 tools/manage.py disable
python3 tools/manage.py restore
```

`disable` 停止显示；`restore` 恢复最近一次安装前的文件，可加 `--backup /实际备份目录`。用户待办、速记始终保留。恢复后重载 Shell，再按需启用先前使用的扩展。若来自完整套件，恢复共享扩展文件后请按完整套件的方式重新启用。

## 测试与打包

```bash
bash tools/check.sh
python3 tools/build_package.py
```

测试覆盖桌面焦点、便签交互焦点、活动区筛选、防闪现、停用恢复和安装回退，不需要连接真实桌面。实际布局与硬件仍需实机检查。

产物为 `dist/claude-desktop-sidebar-v1.0.0.zip`，带 `.sha256` 校验文件；包内包含源码、文档、测试和逐文件 `MANIFEST.sha256`。不包含个人笔记、壁纸、日志、账号信息或其他桌面美化模块。

## 上传到 GitHub

建议仓库名：**`claude-desktop-sidebar`**，类型 **Public**。

Description 可直接复制 [DESCRIPTION.txt](DESCRIPTION.txt)：

> A desktop sidebar for GNOME 3.36/X11 with Claude colors, system monitors, glass notes, to-do lists, hover animations, and workspace visibility controls.

发布步骤见 [GitHub 发布说明](docs/PUBLISHING.md)，原理和排查见 [实现与排查](docs/DETAILS.md)。
