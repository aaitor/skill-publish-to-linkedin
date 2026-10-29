# Security and privacy

- **Scopes:** the app requests only `openid` and `profile` (to identify you as the post author) and `w_member_social` (to create and delete your posts). It cannot read your feed, messages or connections.
- **Local storage:** credentials and tokens stay on your machine in `~/.config/linkedin-publisher/`. The script creates `token.json` with mode `600` and warns if `credentials.env` is readable by others.
- **Network:** requests go only to `linkedin.com` and its upload endpoints. Sign-in uses a random `state` value to protect against cross-site request forgery.
- **Approval:** the skill instructs the agent never to publish without your explicit approval of the exact text.
- **Revoking access:** remove the app from LinkedIn's [Permitted services](https://www.linkedin.com/mypreferences/d/permitted-services) settings and delete `~/.config/linkedin-publisher/token.json`.

Use it in line with LinkedIn's [User Agreement](https://www.linkedin.com/legal/user-agreement) and [API Terms of Use](https://www.linkedin.com/legal/l/api-terms-of-use). Don't use it for spam or mass posting.

For responsible disclosure, see [SECURITY.md](../SECURITY.md).
