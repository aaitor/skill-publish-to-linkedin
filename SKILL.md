---
name: publish-to-linkedin
description: Use when the user asks to publish, post or share content on their personal LinkedIn profile (a text post, or a post with one image), to delete one of their LinkedIn posts, to automate or schedule LinkedIn posts, or when the LinkedIn token is missing, expired or returns 401.
---

# Publish to LinkedIn

Publishes to the authorized member's **personal profile** through the official LinkedIn Posts API (`w_member_social`). Python 3.9+ standard library only, nothing to install.

`<skill-dir>` is the directory that contains this `SKILL.md`.

```bash
LI="python3 <skill-dir>/scripts/linkedin.py"
$LI status                                  # authorized account + days until token expiry
$LI post --file post.txt --dry-run          # print the exact payload, publish nothing
$LI post --file post.txt [--image x.png --alt "..."] [--visibility CONNECTIONS]
$LI delete <post URL or URN>                # delete one of the member's own posts
$LI auth                                    # browser consent, needed every 60 days
```

## Workflow

1. **Check setup:** run `$LI status`.
   - `Not authorized`, `Token expired` or `401`: run `$LI auth` as a long-running or background command. It opens the browser and blocks until the user approves (5 minute limit). Tell the user to approve the consent screen, then wait for the command to exit. If you run in a sandbox that cannot open a browser or write to `~/.config`, ask the user to run that command in their own terminal instead.
   - `Cannot reach LinkedIn`: your sandbox blocks network access. Request approval to run the command with network access, or ask the user to enable it.
   - `Missing LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET`: the one-time LinkedIn app setup is not done. Walk the user through `<skill-dir>/docs/installation.md`, sections "Create a LinkedIn app" and "Configuration". Never ask the user to paste the client secret into the chat.
2. **Draft:** if the user has a writing-voice or style skill, draft with it. Otherwise follow the user's instructions and keep their wording. Write the final text to a temporary file. Use plain text: LinkedIn does not render Markdown, so `**bold**` shows literally. Use line breaks and plain `#hashtags`.
3. **Preview:** run `$LI post --file <path> [--image ...] --dry-run`. Show the user the full post text, the visibility and the image.
4. **Approval gate:** publish only after the user explicitly approves *this exact text* in the conversation. A scheduled or automated run counts as approved only when the user created it with the verbatim text. If the text changes after approval, preview and ask again.
5. **Publish:** rerun without `--dry-run`. Give the user the returned `https://www.linkedin.com/feed/update/...` URL.

## Notes

- **Images:** one JPG, PNG or GIF per post. If an image pasted into the chat comes with a local file path, pass that path to `--image`; if it doesn't, ask the user for the file. Download remote images to a temporary file first.
- **Escaping:** the text is escaped for LinkedIn's "little text" format automatically. Unescaped `( ) [ ] @ _ *` silently truncate a post. `#word` stays a clickable hashtag.
- **Mentions:** use `@[Exact Name](urn:li:person:ID)` or `@[Company](urn:li:organization:ID)` with `--raw`. With `--raw` you must escape every other reserved character yourself (`\(`, `\_`, ...). This skill cannot look up member or organization IDs.
- **Links:** put URLs inline in the text. The API does not generate link-preview cards.
- **Delete** only after the user confirms which post, by its URL. Deletion is permanent and only works on the authorized member's own posts. A `404 NOT_FOUND` means the post is already deleted or the URL is wrong.
- **Limits:** 3000 characters. Video, documents, polls, multi-image and link-preview cards are not supported.
- **Not possible:** reading posts back (`r_member_social` is partner-only), direct messages and InMail (the Messaging API is closed to self-serve apps), and Company Page posts (need `w_organization_social`).
