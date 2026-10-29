# Real skill demo

The README animation records the repository's `SKILL.md` workflow using Aitor's authorized LinkedIn account. It shows the actual skill instructions, a live status check, the draft text, and the real CLI dry-run. There are no fixture identities or mocked API calls in the recording. It stops at the preview stage before publishing approval.

The only output transformation is [redact.py](redact.py), which replaces the personal LinkedIn member ID with `[redacted]`. It does not read credentials, patch the skill, or change the post payload. The status check contacts LinkedIn; dry-run loads the saved author identity and prints the payload without uploading or publishing.

## Reproduce with your own account

Complete [installation and authorization](../docs/installation.md) first. From the repository root:

```bash
# Read the actual skill workflow.
sed -n '6,15p' SKILL.md

# Validate your saved authorization against LinkedIn.
python3 scripts/linkedin.py status | python3 examples/redact.py

# Inspect the draft that will be previewed.
cat examples/demo-post.txt

# Run the unmodified CLI using your saved author identity.
python3 scripts/linkedin.py post --file examples/demo-post.txt --dry-run | python3 examples/redact.py
```

Expected result: a successful status check for your account, then a JSON payload with redacted author ID, the escaped draft, visibility `PUBLIC`, and `DRY RUN: nothing published`. The payload's `lifecycleState: PUBLISHED` is the value that would be submitted if approved; dry-run returns before sending it.

## Record the animation

Install [VHS and its prerequisites](https://github.com/charmbracelet/vhs#installation), including `ttyd` and `ffmpeg`, plus DejaVu Sans Mono or a substitute font. With Python 3.9+ and a valid saved LinkedIn token, run:

```bash
vhs examples/demo.tape
```

The tape records the commands above directly and writes `assets/terminal-demo.gif`. It imports the shared terminal theme from `aaitor/assets`. Watch the result before committing it; it contains your account name, token expiry, and draft text. The ID filter does not anonymize those other details.

## Credential-free CLI example

For a separate offline exercise or CI, run:

```bash
python3 examples/offline_preview.py
```

This uses [sample post text](post.txt), a fixture identity, and blocked network requests. It is useful for trying the payload format without credentials, but it is **not the workflow recorded in the README GIF**. The real recording uses [demo-post.txt](demo-post.txt) and the actual saved identity.
