# Install the skill and use it with Claude Code

The README GIF shows a real Claude Code session on a black terminal background:

1. Clone the skill into the project's `.claude/skills/publish-to-linkedin` directory.
2. Invoke `/publish-to-linkedin` through Claude Code.
3. Review the draft and stop at the publishing approval prompt.

Claude reads the installed skill and uses the actual CLI to check authorization and dry-run the message. Its final response shows the draft, visibility, and approval question. Nothing is published. Waiting time for cloning and model output is omitted from the animation; the commands and Claude's answer are recorded live.

## Try it

Complete [LinkedIn setup and authorization](../docs/installation.md) and install Claude Code. From your project directory:

```bash
git clone https://github.com/aaitor/skill-publish-to-linkedin .claude/skills/publish-to-linkedin
```

Create `message.txt` with your draft, then use Claude Code's non-interactive harness:

```bash
claude -p "/publish-to-linkedin Preview message.txt. Ask before publishing."
```

You can also start `claude` interactively and submit the same `/publish-to-linkedin` request. Allow the skill's status and dry-run commands when your harness asks. Review the exact post text and visibility before authorizing publishing. In the recorded demo, the user chose to stop at this approval step.

## Reproduce the recording

Requires Python 3.9+, Git, an authenticated Claude Code installation, saved LinkedIn authorization, [VHS with ttyd and ffmpeg](https://github.com/charmbracelet/vhs#installation), and DejaVu Sans Mono or a substitute font. Running the recorder invokes your real Claude Code account and may consume model usage. It makes a live LinkedIn status request and a local dry-run; it does not publish.

From this repository:

```bash
python3 examples/record_demo.py
```

The helper creates an isolated temporary project, installs the skill visibly through the tape, and saves the finished GIF to `assets/terminal-demo.gif`. Use `--out /tmp/demo.gif` to choose another location. The existing GIF is replaced only after recording completes.

[demo.tape](demo.tape) controls the visible commands, timing, and black background. [claude-demo.md](claude-demo.md) contains the recording instructions. [demo-post.txt](demo-post.txt) supplies the draft. The helper limits the harness to file/skill tools plus Python status and dry-run commands, loads only the isolated project settings, disables optional hooks, and excludes configured MCP servers, and leaves global harness settings unchanged. It does not bypass permissions. The visible `claude` command uses this session-specific configuration through a shell function; Claude Code and the skill execute normally.

Watch the finished GIF before committing it. It may contain your name, draft text, and Claude's response; do not record private content. Regenerating the recording is a manual action, never a CI step.

## Credential-free CLI example

For a separate offline exercise or CI:

```bash
python3 examples/offline_preview.py
```

This uses [sample post text](post.txt), a fixture identity, and blocked network requests to demonstrate the payload format. It is not the workflow recorded in the README GIF.
