# Run from the repository root: vhs examples/demo.tape
Source examples/theme.tape
Output assets/terminal-demo.gif
Set Height 700
Hide
Type "export PS1='$ '; clear"
Enter
Sleep 500ms
Show
Type "python3 examples/offline_preview.py"
Enter
Wait+Screen /DRY RUN: nothing published/
Sleep 5s
