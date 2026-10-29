<p align="center">
  <img src="https://raw.githubusercontent.com/aaitor/assets/26be4ac7da293f2afd2252f5370359e7a4e82b1d/banners/skill-publish-to-linkedin.svg" alt="Publish to LinkedIn — draft, preview, and publish with your AI agent" width="100%">
</p>

<h1 align="center">Publish to LinkedIn</h1>
<p align="center">Draft, preview, and publish with your AI agent.</p>
<p align="center"><a href="https://github.com/aaitor/skill-publish-to-linkedin/releases/tag/v1.0">v1.0 release</a></p>
<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="docs/installation.md">Setup</a> ·
  <a href="docs/usage.md">Usage</a> ·
  <a href="#contributing-and-support">Contribute</a>
</p>
<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-89E5CC?style=flat-square&amp;labelColor=101827" alt="MIT license"></a>
  <a href="https://github.com/aaitor/skill-publish-to-linkedin/actions/workflows/quality.yml"><img src="https://github.com/aaitor/skill-publish-to-linkedin/actions/workflows/quality.yml/badge.svg" alt="Offline tests and documentation checks"></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square" alt="Python 3.9 or later">
</p>

An [Agent Skill](https://agentskills.io) for publishing to **your personal LinkedIn profile**, using your own account and the official [LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api). Works with Claude Code, Codex, and other compatible agents. The CLI uses Python's standard library; there are no runtime packages to install.

## Demo

![Install the skill and ask Claude Code to preview a LinkedIn message](assets/terminal-demo.gif)

Install the skill, invoke **Claude Code** with `/publish-to-linkedin`, and review its draft and publishing approval prompt. This is a real Claude Code session using the installed skill and saved LinkedIn authorization, on a black terminal background. It stops before approval; nothing is published. See the [recording guide](examples/README.md) to reproduce it.

## Quick start

**Prerequisites:** Python 3.9+ and Git. Try the offline example before configuring an account:

```bash
git clone https://github.com/aaitor/skill-publish-to-linkedin.git
cd skill-publish-to-linkedin
python3 examples/offline_preview.py
```

Expected result: a JSON post payload for `urn:li:person:EXAMPLE`, followed by `DRY RUN: nothing published`.

To publish with your own identity:

1. [Install the skill](docs/agent-setup.md) in your agent's skills directory.
2. [Create a LinkedIn app and configure credentials](docs/installation.md#create-a-linkedin-app). A LinkedIn account and a Page you administer are required for app setup; posts go to your personal profile.
3. Run `python3 <skill-dir>/scripts/linkedin.py auth` and approve browser consent.
4. Ask your agent to draft a post. Review the exact text and image, then approve publishing.

You can also use the [CLI directly](docs/usage.md#command-line). Its publishing commands execute immediately; use `--dry-run` when you want a preview. Normal CLI dry runs need your saved author token. The offline example is a separate credential-free exercise; the demo above uses a real authorized account.

## Features

- **Text and one image:** hashtags, inline links, and one JPG/PNG/GIF with alt text.
- **First comments:** publish links in a comment immediately after a post, or add a comment to an existing post.
- **Visibility:** public or connections-only posts.
- **Preview and approval:** the skill shows the exact draft and publishes only after explicit approval.
- **Text escaping:** preserves characters that LinkedIn's text format treats specially.
- **Own-account publishing and deletion:** uses your authorized personal profile.
- **No runtime dependencies:** one Python CLI and an open `SKILL.md` entrypoint.

Personal profiles only; no Company Page publishing, DMs, video, documents, polls, multi-image posts, or link-preview cards. Post text is limited to 3,000 characters. See [usage and limitations](docs/usage.md).

## Examples

With the skill installed, ask your agent:

```text
Draft a short LinkedIn post about our open-source release.
Show me the exact text and a dry-run preview before publishing.
```

For a CLI preview after authorization, run from this repository:

```bash
python3 scripts/linkedin.py post --file examples/post.txt --dry-run
```

See [examples/](examples/README.md) for the Claude Code recording and a separate offline exercise, and [usage](docs/usage.md) for image posts, connections-only visibility, mentions, and deletion.

## Configuration

Keep app credentials in `~/.config/linkedin-publisher/credentials.env` or the environment. Authorization writes the member token separately to `~/.config/linkedin-publisher/token.json`.

| Setting | Purpose |
| --- | --- |
| `LINKEDIN_CLIENT_ID` | Your app client ID |
| `LINKEDIN_CLIENT_SECRET` | Your app secret; needed for authorization |
| `LINKEDIN_VERSION` | API version override; implementation default is `202610` |

Follow [configuration and authorization](docs/installation.md#configuration) for file permissions and token renewal. Keep secrets out of chat, issues, commits, and demo recordings. See [security and privacy](docs/security-and-privacy.md) for scopes and local storage.

## How it works

The agent reads [SKILL.md](SKILL.md), drafts your post, invokes the CLI to preview it, and asks for approval. After approval, the CLI sends the request to LinkedIn and returns the published URL. Credentials remain local; there is no hosted backend. Read the [architecture](docs/architecture.md) for details.

## Documentation

- [Installation, app setup, configuration, and authorization](docs/installation.md)
- [Agent installation and network access](docs/agent-setup.md)
- [Command reference, writing tips, and limitations](docs/usage.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Security and privacy](docs/security-and-privacy.md)
- [Banner generation and social preview](docs/branding.md)

## Contributing and support

Questions, bugs, and feature ideas belong in [Issues](https://github.com/aaitor/skill-publish-to-linkedin/issues). See [CONTRIBUTING.md](CONTRIBUTING.md) and the [code of conduct](CODE_OF_CONDUCT.md). Report vulnerabilities privately using [SECURITY.md](SECURITY.md).

Run `python3 scripts/test_linkedin.py` and `python3 scripts/check.py` before submitting changes. Both run offline; never use a real account to test publishing as part of CI. Changes are recorded in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE). Embedded banner fonts retain their [SIL OFL 1.1 notices](assets/font-notices/NOTICE.md). This project is not affiliated with or endorsed by LinkedIn, Anthropic, or OpenAI.

---

Built by [Aitor Argomaniz](https://github.com/aaitor) · [LinkedIn](https://www.linkedin.com/in/aitorargomaniz) · [More open source](https://github.com/aaitor?tab=repositories)
