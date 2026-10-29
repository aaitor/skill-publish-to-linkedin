# Banner and social preview

The header follows the shared repository format: **diagonal-drift (1a)**, seed `7`, with the title `Publish to LinkedIn` and handle `@aaitor`. The README points at a commit-pinned banner in [aaitor/assets](https://github.com/aaitor/assets); a local copy is kept in `assets/hero.svg`.

`shared-assets.json` records the shared source revision and template revision. The skill runtime remains Python-only: Node.js is needed only when maintainers regenerate banner artwork in the assets repository.

## Generate the banner

From a clone of `aaitor/assets` with Node.js 18+ installed:

```bash
node banner-kit/make-banner.mjs --style diagonal-drift \
  --repo "Publish to LinkedIn" \
  --tagline "Draft, preview, and publish with your AI agent." \
  --handle "@aaitor" --seed 7 --out banners/skill-publish-to-linkedin.svg
```

See the [shared generation guide](https://github.com/aaitor/assets/blob/26be4ac7da293f2afd2252f5370359e7a4e82b1d/docs/banner-generation.md) for all styles, fixed seeds, static output, and the JavaScript API. The kit requires no npm packages or network access. Preserve the bundled font notices.

## Regenerate the social card

From that same assets checkout, center the generated banner on a matching 1280 × 640 canvas:

```bash
python3 - <<'PYTHON'
from pathlib import Path
banner = Path('banners/skill-publish-to-linkedin.svg').read_text()
inner = banner.replace('<svg ', '<svg x="0" y="160" ', 1)
Path('social/skill-publish-to-linkedin.svg').write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" '
    'viewBox="0 0 1280 640" role="img" aria-label="Publish to LinkedIn">'
    '<rect width="1280" height="640" fill="#0e0f11"/>' + inner + '</svg>\n')
PYTHON
```

Open the SVG in a modern browser to check fonts and clipping. Export to PNG with a browser or vector editor that supports embedded webfonts. If using Chromium, run from the assets checkout:

```bash
chromium --headless --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=1280,640 \
  --virtual-time-budget=1500 \
  --screenshot="$PWD/social/skill-publish-to-linkedin.png" \
  "file://$PWD/social/skill-publish-to-linkedin.svg"
```

Copy the reviewed banner and social SVG/PNG into this skill's `assets/`, update the source revision and pinned README URL after publishing upstream, and keep the font notices. The ready-to-upload `assets/social-preview.png` is included, but must be uploaded through **GitHub Settings → General → Social preview** to activate it. Merely committing it does not set the repository preview.

## Terminal demo

The [example guide](../examples/README.md) documents the credential-free preview and VHS recording. Its terminal theme is shared with `aaitor/assets`; the sample author and post text are deliberately synthetic.
