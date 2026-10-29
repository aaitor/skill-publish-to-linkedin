# Contributing

Use [Issues](https://github.com/aaitor/skill-publish-to-linkedin/issues) for reproducible bugs and proposals. Discuss large changes first. Keep the skill and CLI usable with Python 3.9+ and the standard library.

1. Fork and clone; create a focused branch.
2. Update implementation, examples, and documentation together.
3. Run `python3 scripts/test_linkedin.py` and `python3 scripts/check.py`. These use fixtures and do not need a LinkedIn account.
4. Submit a pull request describing the problem, resulting behavior, and verification.

Do not publish or delete real posts in tests. Preserve the skill's exact-content approval gate and use mocked network responses for API behavior. Never include credentials, tokens, personal post data, or unredacted API logs in issues or recordings.

Contributions use the repository's MIT license. Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Report vulnerabilities through [SECURITY.md](SECURITY.md).
