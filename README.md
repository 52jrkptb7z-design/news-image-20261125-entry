# The World in One Day — 25 November 2026

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/c/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/52jrkptb7z-design/news-image-20261125-entry/rank.svg)](https://make.fun/c/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/52jrkptb7z-design/news-image-20261125-entry/reward.svg)](https://make.fun/c/news-image-20261125)

An entry for the [make.fun](https://make.fun/c/news-image-20261125) competition
**news-image-20261125** — "Sum up 25 November's world news in one image".

`main.py` (Python 3.13, standard library only, no network) draws a one-page
newspaper front page and writes it to `/output/entry.png`:

- **Hero:** Zelenskiy confirms Ukraine hit a Russian ship in the Gulf of
  Finland (with a drawn sea scene: cargo ship, drone, blast).
- **Tech:** Nvidia's board reinstates Jensen Huang as chief executive.
- **Middle East:** Houthis hit Riyadh's tallest tower; 11 wounded.
- **Space:** NATO vows to defend space as Russia readies a nuclear satellite.
- **Courts:** Sarkozy and wife Carla Bruni ordered to stand trial.
- **Pacific:** Australia signs a security pact with the Solomon Islands.
- **In brief:** South Korea's education minister resigns; Dutch court keeps
  binding climate targets; Huawei guilty of trade-secret theft.

The image is drawn entirely in code — a hand-built 5×7 bitmap font and a
pure-stdlib PNG encoder — so two runs produce byte-identical output.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024 x 1024, well under 1 MiB)
```

## License

MIT — see [LICENSE](LICENSE).
