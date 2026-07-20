# Platform adapters

The canonical skill contains behavior and contracts. Each adapter handles discovery, attachments, tools, asynchronous jobs, and rendering.

## Capability matrix

| Platform | Skill surface | Recommended installation | Full audio path |
|---|---|---|---|
| OpenAI Codex desktop/CLI/IDE | Agent Skills | Repository `.agents/skills/`, user `~/.agents/skills/`, or plugin | memEcho MCP server or approved local media tool |
| Claude Code | Filesystem skills | Project `.claude/skills/` or user `~/.claude/skills/` | Local/network-capable tool or MCP connection |
| Claude API / claude.ai | Uploaded custom skill | Upload for that surface | Separately registered memEcho tool; do not rely on code-execution network access |
| Kimi Work | `/` invocation or automatic matching | Current Kimi Work skill import surface | Supported local tool or memEcho service adapter |
| OpenClaw | AgentSkills-compatible skill | Workspace `skills/`, project `.agents/skills/`, personal `~/.agents/skills/`, or plugin/ClawHub | memEcho plugin/MCP or approved local binary |

Claude surfaces do not automatically synchronize uploaded skills. Confirm Kimi Work's exact packaging format during adapter implementation; preserve the portable contracts even if metadata differs.

## Adapter interface

```text
analyze_text(request) -> result | job
analyze_media(request, media_handle) -> result | job
get_analysis_job(job_id) -> status
get_analysis_result(job_id) -> result
write_memory(result_id, consent) -> receipt
delete_memory_source(source_id) -> receipt
```

Memory tools remain separate so analysis cannot silently become a persistent profile.

## Fidelity negotiation

Adapters expose capabilities such as media reading, transcription, acoustic extraction, memEcho service access, and memory persistence. The skill selects the highest mode and records missing signals. “Same effect” means the same report semantics and evidence policy; numerically comparable acoustic results require the same memEcho service/model manifest.

## Official references

- Agent Skills specification: https://agentskills.io/specification
- OpenAI Codex skills: https://learn.chatgpt.com/docs/build-skills
- Claude Agent Skills: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Kimi Work: https://www.kimi.com/products/kimi-work
- Kimi Skills: https://www.kimi.com/help/agent/what-are-skills
- OpenClaw skills: https://docs.openclaw.ai/skills
