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
