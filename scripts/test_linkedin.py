"""Run: python3 scripts/test_linkedin.py"""
import os
import tempfile
from pathlib import Path

from linkedin import build_post, escape, load_credentials, post_urn

with tempfile.TemporaryDirectory() as tmp:
    creds = Path(tmp) / "credentials.env"
    creds.write_text("# LinkedIn app\nexport LINKEDIN_CLIENT_ID='file-id'\nLINKEDIN_CLIENT_SECRET=\"file-secret\"\n")
    os.chmod(creds, 0o600)
    assert load_credentials(creds, {}) == ("file-id", "file-secret")
    assert load_credentials(creds, {"LINKEDIN_CLIENT_ID": "env-id"}) == ("env-id", "file-secret")  # env wins
    assert load_credentials(Path(tmp) / "missing.env", {}) == (None, None)

assert post_urn("https://www.linkedin.com/feed/update/urn:li:share:7000000000000000000/") == "urn:li:share:7000000000000000000"
assert post_urn("urn:li:ugcPost:123") == "urn:li:ugcPost:123"
assert post_urn("https://www.linkedin.com/in/someone/") is None

assert escape("Hi (all) @you [x] a_b *c* ~d~ <e> {f} | \\") == \
    "Hi \\(all\\) \\@you \\[x\\] a\\_b \\*c\\* \\~d\\~ \\<e\\> \\{f\\} \\| \\\\"
assert escape("#AI agents #x402") == "#AI agents #x402"  # hashtags survive
assert escape("#ai\n#ml") == "#ai\n#ml"
assert escape("# heading") == "\\# heading"
assert escape("see page#anchor") == "see page\\#anchor"
assert escape("plain text, no change.") == "plain text, no change."

post = build_post("urn:li:person:abc", "Hello (world)", "CONNECTIONS")
assert post["commentary"] == "Hello \\(world\\)" and post["visibility"] == "CONNECTIONS"
assert "content" not in post
assert build_post("u", "@[Acme](urn:li:organization:1)", raw=True)["commentary"] == "@[Acme](urn:li:organization:1)"
assert build_post("u", "t", image_urn="urn:li:image:1", alt="pic")["content"] == {"media": {"id": "urn:li:image:1", "altText": "pic"}}
assert build_post("u", "t", image_urn="urn:li:image:1")["content"] == {"media": {"id": "urn:li:image:1"}}
print("ok")

# Exercise real CLI parsing and commands with only the network/token boundaries mocked.
import contextlib
import io
import json
import sys
from unittest.mock import patch
import linkedin

TOKEN = {"access_token": "test-token", "person_urn": "urn:li:person:test", "name": "Test", "scope": "openid profile w_member_social w_member_social_feed"}
URN = "urn:li:share:123"
LINKS = "Read (more): https://example.com/a_b?q=x&v=2#section"


def cli(*args, responses=None):
    output = io.StringIO()
    with patch.object(sys, "argv", ["linkedin.py", *args]), \
            patch.object(linkedin, "load_token", return_value=TOKEN), \
            patch.object(linkedin, "rest", side_effect=responses) as api, \
            patch.object(linkedin, "upload_image", return_value="urn:li:image:1") as upload, \
            contextlib.redirect_stdout(output):
        linkedin.main()
    return output.getvalue(), api, upload


preview, api, upload = cli("post", "--text", "Update", "--first-comment", LINKS,
                           "--image", __file__, "--dry-run")
assert json.loads(preview.split("\nFirst comment", 1)[0])["commentary"] == "Update"
assert LINKS in preview and "<created post URN>" in preview
api.assert_not_called()
upload.assert_not_called()

for target in (URN, "urn:li:ugcPost:123", f"https://www.linkedin.com/feed/update/{URN}/"):
    preview, api, _ = cli("comment", target, "--text", LINKS, "--dry-run")
    body = json.loads(preview.split("\n\n---", 1)[0])
    assert body["message"]["text"] == LINKS
    assert body["actor"] == TOKEN["person_urn"]
    api.assert_not_called()

result, api, _ = cli("post", "--text", "Update", "--first-comment", LINKS,
                     responses=[({"x-restli-id": URN}, None), ({"x-restli-id": "456"}, {})])
assert api.call_count == 2
assert api.call_args_list[0].args[1] == "posts"
assert api.call_args_list[1].args == (
    "POST", "socialActions/urn%3Ali%3Ashare%3A123/comments", "test-token",
    {"actor": TOKEN["person_urn"], "object": URN, "message": {"text": LINKS}})
assert "Comment published" in result and URN in result

_, api, _ = cli("post", "--text", "Update", responses=[({"x-restli-id": URN}, None)])
assert api.call_count == 1

with tempfile.TemporaryDirectory() as tmp:
    file = Path(tmp) / "comment.txt"
    file.write_text(LINKS)
    _, api, _ = cli("comment", URN, "--file", str(file), responses=[({}, {})])
    assert api.call_args.args[3]["message"]["text"] == LINKS
    _, api, _ = cli("post", "--text", "Update", "--first-comment-file", str(file), "--dry-run")
    api.assert_not_called()

with patch.object(sys, "stdin", io.StringIO(LINKS)):
    _, api, _ = cli("comment", URN, "--file", "-", responses=[({}, {})])
    assert api.call_args.args[3]["message"]["text"] == LINKS

with patch.object(sys, "stdin", io.StringIO(LINKS)):
    preview, api, _ = cli("post", "--text", "Update", "--first-comment-file", "-", "--dry-run")
    assert LINKS in preview
    api.assert_not_called()

