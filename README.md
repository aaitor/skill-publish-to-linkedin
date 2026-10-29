# Publish to LinkedIn: an Agent Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![Dependencies: none](https://img.shields.io/badge/dependencies-none-brightgreen)
[![Agent Skills](https://img.shields.io/badge/format-Agent%20Skills-purple)](https://agentskills.io)

An [Agent Skill](https://agentskills.io) that lets your AI agent write and publish posts on **your personal LinkedIn profile**, using your own account and the official [LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api).

It works with any agent that supports the open `SKILL.md` format. It has been tested with **Claude Code** and **OpenAI Codex**.

```text
You:    Write a LinkedIn post announcing our v2 release and publish it with ./cover.png
Agent:  [drafts the post, shows a dry-run preview] Publish it as is?
You:    yes
Agent:  Published: https://www.linkedin.com/feed/update/urn:li:share:7521.../
```

## Features

- **Text posts** with hashtags, line breaks and inline links, up to 3000 characters.
- **One image per post** (JPG, PNG or GIF) with alt text.
- **Public or connections-only** visibility.
- **Delete** your own posts by URL.
- **Dry-run preview and an approval gate**: the agent shows you the exact post and publishes only after you approve it.
- **Automatic escaping** for LinkedIn's text format, so parentheses, underscores and `@` don't silently truncate your post.
- **No dependencies:** one Python script using only the standard library. It talks only to LinkedIn.

## How it works

```text
agent ──> scripts/linkedin.py ──> LinkedIn REST API (/rest/posts, /rest/images)
               │
               └── ~/.config/linkedin-publisher/
                     credentials.env   your LinkedIn app's client ID and secret (you create this)
                     token.json        60-day access token (written by `auth`, mode 600)
```

You create your own LinkedIn developer app once (free and self-serve). You authorize it in the browser, and the script stores the access token locally. The agent reads `SKILL.md` and calls the script to preview, publish or delete posts. Because the logic lives in a plain CLI, you can also use it without an agent.

## Requirements

- Python 3.9 or later. Tested on Linux; macOS and Windows should work (use `python` if `python3` is not on your `PATH`).
- A LinkedIn account and a **LinkedIn Page** you administer. LinkedIn requires every developer app to be linked to a Page. Posts still go to your personal profile, and a newly created Page works.
- An agent that supports [Agent Skills](https://agentskills.io), such as Claude Code or OpenAI Codex. This is optional if you only use the CLI.

## 1. Install

Clone the repository into your agent's skills directory:

| Agent | Personal (all projects) | One project only |
|---|---|---|
| Claude Code | `~/.claude/skills/publish-to-linkedin` | `<project>/.claude/skills/publish-to-linkedin` |
| OpenAI Codex | `~/.agents/skills/publish-to-linkedin` | `<project>/.agents/skills/publish-to-linkedin` |
| Other agents | Your tool's skills directory (see its docs and the [client list](https://agentskills.io/clients)) | |

```bash
# Example: Codex
git clone https://github.com/aaitor/skill-publish-to-linkedin.git ~/.agents/skills/publish-to-linkedin

# Using more than one agent? Clone once and symlink, for example for Claude Code:
ln -s ~/.agents/skills/publish-to-linkedin ~/.claude/skills/publish-to-linkedin
```

In the rest of this README, `<skill-dir>` means the directory you cloned into. To update later, run `git -C <skill-dir> pull`.

## 2. Create a LinkedIn app

1. Open <https://www.linkedin.com/developers/apps/new>. Enter an app name, select your LinkedIn Page, upload a logo and accept the terms. The app name is shown on the consent screen.
2. On the **Products** tab, request **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**. Both are self-serve and approved instantly.
3. On the **Auth** tab:
   - Under *Authorized redirect URLs*, add exactly `http://localhost:8765/callback`.
   - Copy the **Client ID** and the **Primary Client Secret**.
   - Check that *OAuth 2.0 scopes* lists `openid`, `profile` and `w_member_social`.

If LinkedIn asks you to verify the app, use the *Verify* button on the **Settings** tab and have a Page admin approve it. If you own the Page, that admin is you.

## 3. Configuration

Store the credentials in `~/.config/linkedin-publisher/credentials.env`, readable only by you:

```bash
mkdir -p -m 700 ~/.config/linkedin-publisher
touch ~/.config/linkedin-publisher/credentials.env
chmod 600 ~/.config/linkedin-publisher/credentials.env
"${EDITOR:-nano}" ~/.config/linkedin-publisher/credentials.env
```

```bash
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-primary-client-secret
```

The file uses plain `KEY=VALUE` lines, optionally prefixed with `export`. Comments and quotes are fine. If you already keep these values in another env file, symlink it to this path. Environment variables with the same names take precedence over the file.

The client secret is only used during `auth`. Do not paste it into the agent chat.

| Setting | Default | Purpose |
|---|---|---|
| `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET` | none | Your app credentials (file or environment) |
| `LINKEDIN_VERSION` | `202610` | LinkedIn API version (`YYYYMM`). LinkedIn retires each version about 12 months after release. |

## 4. Authorize

Run this in your terminal, or ask the agent to "check my LinkedIn setup":

```bash
python3 <skill-dir>/scripts/linkedin.py auth
```

Your browser opens LinkedIn's consent screen. After you approve it, the token is saved to `~/.config/linkedin-publisher/token.json`.

LinkedIn does not issue refresh tokens to self-serve apps, so the token **expires after 60 days**. When it does, run `auth` again. The agent offers to do this when it sees an expired token. Run `status` to see how many days are left.

**Sandboxed agents (for example Codex):** `auth` opens a browser, listens on `localhost:8765` and writes to `~/.config`, which a sandbox usually blocks. Run `auth` in your own terminal.

**Remote machine (SSH):** the consent redirect goes to `localhost:8765` on the machine running the script. Connect with `ssh -L 8765:localhost:8765 <host>`, run `auth`, and open the printed URL in your local browser.

## Usage

### With your agent

Ask in plain language. For example:

- "Post on LinkedIn: *We just shipped dark mode. Thanks to everyone who asked for it! #product*"
- "Write a short LinkedIn post about our talk at DevConf and publish it with this image: ./slides/cover.png"
- "Share this on LinkedIn, visible to my connections only: ..."
- "Delete this LinkedIn post: https://www.linkedin.com/feed/update/urn:li:share:7521.../"
- "Is my LinkedIn token still valid?"

The agent follows the workflow in [`SKILL.md`](SKILL.md):

1. Checks authorization.
2. Drafts the text, using a writing-voice or style skill if you have one.
3. Runs a dry run and shows you the exact post.
4. Publishes only after you explicitly approve that text.
5. Returns the post URL.

Scheduled or automated runs follow the same rule: they publish only text you approved word for word when you set them up.

### Network access in Codex

Codex runs commands in a sandbox with **no network access by default**, so the skill reports `Cannot reach LinkedIn`. In an interactive session, Codex may ask to rerun the command outside the sandbox; approve it. To avoid the prompt, enable network access for the sandbox:

```bash
codex --sandbox workspace-write -c sandbox_workspace_write.network_access=true
```

To make it permanent, add this to `~/.codex/config.toml`:

```toml
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
```

Claude Code needs no extra setup. It asks for permission before running commands, according to your permission settings.

### Command line

```bash
LI="python3 <skill-dir>/scripts/linkedin.py"

$LI status
$LI post --file post.txt --dry-run
$LI post --file post.txt --image cover.png --alt "Team photo at DevConf"
$LI post --text "Short update #AI" --visibility CONNECTIONS
echo "Text from a pipe" | $LI post --file -
$LI delete https://www.linkedin.com/feed/update/urn:li:share:7000000000000000000/
```

| Command | Options | Description |
|---|---|---|
| `auth` | | Browser OAuth consent. Saves a 60-day token. |
| `status` | | Shows the authorized account and token expiry (checks the token live). |
| `post` | `--text TEXT` or `--file PATH` (`-` reads stdin) | Text of the post. One of the two is required. |
| | `--image PATH`, `--alt TEXT` | Attach one JPG, PNG or GIF, with alt text. |
| | `--visibility PUBLIC\|CONNECTIONS` | Default `PUBLIC`. |
| | `--raw` | Send the text without escaping, for mentions (see below). |
| | `--dry-run` | Print the request payload and publish nothing. |
| `delete` | `POST` (post URL or URN) | Delete one of your own posts. |

### Writing tips

- **Formatting:** LinkedIn does not render Markdown. Use line breaks for structure.
- **Hashtags:** write them plainly (`#AI`). They become clickable.
- **Special characters** such as `( ) [ ] @ _ * < > { } | ~` are escaped automatically.
- **Mentions:** use `@[Exact Name](urn:li:person:ID)` or `@[Company](urn:li:organization:ID)` together with `--raw`. With `--raw` you must escape every other special character yourself (`\(`, `\_`, ...). The name must match the profile or Page name exactly.
- **Links:** put them in the text. The API does not build link-preview cards.

## Security and privacy

- **Scopes:** the app requests only `openid` and `profile` (to identify you as the post author) and `w_member_social` (to create and delete your posts). It cannot read your feed, messages or connections.
- **Local storage:** credentials and tokens stay on your machine in `~/.config/linkedin-publisher/`. The script creates `token.json` with mode `600` and warns if `credentials.env` is readable by others.
- **Network:** requests go only to `linkedin.com` and its upload endpoints. Sign-in uses a random `state` value to protect against cross-site request forgery.
- **Approval:** the skill instructs the agent never to publish without your explicit approval of the exact text.
- **Revoking access:** remove the app from LinkedIn's [Permitted services](https://www.linkedin.com/mypreferences/d/permitted-services) settings and delete `~/.config/linkedin-publisher/token.json`.

Use it in line with LinkedIn's [User Agreement](https://www.linkedin.com/legal/user-agreement) and [API Terms of Use](https://www.linkedin.com/legal/l/api-terms-of-use). Don't use it for spam or mass posting.

## Limitations

- Posts go to **your personal profile** only. Company Page posts need the `w_organization_social` scope, which requires LinkedIn approval.
- **No direct messages or InMail.** LinkedIn's Messaging API is not available to self-serve apps.
- **No reading posts back** (`r_member_social` is restricted to approved partners), so the agent cannot list or edit existing posts.
- **No scheduling on LinkedIn's side.** Use your agent's scheduler with pre-approved text.
- **Not supported:** video, documents, polls, multi-image posts and link-preview cards.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Browser shows *redirect_uri does not match* | Add exactly `http://localhost:8765/callback` under Auth → *Authorized redirect URLs*. |
| Browser shows *unauthorized_scope_error* | Add both products on the **Products** tab, then run `auth` again. |
| `Missing LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET` | Create `credentials.env` (see [Configuration](#3-configuration)). |
| `Cannot reach LinkedIn` | No network, or the agent's sandbox blocks it (see [Network access in Codex](#network-access-in-codex)). |
| `Timed out waiting for the LinkedIn redirect` | Approve within 5 minutes. On a remote host, use the SSH tunnel described above. |
| `Address already in use` during `auth` | Another process is using port 8765. Stop it and retry. |
| `LinkedIn 401` | The token expired or was revoked. Run `auth`. |
| `LinkedIn 403 ACCESS_DENIED` | The token lacks `w_member_social`. Add *Share on LinkedIn* and run `auth` again. |
| `LinkedIn 404` on `delete` | The post is already deleted, or the URL is not one of your posts. |
| `LinkedIn 422 ...` | The message names the invalid field, for example text that is too long. |
| Error about the API version | The pinned version was retired. Set `LINKEDIN_VERSION` to a recent `YYYYMM`. |
| Post appears cut off | You used `--raw` without escaping special characters. Remove `--raw` or escape them. |
| The agent doesn't use the skill | Check the install path for your agent (see [Install](#1-install)), restart the agent, and mention "LinkedIn" in your request. |

## Development

```text
SKILL.md                 instructions the agent loads (Agent Skills format)
scripts/linkedin.py      CLI: auth, status, post, delete
scripts/test_linkedin.py self-checks (escaping, payloads, credentials parsing)
```

Run the tests with `python3 scripts/test_linkedin.py` (prints `ok`). Issues and pull requests are welcome.

## License

[MIT](LICENSE). This project is not affiliated with or endorsed by LinkedIn, Anthropic or OpenAI.
