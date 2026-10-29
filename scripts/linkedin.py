#!/usr/bin/env python3
"""Publish posts to your personal LinkedIn profile via the Posts API (w_member_social).

Commands:
  auth    one-time OAuth consent in the browser (token lasts 60 days)
  status  show the authorized account and token expiry
  post    publish a text post, optionally with one image (--dry-run to preview)
  comment add a text comment to an existing post
  delete  delete one of your posts by URL or URN
"""
import argparse
import http.server
import json
import mimetypes
import os
import re
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "linkedin-publisher"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.env"
TOKEN_FILE = CONFIG_DIR / "token.json"
REDIRECT_PORT = 8765
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"
SCOPES = "openid profile w_member_social"
# ponytail: pinned; LinkedIn sunsets a version ~12 months after release, bump (or set LINKEDIN_VERSION) by 2027-10
API_VERSION = os.environ.get("LINKEDIN_VERSION", "202610")
MAX_CHARS = 3000
MAX_COMMENT_CHARS = 1250
IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
# little-text reserved chars; unescaped they truncate or break the post. A '#' that starts a word stays a hashtag.
RESERVED = re.compile(r"[|{}@\[\]()<>\\*_~]|#(?!\w)|(?<=\S)#")


def escape(text):
    return RESERVED.sub(lambda m: "\\" + m.group(0), text)


def post_urn(url_or_urn):
    m = re.search(r"urn:li:(?:share|ugcPost):\d+", url_or_urn)
    return m.group(0) if m else None


def build_post(author, text, visibility="PUBLIC", raw=False, image_urn=None, alt=None):
    body = {
        "author": author,
        "commentary": text if raw else escape(text),
        "visibility": visibility,
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    if image_urn:
        body["content"] = {"media": {"id": image_urn, **({"altText": alt} if alt else {})}}
    return body


def build_comment(actor, urn, text):
    # Comments use plain message.text, not Posts API little-text escaping.
    return {"actor": actor, "object": urn, "message": {"text": text}}


def read_comment(text, file):
    value = ((sys.stdin.read() if file == "-" else Path(file).read_text())
             if file is not None else text).strip()
    if not value:
        sys.exit("Comment text is empty.")
    if len(value) > MAX_COMMENT_CHARS:
        sys.exit(f"Comment is {len(value)} chars; maximum is {MAX_COMMENT_CHARS}.")
    return value


def publish_comment(tok, urn, text):
    headers, _ = rest("POST", f"socialActions/{urllib.parse.quote(urn, safe='')}/comments",
                      tok["access_token"], build_comment(tok["person_urn"], urn, text))
    print(f"Comment published on https://www.linkedin.com/feed/update/{urn}/ "
          f"(comment ID: {headers.get('x-restli-id', 'not returned')}).")


def request(method, url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return resp.headers, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        hint = " (token expired or revoked: run `auth`)" if e.code == 401 else ""
        sys.exit(f"LinkedIn {e.code} on {method} {url}{hint}: {e.read().decode(errors='replace')}")
    except urllib.error.URLError as e:
        sys.exit(f"Cannot reach LinkedIn ({e.reason}). If this runs in an agent sandbox, allow network access.")


def rest(method, path, token, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    return request(method, f"https://api.linkedin.com/rest/{path}", data, {
        "Authorization": f"Bearer {token}",
        "LinkedIn-Version": API_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        **(headers or {}),
    })


def userinfo(token):
    return request("GET", "https://api.linkedin.com/v2/userinfo",
                   headers={"Authorization": f"Bearer {token}"})[1]


def load_credentials(path=CREDENTIALS_FILE, environ=os.environ):
    """Client id/secret from the environment, else from KEY=VALUE lines in the credentials file."""
    found = {}
    if path.exists():
        if path.stat().st_mode & 0o077:
            print(f"Warning: {path} is readable by other users, run: chmod 600 {path}", file=sys.stderr)
        for line in path.read_text().splitlines():
            key, sep, value = line.strip().removeprefix("export ").partition("=")
            if sep and not key.startswith("#"):
                found[key.strip()] = value.strip().strip("'\"")
    get = lambda key: environ.get(key) or found.get(key)  # noqa: E731
    return get("LINKEDIN_CLIENT_ID"), get("LINKEDIN_CLIENT_SECRET")


def load_token():
    if not TOKEN_FILE.exists():
        sys.exit(f"Not authorized yet: run `{sys.argv[0]} auth`.")
    tok = json.loads(TOKEN_FILE.read_text())
    if tok["expires_at"] < time.time():
        sys.exit(f"Token expired on {time.ctime(tok['expires_at'])}: run `{sys.argv[0]} auth`.")
    return tok


def wait_for_callback(timeout=300):
    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({k: v[0] for k, v in query.items() if k in ("code", "state", "error", "error_description")})
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"LinkedIn authorization received. You can close this tab.")

        def log_message(self, *args):
            pass

    with http.server.HTTPServer(("localhost", REDIRECT_PORT), Handler) as server:
        server.timeout = 5
        deadline = time.monotonic() + timeout
        while not result and time.monotonic() < deadline:
            server.handle_request()
    return result


def cmd_auth(_args):
    client_id, client_secret = load_credentials()
    if not (client_id and client_secret):
        sys.exit(f"Missing LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET: put them in {CREDENTIALS_FILE} "
                 "or the environment (see README, Configuration).")
    state = secrets.token_urlsafe(24)
    url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": client_id,
        "redirect_uri": REDIRECT_URI, "state": state, "scope": SCOPES,
    })
    print(f"Authorize in the browser (waiting up to 5 min):\n{url}", flush=True)
    webbrowser.open(url)
    result = wait_for_callback()
    if not result:
        sys.exit("Timed out waiting for the LinkedIn redirect.")
    if not secrets.compare_digest(result.get("state", ""), state):
        sys.exit("OAuth state mismatch, aborting.")
    if "error" in result:
        sys.exit(f"Authorization denied: {result.get('error_description', result['error'])}")
    _, token = request("POST", "https://www.linkedin.com/oauth/v2/accessToken", urllib.parse.urlencode({
        "grant_type": "authorization_code", "code": result["code"], "redirect_uri": REDIRECT_URI,
        "client_id": client_id, "client_secret": client_secret,
    }).encode(), {"Content-Type": "application/x-www-form-urlencoded"})
    me = userinfo(token["access_token"])
    saved = {
        "access_token": token["access_token"],
        "expires_at": int(time.time()) + int(token["expires_in"]),
        "person_urn": f"urn:li:person:{me['sub']}",
        "name": me.get("name"),
    }
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(saved, f)
    print(f"Authorized as {saved['name']} ({saved['person_urn']}), token valid until {time.ctime(saved['expires_at'])}.")


