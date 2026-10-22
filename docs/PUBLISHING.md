# 发布到 GitHub

1. 在 GitHub 新建仓库：名称 `claude-desktop-sidebar`，选择 **Public**，勾选初始化 README。
2. Description 粘贴根目录 `DESCRIPTION.txt` 的一行英文。
3. 解压 `claude-desktop-sidebar-v1.0.0.zip`，通过 **Add file → Upload files** 上传里面的文件和文件夹，让仓库根目录直接出现 README、extensions、desktop、tools 等；不要多套一层同名目录。
4. 提交后进入 **Releases → Draft a new release**。
5. 标签填 `v1.0.0`，标题填 `Claude Desktop Sidebar v1.0.0`。
6. 附上 ZIP 及同目录的 `.sha256` 校验文件，复制下面的说明，点击 **Publish release**。

```markdown
屏幕右侧桌面侧边栏，适配 GNOME Shell 3.36 / X11。

- CPU/GPU/内存/存储/网络状态和进程排行。
- 米白玻璃风格 TODO LIST 与 QUICK NOTES，支持编辑、完成和复制。
- 仅桌面获得焦点时悬停翻正，可按活动区显示，并有切换防闪现保护。
- 后台启动、安装备份、恢复工具和完整说明。

不包含灵动岛、终端或 Dock 美化，不包含个人笔记和壁纸。
请先阅读 README，确认运行环境和硬件采样适配范围。
```

这是源码与配置包，浏览器上传不需要密钥。原始 ZIP 用于 Release 下载，解压后的源码用于仓库浏览。完整桌面套件已经包含此侧栏，不必重复安装。
