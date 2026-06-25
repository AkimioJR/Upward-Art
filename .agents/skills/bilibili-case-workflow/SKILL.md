---
name: bilibili-case-workflow
description: 下载 Bilibili 视频，使用 yt-dlp 获取源视频，通过 transcribe_file MCP 服务转录文本，整理视频总结，并更新 cases/ 下按序号命名的案例。适用于 Codex 需要把 Bilibili 视频沉淀为本项目案例时使用。
---

# Bilibili 案例工作流

## 概述

使用这个技能把一个 Bilibili 视频整理成本仓库中的案例：下载源视频、转录文本、总结内容，并把结果归档到 `cases/`。

## 工作流程

1. 先阅读 `AGENT.md`、`template/README.md` 和 `template/script.md`，对齐项目语气与文件结构。
2. 从视频 URL 中提取 Bilibili 视频 ID，例如 `BV1gp5X6uE22`。
3. 先运行 `scripts/prepare_case.py`，在工作区临时目录 `.tmp/bilibili-case-workflow/<BV id>/` 中创建模板文件。
4. 将视频下载到临时目录，最终文件尽量命名为 `source.mp4`。
5. 对 `source.mp4` 调用 MCP 服务 `transcribe_file` 获取文本。
6. 在 `script.md` 中填写整理后的台词、动作说明和原始 ASR 文本。
7. 在 `README.md` 中填写案例总结、技术真相、领导话术、PPT 模板和金句摘录。
8. 生成案例名后，再运行 `scripts/prepare_case.py --archive-title "<案例名>"`，把临时工作区归档为 `cases/<序号>-<案例名>/`。
9. 检查两个 Markdown 文件中的元数据，确保视频来源、日期和本次处理信息一致。

## 下载命令

使用下面的基础命令，只替换 URL 和输出路径：

```bash
uv tool run yt-dlp --cookies-from-browser edge -o ".tmp/bilibili-case-workflow/<BV id>/source.%(ext)s" "https://www.bilibili.com/video/<BV id>/"
```

如果 yt-dlp 下载出的文件不是 mp4，先确认文件是否能直接播放；只有在确认容器与内容正确后，才转换或重命名。最终案例中尽量保留 `source.mp4`。

在 Codex 沙箱中运行该命令时，需要申请提权，因为它可能访问网络、浏览器 Cookie 和 uv 缓存。

## 转录文本

使用可用的 MCP `transcribe_file` 服务处理本地 `source.mp4`。将工具返回内容作为原始转录文本，再在 `script.md` 中轻度整理标点、分段、说话人标签和动作说明。

如果当前环境没有可用的 `transcribe_file` MCP 服务，下载完成后停止，并明确告诉用户：转录步骤被缺失的 MCP 服务阻塞。

## 案例写作

以 `template/README.md` 和 `template/script.md` 为必需结构。

需要先创建案例目录时，运行 `scripts/prepare_case.py`。它会先在 `.tmp/bilibili-case-workflow/<BV id>/` 建立临时工作区，并只补齐缺失的模板文件，不覆盖已有 `README.md` 或 `script.md`。

归档时，运行 `scripts/prepare_case.py --archive-title "<案例名>"`，把临时工作区复制到 `cases/<序号>-<案例名>/`。序号按 `cases/` 中现有目录自动递增。

填写 `README.md` 时：

- 保留模板中的 YAML frontmatter 字段。
- 设置 `platform: BiliBili`、`video_id`、`url`、`summarize_model` 和 `summarize_date`。
- 根据视频的核心笑点，或“技术真相 -> 包装话术”的转换，提炼案例名称。
- 保持本仓库简洁、讽刺、程序员自嘲式的语气。
- 清楚区分真实技术实现和面向 PPT 的夸张包装。

填写 `script.md` 时：

- 保留模板中的 YAML frontmatter 字段。
- 如果 MCP 返回了模型信息，将 `asr_model` 设置为对应模型；否则使用工具输出中可见的服务名或模型名。
- 临时处理阶段，可将 `local_filepath` 写成 `.tmp/bilibili-case-workflow/BV1gp5X6uE22/source.mp4`。
- 归档后，把 `local_filepath` 更新为最终目录路径，例如 `cases/001-太极加密/source.mp4`。
- 在 `## 视频脚本` 下写入可读性更好的整理版本。
- 在 `## 原文` 下写入未经改写的 ASR 原文。

## 更新规则

- 不要盲目覆盖用户已经整理过的内容；先阅读现有文件，保留有价值的人工修订。
- 不要改动无关案例。
- 日期统一使用 `YYYY-MM-DD` 格式。