_, api, _ = cli("comment", URN, "--text", "x" * 1250, responses=[({}, {})])
assert len(api.call_args.args[3]["message"]["text"]) == 1250

_, api, upload = cli("post", "--text", "Update", "--image", __file__, "--first-comment", LINKS,
                     responses=[({"x-restli-id": URN}, None), ({}, {})])
upload.assert_called_once()
assert api.call_args_list[0].args[3]["content"]["media"]["id"] == "urn:li:image:1"
assert api.call_count == 2

for args in (
    ("post", "--file", "-", "--first-comment-file", "-"),
    ("post", "--text", "Update", "--first-comment", "  "),
    ("post", "--text", "Update", "--first-comment", "x" * 1251),
    ("comment", URN, "--text", "  "),
    ("comment", URN, "--text", "x" * 1251),
    ("comment", "https://www.linkedin.com/in/someone/", "--text", LINKS),
):
    with patch.object(sys, "argv", ["linkedin.py", *args]), \
            patch.object(linkedin, "load_token") as token, patch.object(linkedin, "rest") as api:
        try:
            linkedin.main()
            raise AssertionError("Invalid input accepted")
        except SystemExit as exc:
            assert exc.code
        token.assert_not_called()
        api.assert_not_called()

for failure in (SystemExit("LinkedIn 403"), SystemExit("Cannot reach LinkedIn"), TimeoutError("timeout")):
    output = io.StringIO()
    with patch.object(sys, "argv", ["linkedin.py", "post", "--text", "Update", "--first-comment", LINKS]), \
            patch.object(linkedin, "load_token", return_value=TOKEN), \
            patch.object(linkedin, "rest", side_effect=[({"x-restli-id": URN}, None), failure]) as api, \
            contextlib.redirect_stdout(output):
        try:
            linkedin.main()
            raise AssertionError("Comment failure was hidden")
        except SystemExit as exc:
            assert URN in str(exc) and "Do not rerun `post`" in str(exc)
    assert api.call_count == 2 and f"Published: https://www.linkedin.com/feed/update/{URN}/" in output.getvalue()

for response in (SystemExit("Post failed"), ({}, None)):
    with patch.object(sys, "argv", ["linkedin.py", "post", "--text", "Update", "--first-comment", LINKS]), \
            patch.object(linkedin, "load_token", return_value=TOKEN), \
            patch.object(linkedin, "rest", side_effect=[response]) as api:
        try:
            linkedin.main()
            raise AssertionError("Post failure or missing ID was hidden")
        except SystemExit:
            pass
    assert api.call_count == 1

print("ok: comment previews, payloads, input validation, sequencing, and partial failures")


# Missing/legacy comment scopes must fail before image upload or post creation.
for scope in (None, "openid profile w_member_social"):
    token = dict(TOKEN)
    if scope is None:
        token.pop("scope")
    else:
        token["scope"] = scope
    for argv in (["post", "--text", "Update", "--first-comment", LINKS, "--image", __file__],
                 ["comment", URN, "--text", LINKS]):
        with patch.object(sys, "argv", ["linkedin.py", *argv]), \
                patch.object(linkedin, "load_token", return_value=token), \
                patch.object(linkedin, "rest") as api, patch.object(linkedin, "upload_image") as upload:
            try:
                linkedin.main()
                raise AssertionError("Missing comment permission was accepted")
            except SystemExit as exc:
                assert "auth --with-comments" in str(exc)
            api.assert_not_called()
            upload.assert_not_called()

for argv in (["comment", URN, "--file", "/does-not-exist/comment.txt"],
             ["post", "--text", "Update", "--first-comment-file", "/does-not-exist/comment.txt"],
             ["post", "--file", "/does-not-exist/post.txt"]):
    try:
        cli(*argv)
        raise AssertionError("Missing file accepted")
    except SystemExit as exc:
        assert "Cannot read" in str(exc)

for failure in (TimeoutError("response read timed out"), SystemExit("LinkedIn 403")):
    try:
        cli("comment", URN, "--text", LINKS, responses=[failure])
        raise AssertionError("Uncertain comment result accepted")
    except SystemExit as exc:
        assert "Check LinkedIn" in str(exc) and URN in str(exc)

# Authorize without a browser or real credentials; inspect the requested and saved scopes.
import argparse
import urllib.parse
for with_comments in (False, True):
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp) / "config"
        token_file = directory / "token.json"
        with patch.object(linkedin, "load_credentials", return_value=("test-id", "test-secret")), \
                patch.object(linkedin.secrets, "token_urlsafe", return_value="test-state"), \
                patch.object(linkedin, "wait_for_callback", return_value={"state": "test-state", "code": "test-code"}), \
                patch.object(linkedin.webbrowser, "open") as browser, \
                patch.object(linkedin, "request", return_value=({}, {"access_token": "fake", "expires_in": 3600})), \
                patch.object(linkedin, "userinfo", return_value={"sub": "test", "name": "Test"}), \
                patch.object(linkedin, "CONFIG_DIR", directory), patch.object(linkedin, "TOKEN_FILE", token_file), \
                contextlib.redirect_stdout(io.StringIO()):
            linkedin.cmd_auth(argparse.Namespace(with_comments=with_comments))
        requested = urllib.parse.parse_qs(urllib.parse.urlparse(browser.call_args.args[0]).query)["scope"][0]
        assert (linkedin.COMMENT_SCOPE in requested.split()) == with_comments
        assert json.loads(token_file.read_text())["scope"] == requested
        assert "w_member_social" in requested.split()

print("ok: opt-in OAuth scopes, publication guard, comment recovery, and missing files")
