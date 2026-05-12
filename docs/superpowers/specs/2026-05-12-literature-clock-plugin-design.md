# InkyPi Literature Clock Plugin — Design

**Date:** 2026-05-12
**Status:** Approved (design phase)

## Summary

A third-party InkyPi plugin that displays a literary quote in which a phrase referencing the current time (HH:MM) is highlighted. Inspired by the privacy-mode literature clock in [mendhak/waveshare-epaper-display](https://github.com/mendhak/waveshare-epaper-display), reusing the same upstream dataset.

## Goals

- Drop-in third-party InkyPi plugin following the structure documented in `InkyPi/docs/building_plugins.md`.
- Display a time-matched literary quote with the time phrase highlighted.
- Work offline on first run; refresh quote dataset weekly when online.
- Reuse InkyPi's HTML/CSS rendering pipeline for clean text wrapping and inline highlighting.

## Non-goals

- Translating quotes or supporting non-English locales (dataset is English).
- Curating or authoring new quotes.
- A standalone web UI outside InkyPi's existing plugin settings page.

## Data Source

- Upstream: `https://raw.githubusercontent.com/JohannesNE/literature-clock/master/litclock_annotated.csv`
- Format: pipe-delimited, no quote char, columns: `time | time_human | full_quote | book_title | author_name | sfw`
- Size: ~1 MB, ~2400 rows. ~70 of 1440 minutes have no entry.

## Repository / Plugin Layout

Repository: `InkyPi-literature-clock` (matches recommended third-party naming).

```
InkyPi-literature-clock/
├── README.md
├── LICENSE
├── docs/superpowers/specs/...
└── literature_clock/                    # the plugin folder InkyPi copies into src/plugins/
    ├── literature_clock.py              # plugin class
    ├── plugin-info.json                 # {id, display_name, class, repository}
    ├── icon.png
    ├── settings.html
    ├── render/
    │   ├── literature_clock.html        # extends InkyPi's plugin.html
    │   └── literature_clock.css
    └── data/
        └── litclock_annotated.csv       # bundled fallback / cache target
```

## Plugin Behavior

### `generate_image(settings, device_config)`

1. Resolve current time using `device_config` timezone (mirrors the built-in Clock plugin's pattern with `pytz`).
2. Ensure the local CSV cache is fresh:
   - Path: alongside the plugin, `data/litclock_annotated.csv`.
   - If file age > 7 days, attempt re-download from upstream; on failure, log and continue with the existing file.
   - The bundled CSV ships with the plugin so the first run works offline.
3. Read all rows where `time == HH:MM`. If the user has not enabled NSFW, exclude rows where `sfw == "nsfw"`.
4. **±1 minute fallback**: if the result set is empty, try `HH:MM-1`, then `HH:MM+1` (handling hour/day wrap). If all three are empty, render a fallback "no quote for this minute" card showing only the time.
5. Pick a quote based on the user's `quote_selection` setting:
   - `shortest` (default): the row with the smallest `len(full_quote)`.
   - `random`: `random.choice(rows)`.
   - `daily`: deterministic per-day pick via `random.Random(seed=YYYY-MM-DD-HHMM).choice(rows)` so the same quote appears for the same minute on the same day across refreshes.
6. Sanitize the quote (strip `<br/>` variants, normalize NBSP, simplify smart quotes/em-dashes — same transforms mendhak applies).
7. Wrap the first case-insensitive occurrence of `time_human` in the quote with `<span class="highlight">…</span>`.
8. Build template params and call `BasePlugin.render_image(dimensions, "literature_clock.html", "literature_clock.css", template_params)` to produce a `PIL.Image`.

### Rendering (HTML/CSS)

- HTML extends `plugin.html` so InkyPi's font face declarations and `style_settings` (text color / background / margin / frame) are honored.
- CSS responsibilities:
  - Center the quote vertically and horizontally.
  - Auto-shrink font with `clamp()` (or a small JS sizing pass) keyed off quote character count, since e-ink resolutions vary widely (4" through 13.3").
  - Style the highlight span according to the user's `highlight_style` setting (bold / italic / underline / colored).
  - Optional attribution line below the quote (`— Book Title, Author Name`), truncated to ~55 chars.

### Settings (`settings.html`)

| Field | Type | Notes |
|---|---|---|
| `quote_selection` | radio | shortest (default), random, daily |
| `allow_nsfw` | checkbox | default off |
| `show_attribution` | checkbox | default on |
| `font_family` | dropdown | populated from `static/fonts/` via `generate_settings_template` |
| `highlight_style` | radio | bold, italic, underline, color |
| `highlight_color` | color picker | shown only when `highlight_style == color` |
| (style settings block) | InkyPi standard | text color, background, margin, frame — enabled via `style_settings = True` |

Form values are prepopulated from `pluginSettings` when editing an existing playlist instance.

### `plugin-info.json`

```json
{
  "display_name": "Literature Clock",
  "id": "literature_clock",
  "class": "LiteratureClock",
  "repository": "https://github.com/<user>/InkyPi-literature-clock"
}
```

## Edge Cases & Error Handling

- **No network on weekly refresh**: log a warning, keep using the cached/bundled CSV. Never raise — staleness is not a user-facing error.
- **No quote at HH:MM and HH:MM±1**: render a fallback card showing the time and a short message ("No quote for this minute"). This path must always succeed.
- **Corrupted CSV** (e.g. partial download): catch parse errors, fall back to the bundled file. If the bundled file is also unreadable, raise `RuntimeError("Literature clock dataset unavailable")` — surfaced in InkyPi's web UI per plugin convention.
- **Long quotes**: handled by font-size shrink in CSS; hard cap at the dataset's longest entry is acceptable since the `shortest` default avoids extremes.
- **Smart-quote / non-ASCII characters**: normalized before rendering (matches mendhak's transform table).

## Refresh Cadence

The plugin is stateless per call; the InkyPi playlist scheduler drives refresh. README will recommend a 1-minute playlist refresh interval since the clock semantics are minute-precise.

## Trade-offs Considered

- **Bundled CSV vs. fetch-on-demand**: Bundled with weekly refresh. Works offline immediately; stays current.
- **Pillow drawing vs. HTML/CSS rendering**: HTML/CSS. Inline highlighting and variable-length wrapping are far cleaner than Pillow text layout. Mendhak's repo uses SVG for the same reason; InkyPi's `render_image` already wraps Jinja + headless Chromium.
- **Quote selection default**: `shortest` matches mendhak's default and reads well on small displays.
- **Fallback policy**: ±1 minute (chosen) over a hard "no quote" card, since transient empties at certain minutes would otherwise dominate the user experience.

## Out of Scope (Future Work)

- Localized quote sets.
- Custom user-supplied quote files.
- Per-time-band font/style overrides.
