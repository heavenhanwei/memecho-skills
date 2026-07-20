# memEcho Skills

[![Validate](https://github.com/heavenhanwei/memecho-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/heavenhanwei/memecho-skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

memEcho 是一套面向会议、访谈、对话和独白的对话分析 Skill。它把内容纪要、事实/观点/态度拆解、VAD 情绪表达轨迹、自我回声与互动陪练组织为可审计的工作流。

Turn one conversation artifact into an evidence-linked report or an interactive coaching session.

> 当前仓库提供 Agent Skill、便携 JSON 合同、合同校验器和请求构造 CLI。完整音频声学分析需要另行连接获授权的 memEcho 服务或本地媒体工具；仅有文本时不会臆测音高、能量、语速或音质。

## 能做什么

- **内容纪要**：摘要、共识、未解决分歧、关注重点、明确动作和建议。
- **内容解析**：按参与者区分事实主张、观点与态度，并总结可观察的互动影响。
- **VAD 走向**：分析表达层面的 Valence、Arousal、Dominance 变化并关联证据。
- **自我回声**：从指定的“我”出发，观察表达之后的对方反应，提供低压力替代表达。
- **陪练模式**：挑选卡点，逐轮提问、等待用户作答，再按统一量表反馈。

所有重要判断都应附证据、置信度和替代解释。VAD 是对当下表达的推断，不是心理诊断，也不揭示隐藏意图。

## 快速开始

### 1. 安装为 Codex / Agent Skill

克隆仓库，把 Skill 目录复制到项目或个人 Skills 目录：

```powershell
git clone https://github.com/heavenhanwei/memecho-skills.git
Copy-Item -Recurse .\memecho-skills\skills\memecho-analyze-conversation .\.agents\skills\
```

随后在对话中直接调用：

```text
memecho analyze --input meeting.txt --self 阿青 --target 阿青,小林
memecho minutes --input meeting.txt
memecho vad --input interview.txt --target 小林
memecho echo --input meeting.txt --self 阿青
memecho coach --input meeting.txt --self 阿青
```

也可以自然语言唤醒：

```text
请使用 memEcho 分析这段会议。我的身份是阿青，重点看我和小林的分歧、我的 VAD 变化与表达影响。
```

### 2. 安装请求构造 CLI

```bash
python -m pip install -e .
memecho --help
```

CLI 将文本或媒体路径整理为便携请求 JSON，并可校验请求/结果合同；它本身不包含分析模型：

```bash
memecho analyze --input examples/meeting-transcript.txt --participants 阿青,小林 --self 阿青 --target 阿青
memecho validate request examples/request-meeting.json
memecho validate result examples/result-text-only.json
```

## 身份与输入规则

- 单人文本：唯一说话人默认视为“我”，并记录 `auto_single_speaker`。
- 多人文本：做自我回声或陪练时必须明确“我是谁”，不得按姓名、声纹、账号或发言量猜测。
- 未指定目标人物：分析所有可靠识别的参与者；`--target` 可缩小详细分析范围。
- 长期记忆默认关闭。只有用户对当前来源和范围明确授权后才可写入。

## 仓库目录

```text
memecho-skills/
├── .github/workflows/validate.yml      # 持续集成
├── docs/
│   ├── user-guide.md                   # 完整用户指南
│   ├── cli-guide.md                    # CLI 与唤醒方式
│   └── use-cases.md                    # 使用场景
├── examples/                           # 输入、请求与结果示例
├── skills/
│   └── memecho-analyze-conversation/   # Agent Skill 主体
├── src/memecho_cli/                    # 请求构造/合同校验 CLI
├── tests/                              # 自动化校验
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
└── pyproject.toml
```

## 文档

- [用户指南](docs/user-guide.md)
- [CLI 使用与唤醒方式](docs/cli-guide.md)
- [使用场景](docs/use-cases.md)
- [输入合同](skills/memecho-analyze-conversation/references/input-contract.md)
- [输出合同](skills/memecho-analyze-conversation/references/output-contract.md)
- [分析边界](skills/memecho-analyze-conversation/references/analysis-policy.md)

## 1.0 发行包

GitHub Release 附带适用于 SkillHub 等 Agent Skills 平台的 `memecho-analyze-conversation-v1.0.1.zip`。压缩包顶层直接包含 `SKILL.md`，并附 `SHA256SUMS.txt` 用于完整性校验。

```bash
python scripts/build_release.py
```

版本历史见 [CHANGELOG](CHANGELOG.md)，1.0 发布说明见 [RELEASE_NOTES_1.0.1](RELEASE_NOTES_1.0.1.md)。

## 验证

```bash
python -m unittest discover -s tests -v
python skills/memecho-analyze-conversation/scripts/validate_contract.py request examples/request-meeting.json
python skills/memecho-analyze-conversation/scripts/validate_contract.py result examples/result-text-only.json
```

## 社区参与

欢迎提交使用场景、平台适配、合同兼容性改进与安全边界修正。请先阅读 [贡献指南](CONTRIBUTING.md) 和 [行为准则](CODE_OF_CONDUCT.md)。安全或隐私问题请按 [安全政策](SECURITY.md) 私下报告。

## 许可证

[MIT License](LICENSE) © 2026 memEcho contributors.

