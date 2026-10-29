# Troubleshooting

| Symptom | Fix |
|---|---|
| Browser shows *redirect_uri does not match* | Add exactly `http://localhost:8765/callback` under Auth → *Authorized redirect URLs*. |
| Browser shows *unauthorized_scope_error* | Add both products on the **Products** tab, then run `auth` again. |
| `Missing LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET` | Create `credentials.env` (see [Configuration](installation.md#configuration)). |
| `Cannot reach LinkedIn` | No network, or the agent's sandbox blocks it (see [Agent network access](agent-setup.md#authorization-and-network-access)). |
| `Timed out waiting for the LinkedIn redirect` | Approve within 5 minutes. On a remote host, use the SSH tunnel described above. |
| `Address already in use` during `auth` | Another process is using port 8765. Stop it and retry. |
| `LinkedIn 401` | The token expired or was revoked. Run `auth`. |
| `LinkedIn 403 ACCESS_DENIED` | The token lacks `w_member_social`. Add *Share on LinkedIn* and run `auth` again. |
| `403` when adding a comment | Comment access depends on the app/product and API version. LinkedIn lists `w_member_social` for member publishing and `w_member_social_feed` for the current [Comments API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/comments-api). Check your app's approved products and permissions; run `auth --with-comments` only after the app has approved Community Management access and lists `w_member_social_feed`. Default `auth` requests post-only scopes. Do not repeatedly reauthorize if your app lacks access. |
| Post published but comment not confirmed | Keep the post URL. Check LinkedIn for the comment before retrying only `comment <post URL> --file links.txt`. Never rerun `post`. |
| `LinkedIn 404` on `delete` | The post is already deleted, or the URL is not one of your posts. |
| `LinkedIn 422 ...` | The message names the invalid field, for example text that is too long. |
| Error about the API version | The pinned version was retired. Set `LINKEDIN_VERSION` to a recent `YYYYMM`. |
| Post appears cut off | You used `--raw` without escaping special characters. Remove `--raw` or escape them. |
| The agent doesn't use the skill | Check the install path for your agent (see [Install](installation.md)), restart the agent, and mention "LinkedIn" in your request. |
