# memEcho Skills 1.0.1

This patch release improves marketplace validation and OpenClaw compatibility without expanding the Skill's default permissions.

## Changes

- Added explicit permissions and safety boundaries to `SKILL.md`.
- Added OpenClaw metadata using its single-line JSON frontmatter format.
- Declared that the core text workflow has no required binaries, environment variables, or network access.
- Documented conditional media/service access and actions that remain prohibited without separate authorization.
- Preserved the portable request/result contract at schema version `1.1`.

Use `memecho-analyze-conversation-v1.0.1.zip` for SkillHub, ClawHub, and other Agent Skills-compatible marketplaces. Verify the archive with the attached `SHA256SUMS.txt`.
