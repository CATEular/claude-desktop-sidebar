# 实现与排查

## 组件

- 两个 Conky desktop 窗口显示状态和进程，使用 `skip_taskbar` / `skip_pager` 等属性。
- GTK3 utility 窗口承载 TODO 和 QUICK NOTES，数据为本地 JSON，横向尺寸受限。
- Shell 扩展用精确窗口标题识别自己的卡片，围绕右边缘旋转。默认每 80ms 检查鼠标，焦点变化时立即判断桌面是否仍被选中。
- 在未勾选的活动区隐藏 Conky，并最小化 GTK 便签以移除点击区域；同步维护零不透明度，拦截 Mutter 重新显示/重设不透明度的事件，避免等下一次轮询导致闪现。
- 回到选中的活动区和停用时恢复之前的 pivot、旋转、可见性与不透明度，不处理其他普通窗口。
- 后台采样写入 `/dev/shm/conky_minimal`，不包含联网服务。

扩展 UUID 沿用完整套件的 `claude-desktop-effects@local`，避免两个控制器同时修改同一列卡片。侧栏包的新配置关闭壁纸和顶栏功能，现有配置则原样保留。

## 常见问题

**什么都没显示**：先检查是否切到了活动区 2，或打开设置勾选当前活动区。再用 `widget_service.py status` 查看组件是否在运行，检查日志。

**鼠标悬停没有翻正**：先点击桌面空白处。普通应用仍被选中时不触发，属于预期行为。编辑便签允许继续操作。

**更新后仍闪一下或仍是旧效果**：关闭旧设置窗口，X11 按 `Alt+F2 → r`，重新打开。GNOME 会缓存 JavaScript，禁用/启用不一定刷新模块。

**字太大、卡片超出屏幕**：调整两个 Conky `.conf` 的宽度、字号和纵向偏移；GTK 便签参考系统卡片宽度，具体定位在 `sidebar_layout.py`。不同分辨率、多显示器、不同 scale factor 需要验收。

**GPU/温度读数不准确**：采样器针对 NVIDIA 和 Intel `coretemp`。缺少这些数据源时会显示回退值，需要按设备适配，不能将默认值当作实测。

**窗口没有 Dock 图标是否就没运行**：不是。卡片是后台窗口，按任务栏隐藏属性工作。结束进程会结束显示，数据不删除。

**安装器连接桌面失败**：在真实 GNOME 3.36 / X11 会话中的普通终端运行。不要用 sudo 或无会话 SSH。`install --dry-run` 只做离线预览，不代表已安装。

## 来源与许可

运行依赖包括 [Conky](https://github.com/brndnmtthws/conky)、GTK3、GJS 和 [GNOME Shell](https://gitlab.gnome.org/GNOME/gnome-shell)，不打包这些第三方二进制或主题素材。

本项目从 Claude Desktop Suite 中拆分已有侧栏实现，原创代码尚未单独附加通用开源许可证；公开源码不改变第三方组件各自的许可。
