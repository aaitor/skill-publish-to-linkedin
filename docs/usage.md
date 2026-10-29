# Usage and command reference

### With your agent

Ask in plain language. For example:

- "Post on LinkedIn: *We just shipped dark mode. Thanks to everyone who asked for it! #product*"
- "Write a short LinkedIn post about our talk at DevConf and publish it with this image: ./slides/cover.png"
- "Share this on LinkedIn, visible to my connections only: ..."
- "Delete this LinkedIn post: https://www.linkedin.com/feed/update/urn:li:share:7521.../"
- "Is my LinkedIn token still valid?"

The agent follows the workflow in [`SKILL.md`](../SKILL.md):

1. Checks authorization.
2. Drafts the text, using a writing-voice or style skill if you have one.
3. Runs a dry run and shows you the exact post.
4. Publishes only after you explicitly approve that text.
5. Returns the post URL.

Scheduled or automated runs follow the same rule: they publish only text you approved word for word when you set them up.

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

## Limitations

- Posts go to **your personal profile** only. Company Page posts need the `w_organization_social` scope, which requires LinkedIn approval.
- **No direct messages or InMail.** LinkedIn's Messaging API is not available to self-serve apps.
- **No reading posts back** (`r_member_social` is restricted to approved partners), so the agent cannot list or edit existing posts.
- **No scheduling on LinkedIn's side.** Use your agent's scheduler with pre-approved text.
- **Not supported:** video, documents, polls, multi-image posts and link-preview cards.
