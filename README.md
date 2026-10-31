# Zbrojní

Czech-first preparation for the firearms permit exam. A working React app with the official 837-question bank, original illustrations and a persistent learning plan across short sessions.

## Run locally

Requires Node.js 22.12+ and npm.

```sh
npm ci
npm run dev
```

Open http://localhost:5173. No accounts, server database or AI credentials are needed. Progress is stored in this browser's IndexedDB. Export/import backups in **Nastavení**. Full offline support is not implemented.

## Run with Docker

Install Docker Engine with Compose (or Docker Desktop), then from this directory run:

```sh
docker compose up --build -d
```

Open http://localhost:8080. Stop it with `docker compose down`. Compose builds a small static web-server image from the app; progress remains in each visitor's browser, so the container needs no database or data volume. To let friends use it, the computer running Docker must be reachable by them (for example, on the same home network, or through a hosted server/VPN).

## Package for a Mac

Run `npm run package:mac` on the build computer. This creates `release/Zbrojni-Trainer-Mac.zip`. Copy the ZIP to a USB drive, unzip it on the Mac, and open `Start.command` in the extracted folder. Python 3 is required to serve the static files locally; see the included `README.txt` for the Mac steps. Browser progress stays on that Mac and in that browser.

```sh
npm run build
npm run preview
npm test
npx playwright install chromium
npm run test:e2e
```

The build output is `dist/`, suitable for static hosting. Nothing has been deployed.

## What works

- Dnes → practice → click an answer → previous result/explanation above the next question → summary.
- Sessions of 10, 15 or 25 questions; one Continue action restores the current question, previous feedback and saved session order after reload.
- Random question selection within unseen/due-review pools, shuffled session order, whole-bank coverage, topic balance, confidence and assistance tracking. Existing sessions keep their saved order; new sessions are randomized.
- Question search by number or accent-insensitive text; topic/status filters and bookmarks.
- Original illustrations, original A/B/C option order, one-click answers, keyboard shortcuts (1–3 submit), and mobile layouts.
- Progress export/import with validation, explicit merge/replace choices and confirmed reset.

Precomputed GPT-6 Luna explanations appear after answer submission, with a shorter version and reasoning for each choice. Most legal drafts cite retained source quotations. Drafts can also explain the official correct answer directly; the app labels that basis, and general web references need no exact quotation. They are labelled as AI drafts without professional review. Questions with unresolved evidence show the specific issue; use **Čeká na podklady** in the question browser to find them. No runtime API calls or API key are required.

Short theory lessons and reviewed conceptual difference annotations are pending editorial review. Current comparison highlights are explicitly labelled as text differences. Official exam simulation is disabled until its complete content mapping and rules have been verified.

## Content and extraction

The original Ministry PDF and supporting references are retained under `sources/`. See `source-manifest.json`, `validation-report.json`, `text-comparison-report.json` and `sample-review.json` for provenance and verification limits. Sources are not bundled into the published website; the app links to their official URLs.

Rebuild the dataset with system Poppler (`pdftohtml`, `pdftotext`):

```sh
npm run ingest
```

This source snapshot contains malformed ToUnicode mappings. A checked-in, source-checksum-bound repair manifest recovers 341 ligatures using their distinct original font character IDs. `scripts/repair_ligatures.py` regenerates that manifest with `pypdf` installed. No legal inference is used to recover keys. Two source choices use grey highlighting without italics and are recorded as visual exceptions.

`npm run ingest` compares all 837 stems and all 2,511 choices against an independent layout-text extraction, ignoring whitespace and normalizing known presentation ligatures. This is an automated comparison plus a 20-question visual sample, not a complete human editorial audit.

Supporting sources can be recollected with `python3 scripts/collect_sources.py`, then `node scripts/collect_laws.mjs` (Playwright Chromium required). These commands need internet access. Legal pages are archived with their displayed current-version context; section-level applicability still requires review.

Explanation source text and page/section passages are generated locally with `npm run build:explanation-sources`. Drafts live in `content/explanations/`; `npm run validate:explanations` validates and publishes the complete pack to `public/data/explanations.json`. The validator preserves the official keys, checks dataset identity and retained-source quotations where supplied, rejects generic filler, and prevents blocked prose from reaching the app. It does not certify that a quotation supports every inference or replace legal/medical review. See `sources/explanation-validation-report.json` for current coverage and validation results.

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for remaining scope and checks.
