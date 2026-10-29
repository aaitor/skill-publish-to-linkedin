# How it works

```text
Agent reads SKILL.md
  → drafts text and asks the CLI for a dry-run payload
  → shows the exact post and asks for approval
  → calls the LinkedIn Posts API only after approval
  → returns the published post URL
```

`scripts/linkedin.py` is the complete CLI implementation. It uses Python's standard library, the official LinkedIn REST endpoints, and a browser OAuth callback on `http://localhost:8765/callback`. There is no hosted backend.

Credentials and the member token are stored separately under `~/.config/linkedin-publisher/`. The CLI reads credentials from the file or environment during authorization. The agent workflow is defined in [SKILL.md](../SKILL.md); the CLI can also be used directly.

The approval gate is an agent instruction. Direct CLI publishing commands execute immediately; `--dry-run` prints the request payload and returns before image upload or post creation. Even a normal dry run needs a saved token for the author identity. The separate [offline example](../examples/offline_preview.py) replaces only token loading with a clearly labeled fixture and blocks network calls while exercising the real CLI parser and dry-run behavior.

See [security and privacy](security-and-privacy.md) for storage, scopes, and revocation, and [usage](usage.md) for supported commands and limitations.

The [README recording](../examples/README.md) uses the real skill instructions and unmodified CLI with a saved authorized account. Its status check calls LinkedIn; the preview uses `--dry-run`. A stdout filter redacts the member ID only. This live recording is regenerated manually and is never run in CI.
