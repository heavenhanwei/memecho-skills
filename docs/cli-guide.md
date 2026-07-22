# CLI 使用与唤醒方式

memEcho 有两层 CLI 语义。

## 对话中的 Skill 唤醒

在支持 Agent Skills 的对话环境里，以 `memecho` 开头即可显式唤醒 Skill：

| 命令 | 功能 |
|---|---|
| `memecho analyze` | 常规完整分析：纪要、内容解析、VAD，以及身份明确时的自我回声 |
| `memecho minutes` | 摘要、共识、分歧、重点、明确动作和建议 |
| `memecho content` | 各参与者的事实主张、观点、态度与互动影响 |
| `memecho vad` | 整体或目标人物的 VAD 走向 |
| `memecho echo` | 从已确认“我”的视角分析表达影响 |
| `memecho coach` | 进入逐轮互动陪练 |
| `memecho help` | 显示帮助 |

不写子命令时，`memecho` 等同于 `memecho analyze`。自然语言参数同样有效。

常用参数：

```text
--input <附件|本地路径|->
--self <说话人姓名或 ID>
--target <说话人姓名或 ID，可用逗号分隔>
--context <meeting|interview|conversation|monologue|自定义说明>
--memory <off|ask|on>
```

## 操作系统中的 `memecho` 命令

仓库还提供一个零依赖 Python CLI，用于把输入整理成 `1.1` 请求合同，或验证请求与结果。它不执行语言模型或声学模型分析。

安装：

```bash
python -m pip install -e .
```

构造请求：

```bash
memecho minutes --input examples/meeting-transcript.txt --participants 阿青,小林
memecho vad --input examples/meeting-transcript.txt --participants 阿青,小林 --target 小林
memecho echo --input examples/meeting-transcript.txt --participants 阿青,小林 --self 阿青 --target 小林
memecho analyze --input examples/monologue.txt --context monologue
```

保存为文件：

```bash
memecho analyze --input examples/monologue.txt --context monologue --output request.json
```

校验合同：

```bash
memecho validate request examples/request-meeting.json
memecho validate result examples/result-text-only.json
```

渲染分析结果：

```bash
memecho render examples/result-text-only.json --format markdown --output report.md
memecho render examples/result-text-only.json --format html --output report.html
memecho render examples/result-text-only.json --format both --output report
```

Markdown 报告包含纯 ASCII 的可信度与 VAD 图，适合终端、GitHub 和 SkillHub。HTML 报告是 UTF-8 单文件，样式内嵌，不加载远程脚本、字体或分析服务，可直接保存并离线打开。

### 媒体输入

音频或视频路径会保留在 `source.path`，CLI 不会读取或转写媒体：

```bash
memecho analyze --input session.wav --source-type audio --participants 阿青,小林 --self 阿青
```

后续必须把请求交给具备媒体能力且得到授权的适配器。没有媒体工具时应返回 `insufficient`，而不是声称完成了声学分析。

### 身份错误

多人 `echo` 或 `coach` 没有 `--self` 时，CLI 会拒绝构造请求。单人 `monologue` 会自动创建唯一参与者“我”，并记录 `self_identity_basis: auto_single_speaker`。

