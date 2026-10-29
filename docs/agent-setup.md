# Install and run with your agent

Clone into your agent's personal or project skills directory. The existing project has been tested with Claude Code and Codex; other clients can use the Agent Skills format.

| Agent | Personal skills | Project skills |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/publish-to-linkedin` | `.claude/skills/publish-to-linkedin` |
| Codex | `~/.agents/skills/publish-to-linkedin` | `.agents/skills/publish-to-linkedin` |

```bash
git clone https://github.com/aaitor/skill-publish-to-linkedin.git ~/.agents/skills/publish-to-linkedin
```

Restart or reload your client as needed and ask it to check your LinkedIn setup. Keep the entire repository together: `SKILL.md` routes to the bundled CLI and setup documentation.

## Authorization and network access

Publishing and status checks need access to LinkedIn. Browser authorization also opens a localhost callback and writes the token under `~/.config/linkedin-publisher/`. Agent sandbox and approval settings vary; allow the required access in your client or run `auth` in your own terminal. Do not disable unrelated protections to run this skill.

For remote machines, use the SSH tunnel in the [authorization guide](installation.md#authorize). See [troubleshooting](troubleshooting.md) for connection and token errors.

The skill's approval gate applies independently of your client's command permissions: approve the exact post text and image before the agent publishes. Installing the skill does not authorize posting or deleting content.
