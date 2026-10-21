# kenney-dl

A small, polite Python script to download [Kenney's](https://kenney.nl) free CC0 game asset packs in bulk, sorted by category.

No dependencies, just Python 3.8+.

```bash
python3 kenney_dl.py                         # everything
python3 kenney_dl.py --category 3D           # only 3D packs
python3 kenney_dl.py --category 3D --category Audio --out ~/Kenney
python3 kenney_dl.py --list                  # see what's there first
```

Options: `--category` (2D, 3D, Audio, Textures, UI, Pixel; repeatable), `--out` (default `kenney_assets/`), `--delay` (seconds between requests, default 1.5. Please don't set it to 0).

It's resumable: re-run it and it skips zips you already have, so it also works for grabbing new releases later.

## Please support Kenney

These assets are free because Kenney makes them free. If they're useful to you:

- [Donate](https://kenney.nl/donate)
- Or buy the [All-in-1 bundle](https://kenney.itch.io/kenney-game-assets), which gets you everything in one download plus updates, and supports more packs being made.

This repo contains no assets, only the script. Assets are CC0 by Kenney. Not affiliated with Kenney.

## Licence

Script: MIT.