def cmd_status(_args):
    tok = load_token()
    me = userinfo(tok["access_token"])
    days = (tok["expires_at"] - time.time()) / 86400
    print(f"{me.get('name')} ({tok['person_urn']}): token OK, expires in {days:.0f} days "
          f"({time.ctime(tok['expires_at'])}). API version {API_VERSION}.")


def upload_image(token, owner, path):
    mime = mimetypes.guess_type(path)[0]
    if mime not in IMAGE_TYPES:
        sys.exit(f"Unsupported image type {mime!r} for {path}: use JPG, PNG or GIF.")
    _, init = rest("POST", "images?action=initializeUpload", token,
                   {"initializeUploadRequest": {"owner": owner}})
    request("PUT", init["value"]["uploadUrl"], Path(path).read_bytes(),
            {"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"})
    return init["value"]["image"]


def cmd_post(args):
    if args.file == "-" and args.first_comment_file == "-":
        sys.exit("Post and first comment cannot both read stdin.")
    comment = (read_comment(args.first_comment, args.first_comment_file)
               if args.first_comment is not None or args.first_comment_file is not None else None)
    text = (sys.stdin.read() if args.file == "-" else Path(args.file).read_text()) if args.file else args.text
    text = text.strip()
    if not text:
        sys.exit("Post text is empty.")
    if len(text) > MAX_CHARS:
        sys.exit(f"Post is {len(text)} chars; LinkedIn allows {MAX_CHARS}.")
    if args.image and not Path(args.image).is_file():
        sys.exit(f"Image not found: {args.image}")
    tok = load_token()
    if args.dry_run:
        image = f"<uploaded from {args.image}>" if args.image else None
        print(json.dumps(build_post(tok["person_urn"], text, args.visibility, args.raw, image, args.alt), indent=2))
        if comment is not None:
            print("\nFirst comment (after post creation):")
            print(json.dumps(build_comment(tok["person_urn"], "<created post URN>", comment), indent=2))
        print(f"\n--- DRY RUN: nothing published. {len(text)}/{MAX_CHARS} chars, as {tok['name']}. ---")
        return
    image_urn = upload_image(tok["access_token"], tok["person_urn"], args.image) if args.image else None
    headers, _ = rest("POST", "posts", tok["access_token"],
                      build_post(tok["person_urn"], text, args.visibility, args.raw, image_urn, args.alt))
    urn = headers.get("x-restli-id")
    if not urn or post_urn(urn) != urn:
        sys.exit("Post creation succeeded but LinkedIn returned no usable post URN. "
                 "Check your profile before retrying; no first comment was attempted.")
    print(f"Published: https://www.linkedin.com/feed/update/{urn}/", flush=True)
    if comment is not None:
        try:
            publish_comment(tok, urn, comment)
        except (SystemExit, OSError, ValueError) as exc:
            sys.exit(f"Post is already published at https://www.linkedin.com/feed/update/{urn}/, "
                     f"but the first comment was not confirmed: {exc}\n"
                     "Do not rerun `post`. Check the post for the comment first; if absent, "
                     f"use `comment {urn} --file <comment-file>` to add it.")


