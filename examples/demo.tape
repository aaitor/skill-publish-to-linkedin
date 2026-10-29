# Real skill workflow. Requires an already authorized LinkedIn account.
# This tape checks status and previews only. It never publishes or deletes.
# Run from the repository root: vhs examples/demo.tape
Source examples/theme.tape
Output assets/terminal-demo.gif
Set Width 1280
Set Height 820
Set FontSize 20
Hide
Type "export PS1='$ '; set -o pipefail; clear"
Enter
Sleep 500ms
Show
Type "sed -n '6,15p' SKILL.md"
Enter
Sleep 4s
Type "clear"
Enter
Type 'LI="python3 scripts/linkedin.py"'
Enter
Type "$LI status | python3 examples/redact.py"
Enter
Wait+Screen /token OK/
Sleep 2s
Type "cat examples/demo-post.txt"
Enter
Sleep 4s
Type "$LI post --file examples/demo-post.txt --dry-run | python3 examples/redact.py"
Enter
Wait+Screen /DRY RUN: nothing published/
Sleep 6s
