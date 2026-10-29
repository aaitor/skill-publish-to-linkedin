# Installation and authorization

Requires Python 3.9+ and Git. The CLI has been tested on Linux; macOS and Windows have not been verified here. Use `python` if `python3` is not on your PATH.

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

In this guide, `<skill-dir>` means the directory you cloned into. To update later, run `git -C <skill-dir> pull`.

## Create a LinkedIn app

1. Open <https://www.linkedin.com/developers/apps/new>. Enter an app name, select your LinkedIn Page, upload a logo and accept the terms. The app name is shown on the consent screen.
2. On the **Products** tab, request **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**. Both are self-serve and approved instantly.
3. On the **Auth** tab:
   - Under *Authorized redirect URLs*, add exactly `http://localhost:8765/callback`.
   - Copy the **Client ID** and the **Primary Client Secret**.
   - Check that *OAuth 2.0 scopes* lists `openid`, `profile` and `w_member_social`.

If LinkedIn asks you to verify the app, use the *Verify* button on the **Settings** tab and have a Page admin approve it. If you own the Page, that admin is you.

## Comment access

Comments and first comments require **Community Management API** access and the `w_member_social_feed` OAuth scope, as listed in the official [Comments API permissions](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/comments-api). The self-serve Share on LinkedIn setup above enables posts only. Community Management requires LinkedIn approval; requesting a scope does not grant product access.

After your app is approved and its Auth tab lists `w_member_social_feed`, authorize with:

```bash
python3 <skill-dir>/scripts/linkedin.py auth --with-comments
```

This requests the existing post/identity scopes plus `w_member_social_feed`. Default `auth` keeps its original scopes, so it still works for apps without Community Management. Use `auth --with-comments` when renewing a comment-enabled token. The CLI records granted scopes, shows comment scope status in `status`, and refuses live comment workflows before publishing anything if the saved token lacks the comment scope. Tokens saved by older versions need reauthorization. Dry runs still work without the comment scope.

## Configuration

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

## Authorize

Run this in your terminal, or ask the agent to "check my LinkedIn setup":

```bash
python3 <skill-dir>/scripts/linkedin.py auth
```

Your browser opens LinkedIn's consent screen. After you approve it, the token is saved to `~/.config/linkedin-publisher/token.json`.

LinkedIn does not issue refresh tokens to self-serve apps, so the token **expires after 60 days**. When it does, run `auth` again. The agent offers to do this when it sees an expired token. Run `status` to see how many days are left.

**Sandboxed agents (for example Codex):** `auth` opens a browser, listens on `localhost:8765` and writes to `~/.config`, which a sandbox usually blocks. Run `auth` in your own terminal.

**Remote machine (SSH):** the consent redirect goes to `localhost:8765` on the machine running the script. Connect with `ssh -L 8765:localhost:8765 <host>`, run `auth`, and open the printed URL in your local browser.
