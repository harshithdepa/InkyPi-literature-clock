# InkyPi-literature-clock

![Example of InkyPi-literature-clock](./example.png)

*InkyPi-literature-clock* is a plugin for [InkyPi](https://github.com/fatihak/InkyPi) that displays a literary quote referencing the current minute, with the time phrase highlighted — a literature clock in the spirit of [Author Clock](https://www.authorclock.com/) and [Jaap Meijers' literary clock](https://github.com/JohannesNE/literature-clock).

**What it does:**

- **Quote of the minute** — Picks a literary passage that contains a phrase referencing the current `HH:MM`, with that phrase highlighted (bold / italic / underline / color).
- **Selection strategy** — Choose `shortest` (best on small displays), `random`, or `daily` (deterministic per minute per day, so the same quote stays put within a minute).
- **Attribution** — Optional book title and author line below the quote.
- **Offline-first** — Bundles the JohannesNE/literature-clock dataset (~3,600 quotes) and refreshes weekly when online; works fully offline if the network is unavailable.
- **Graceful gaps** — A handful of minutes have no exact-time quote in the dataset; the plugin falls back to ±1 minute, then to a clean "no quote" card.
- **Responsive layout** — Five font-size tiers based on quote length, so long passages still fit and short ones still feel at home on small displays.

The plugin uses no external APIs and requires no API key.

**Quote source:** [JohannesNE/literature-clock](https://github.com/JohannesNE/literature-clock) (`litclock_annotated.csv`), the same dataset used by [mendhak/waveshare-epaper-display](https://github.com/mendhak/waveshare-epaper-display)'s privacy mode.

**Requirements:**

- InkyPi running on a Raspberry Pi.
- No additional Python dependencies (uses libraries already shipped with InkyPi).

---

**Settings:**

![Screenshot of settings of InkyPi-literature-clock](./settings.png)

- **Quote selection** — `shortest` (default), `random`, or `daily`.
- **Allow NSFW quotes** — Off by default. The dataset flags a small number of quotes; enable this only if you want them included.
- **Show attribution** — Toggle the book/author line below the quote.
- **Font** — Any font available in InkyPi's `static/fonts/`.
- **Highlight style** — `bold` (default), `italic`, `underline`, or `color`.
- **Highlight color** — Custom color picker, used when highlight style is `color`.
- Standard InkyPi style settings (text color, background, margin, frame) apply.

**Recommended refresh:** set the playlist refresh interval to **1 minute** for true clock semantics.

---

## Installation

Install the plugin using the InkyPi CLI with the plugin ID and repository URL:

```bash
inkypi plugin install literature_clock https://github.com/harshithdepa/InkyPi-literature-clock
```

Or install the [Plugin Manager](https://github.com/RobinWts/InkyPi-Plugin-PluginManager) first and install this plugin via the Web UI.

Then add a Literature Clock instance to a playlist and configure the settings as desired.

---

## Development status

Actively maintained.

---

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).
