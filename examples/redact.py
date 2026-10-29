"""Redact LinkedIn member IDs from real CLI output when recording a public demo."""
import re
import sys

# Leave the actual CLI output intact except for the personal member identifier.
# This filter neither imports nor patches the skill and does not load credentials.
for line in sys.stdin:
    print(re.sub(r'urn:li:person:[A-Za-z0-9_-]+', 'urn:li:person:[redacted]', line), end='', flush=True)
