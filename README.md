# InkyPi Literature Clock

A third-party [InkyPi](https://github.com/fatihak/InkyPi) plugin that displays a literary quote referencing the current minute, with the time phrase highlighted.

Inspired by the privacy-mode literature clock in [mendhak/waveshare-epaper-display](https://github.com/mendhak/waveshare-epaper-display) and the original [Author Clock](https://www.authorclock.com/) / [Jaap Meijers' literary clock](https://github.com/JohannesNE/literature-clock).

## Screenshot

_Coming soon — replace with an actual photo of the plugin running on your display._

## Installation

1. SSH into your Pi.
2. Clone this repo:
   ```bash
   git clone https://github.com/hdepa/InkyPi-literature-clock.git
   ```
3. Copy the plugin folder into your InkyPi install:
   ```bash
   cp -R InkyPi-literature-clock/literature_clock /path/to/InkyPi/src/plugins/
   ```
4. Restart the InkyPi service:
   ```bash
   sudo systemctl restart inkypi.service
   ```
5. The plugin will appear in the InkyPi web UI under **Plugins → Literature Clock**.

## Settings

| Setting | Description |
|---|---|
| Quote selection | `shortest` (default), `random`, or `daily` (deterministic per minute per day) |
| Allow NSFW | Includes NSFW-flagged quotes (default off) |
| Show attribution | Display book title + author below the quote |
| Font | Any font available in InkyPi's `static/fonts/` |
| Highlight style | bold / italic / underline / color |
| Highlight color | Custom color when style = color |

## Refresh cadence

Set the playlist refresh interval to **1 minute** for true clock semantics.

## Dataset

Quotes come from [JohannesNE/literature-clock](https://github.com/JohannesNE/literature-clock) (`litclock_annotated.csv`). The plugin bundles a copy for offline use and refreshes weekly when online. About 70 of the 1440 minutes in a day have no exact-time entry; the plugin falls back to ±1 minute, then to a "no quote" card.

No API key required.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python3 -m pytest -v
```

## Status

Actively maintained.

## License

MIT
