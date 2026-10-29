"""Run the real CLI dry-run with a sample identity, without credentials or network."""
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import linkedin


def main():
    print('Offline example: sample identity; no credentials or network.', flush=True)
    arguments = ['linkedin.py', 'post', '--file', str(ROOT / 'examples/post.txt'), '--dry-run']
    sample = {'person_urn': 'urn:li:person:EXAMPLE', 'name': 'Example Author'}
    with patch.object(sys, 'argv', arguments), \
         patch.object(linkedin, 'load_token', return_value=sample), \
         patch.object(linkedin, 'request', side_effect=AssertionError('Offline demo attempted network access')):
        linkedin.main()


if __name__ == '__main__':
    main()