def cmd_comment(args):
    urn = post_urn(args.post)
    if not urn:
        sys.exit(f"No post URN (urn:li:share:N or urn:li:ugcPost:N) in {args.post!r}.")
    text = read_comment(args.text, args.file)
    tok = load_token()
    if args.dry_run:
        print(json.dumps(build_comment(tok["person_urn"], urn, text), indent=2))
        print(f"\n--- DRY RUN: nothing published. {len(text)}/{MAX_COMMENT_CHARS} comment chars. ---")
        return
    publish_comment(tok, urn, text)


def cmd_delete(args):
    urn = post_urn(args.post)
    if not urn:
        sys.exit(f"No post URN (urn:li:share:N or urn:li:ugcPost:N) in {args.post!r}.")
    tok = load_token()
    rest("DELETE", f"posts/{urllib.parse.quote(urn, safe='')}", tok["access_token"],
         headers={"X-RestLi-Method": "DELETE"})
    print(f"Deleted {urn}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth", help="authorize via browser OAuth").set_defaults(func=cmd_auth)
    sub.add_parser("status", help="show account and token expiry").set_defaults(func=cmd_status)
    post = sub.add_parser("post", help="publish a post")
    src = post.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="post text")
    src.add_argument("--file", help="file with the post text ('-' for stdin)")
    first = post.add_mutually_exclusive_group()
    first.add_argument("--first-comment", help="text comment to publish immediately after the post")
    first.add_argument("--first-comment-file", help="file with first comment text ('-' for stdin)")
    post.add_argument("--image", help="attach one JPG/PNG/GIF")
    post.add_argument("--alt", help="image alt text")
    post.add_argument("--visibility", choices=["PUBLIC", "CONNECTIONS"], default="PUBLIC")
    post.add_argument("--raw", action="store_true",
                      help="send text as-is (no escaping), for @[Name](urn:li:...) mentions")
    post.add_argument("--dry-run", action="store_true", help="print the payload, publish nothing")
    post.set_defaults(func=cmd_post)
    comment = sub.add_parser("comment", help="add a text comment to an existing post")
    comment.add_argument("post", help="post URL or share/ugcPost URN")
    comment_src = comment.add_mutually_exclusive_group(required=True)
    comment_src.add_argument("--text", help="comment text (plain text, including links)")
    comment_src.add_argument("--file", help="file with comment text ('-' for stdin)")
    comment.add_argument("--dry-run", action="store_true", help="print the payload, publish nothing")
    comment.set_defaults(func=cmd_comment)
    delete = sub.add_parser("delete", help="delete one of your posts")
    delete.add_argument("post", help="post URL (linkedin.com/feed/update/...) or URN")
    delete.set_defaults(func=cmd_delete)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
