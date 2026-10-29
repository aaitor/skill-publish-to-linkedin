# Usage and command reference

### With your agent

Ask in plain language. For example:

- "Post on LinkedIn: *We just shipped dark mode. Thanks to everyone who asked for it! #product*"
- "Write a short LinkedIn post about our talk at DevConf and publish it with this image: ./slides/cover.png"
- "Share this on LinkedIn, visible to my connections only: ..."
- "Delete this LinkedIn post: https://www.linkedin.com/feed/update/urn:li:share:7521.../"
- "Publish this update with the project link in the first comment: https://example.com/project"
- "Add this comment to my LinkedIn post <post URL>: Read more at https://example.com"
- "Is my LinkedIn token still valid?"

The agent follows the workflow in [`SKILL.md`](../SKILL.md):

1. Checks authorization.
2. Drafts the text, using a writing-voice or style skill if you have one.
3. Runs a dry run and shows you the exact post and any first comment.
4. Publishes only after you explicitly approve the post and any comment text.
5. Returns the post URL.

Scheduled or automated runs follow the same rule: they publish only post and comment text you approved word for word when you set them up.

### Command line

```bash
LI="python3 <skill-dir>/scripts/linkedin.py"

$LI status
$LI post --file post.txt --dry-run
$LI post --file post.txt --first-comment-file links.txt --dry-run
$LI post --file post.txt --first-comment "Read more: https://example.com/project"
$LI comment urn:li:share:7000000000000000000 --file links.txt --dry-run
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
| | `--first-comment TEXT` or `--first-comment-file PATH` | Add a comment immediately after publishing. File accepts `-` for stdin, unless post text also uses stdin. |
| | `--image PATH`, `--alt TEXT` | Attach one JPG, PNG or GIF, with alt text. |
| | `--visibility PUBLIC\|CONNECTIONS` | Default `PUBLIC`. |
| | `--raw` | Send the text without escaping, for mentions (see below). |
| | `--dry-run` | Print the request payload and publish nothing. |
| `comment` | `POST` plus `--text TEXT` or `--file PATH` | Add a plain text comment to a post URL or share/ugcPost URN. File accepts `-` for stdin. |
| | `--dry-run` | Preview the comment without publishing. |
| `delete` | `POST` (post URL or URN) | Delete one of your own posts. |

### Writing tips

- **Formatting:** LinkedIn does not render Markdown. Use line breaks for structure.
- **Hashtags:** write them plainly (`#AI`). They become clickable.
- **Special characters** such as `( ) [ ] @ _ * < > { } | ~` are escaped automatically.
- **Mentions:** use `@[Exact Name](urn:li:person:ID)` or `@[Company](urn:li:organization:ID)` together with `--raw`. With `--raw` you must escape every other special character yourself (`\(`, `\_`, ...). The name must match the profile or Page name exactly.
- **Links:** put them in the post or use a first comment. The API does not build link-preview cards.

### First comments and recovery

Use `--first-comment` or `--first-comment-file` to submit a comment immediately after the new post. The dry run previews both requests, and the agent asks you to approve both texts. Other people may comment before this request completes, so first placement is not guaranteed.

Comments use plain text, preserve URL punctuation without post escaping, and are limited by this CLI to 1250 characters. The `comment` command can also target an existing post; it does not read the post or verify ownership.

Post creation and comment creation are separate requests. If the comment fails, the CLI exits with an error and preserves the published post URL. Do not rerun `post`, which would create a duplicate. Check LinkedIn for the comment first (a timeout may occur after it was saved), then use `comment <post URL> --file links.txt` only if it is absent. There are no automatic retries. See [troubleshooting](troubleshooting.md) for comment permission errors.

## Limitations

- Posts go to **your personal profile** only. Company Page posts need the `w_organization_social` scope, which requires LinkedIn approval.
- **No direct messages or InMail.** LinkedIn's Messaging API is not available to self-serve apps.
- **No reading posts back** (`r_member_social` is restricted to approved partners), so the agent cannot list or edit existing posts.
- **No scheduling on LinkedIn's side.** Use your agent's scheduler with pre-approved text.
- **Not supported:** video, documents, polls, multi-image posts and link-preview cards.
