# swatplus-documentation

Documentation site for [SWAT+](https://github.com/swat-model/swatplus), built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

Published at https://swat-model.github.io/swatplus-documentation/

## Layout

```
swatplus-documentation/
├── mkdocs.yml       site config, theme, and nav
├── docs/            all documentation content and assets
├── pdf/             per-section PDF build pipeline (pandoc -> xelatex)
└── requirements.txt
```

## Develop

```bash
pip install -r requirements.txt
mkdocs serve
```

Then open `http://localhost:8000`.

## Build

```bash
mkdocs build
python3 pdf/build.py --repo . --out site
```

Static output, including per-section PDFs, is written to `site/`.

## Deploy

A GitHub Actions workflow (`.github/workflows/deploy.yml`) builds the site and PDFs and
publishes them to GitHub Pages on every push to `main`.
