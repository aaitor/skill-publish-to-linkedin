# Examples

Run the credential-free preview:

```bash
python3 examples/offline_preview.py
```

It exercises the real CLI dry-run with [sample post text](post.txt), a fixture author, and blocked network requests. Output includes the escaped commentary, visibility, and `DRY RUN: nothing published`. It does not read your token or credentials and cannot publish.

For a normal dry run with your authorized identity, first complete [setup](../docs/installation.md), then run from the repository root:

```bash
python3 scripts/linkedin.py post --file examples/post.txt --dry-run
```

To reproduce the README GIF, install [VHS and its prerequisites](https://github.com/charmbracelet/vhs#installation), then run `vhs examples/demo.tape` from the root. The tape uses the shared terminal theme from `aaitor/assets`. The recording shows this offline example, not a real authorization or published post.
