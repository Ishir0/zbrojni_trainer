# Implementation status

Updated 2026-10-29. Local working app; no deployment, push or remote repository creation.

## Implemented

- React 19, TypeScript, Vite, Tailwind; local learner data in IndexedDB via a small persistence wrapper.
- Responsive Czech Dnes, Otázky, Pokrok, practice, summary, source/status and settings screens.
- One clear Continue action, 10/15/25-question sessions and whole-bank seen/unseen counts.
- One-click answers submit and advance together; the previous result and explanation remain above the next question. A brief click guard prevents accidental double-clicks from answering two questions. Confidence/hints are available before answering; number keys 1–3 submit directly. Last-answer feedback appears on the summary.
- Persisted attempts, confidence, assistance, feedback and position survive refresh. Sessions saved under the old confirm/next flow resume without duplicate attempts.
- Official answer feedback for correct and incorrect attempts, source page links and optional textual choice comparison. Pre-answer comparison marks the attempt as assisted.
- Precomputed GPT-6 Luna explanation drafts: concise/simpler text, option-specific reasoning, decisive detail, retained-source quotes and links where supplied. Short explanations may derive from the official correct answer, with that basis displayed. Drafts appear after submission and remain explicitly unreviewed. Evidence gaps show specific issues and can be filtered in the browser. Source/dataset/key checks run before publication; blocked items cannot contain explanatory prose. No runtime model/API key is needed.
- Confidence defaults to unknown. Hints, guesses and immediate retries cannot establish mastery.
- Randomized question scheduling: up to 60% due reviews, remaining slots for unseen questions; random selection within each topic, random topic order and shuffled final session order. Topic balance and whole-bank coverage remain. Targeted retries are randomized too. Once the bank is covered, optional future practice retains earliest-per-topic review priority. Sessions store their exact question order and selection reasons.
- Interval configuration: delayed confident unaided successes use 1/3/7/14/30 days; failure resets the evidence and uses 10 minutes; uncertain/assisted success uses 1 day. Immediate success does not increase the interval. Mastery requires three delayed confident unaided successes and a latest confident unaided success.
- Search across text/number (accent insensitive), topic/status filters, bookmarks and paginated results. Browsing never creates retrieval attempts.
- JSON backup round-trip, validation, explicit merge/replace choices and confirmed reset. Merge deduplicates attempt IDs and retains the active local session.
- Focus states, native radio semantics, keyboard shortcuts, native modal focus handling, reduced motion and feedback distinguished by text/icons as well as colour.

## Retained and extracted content

- Downloaded the original Ministry PDF (219 pages; 3,221,833 bytes) on 2026-10-20.
- SHA-256: `edd539efc9e504f067d9f5b9409475935a08938c02fbb41c768b1a3f205a04a4`.
- All 837 contiguous questions, all 2,511 options and 73 extracted original image assets associated with 71 questions.
- Five source sections: 561 firearms-law questions, 48 implementing-regulation questions, 39 other-law questions, 151 arms/ammunition questions, 38 first-aid questions.
- Key extraction uses the original italic answer markers. Questions 716 and 717 instead use grey highlighting; their A/B keys were checked visually on original pages 190–191.
- Recovered 341 malformed font ligatures (`ft`, `ti`, `tí`) using their distinct original CIDs. Recovery is tied to the source checksum; ordered surrounding word contexts are cross-checked independently. Official wording/source typos are preserved; whitespace and presentation ligatures are normalized.
- Independent `pdftotext -layout` comparison matches every extracted stem and option (837 questions; zero text differences after whitespace normalization). This is independent text extraction, not a second key-format verifier.
- Visual comparison of exact text, all choices and keys for 20 questions across every source section, including illustrated questions 649 and 650. See `sources/sample-review.json`.
- Complete-bank manual text/key/illustration audit remains unfinished. Per-item status distinguishes visual sample review from automatic format checks. No explanation has been certified by the agent.
- Retained the original 45 PDFs linked by the Ministry/Red Cross, including a duplicate official-bank copy, Ministry training/interpretation documents, first-aid standards and all eight linked 2026 amendment sheets.
- Retained rendered official text for 17 laws/regulations from e-Sbírka with checksums and displayed version context, including Act 90/2024, the four implementing regulations, Charter, Criminal Code, proof-testing rules and related acts cited by the bank.
- Additional technical sources include the AFTE glossary, official ČÚZZS proof-mark charts and C.I.P. cartridge tables. TIS and ZZS Prague material supplements Red Cross first-aid guidance; historical material is identified in source titles. Draft/source provenance is retained in the manifest and passage index.
- Rendered legal snapshots include website navigation. Before editorial use, verify section completeness, effective dates, repealed provisions and relevance. The collection is a source base, not a completed question-to-provision applicability audit.

- Explanation pack: all 837 questions processed; 834 AI drafts (80 derived from the official answer), with 3 first-aid items pending review (809, 820, 830). Complete assembly has zero validation errors and zero missing records.

## Verification

- `npm run ingest`: all 837 questions/keys structurally valid; independent layout text comparison reports zero differences.
- `npm test`: 24 focused tests pass, including whole-bank traversal across 84 sessions, unseen-question reservation, topic balance, mastery signals, duplicate protection, source checksums, image references, validation and backup merge.
- `npm run test:e2e`: 20 checks pass across desktop (1440×1080) and mobile (390×844), including two axe WCAG A/AA checks covering home, question and feedback. Explanation checks cover disclosure after submission, selected-choice reasoning, exact source links, persistence, missing-pack fallback, unresolved-evidence feedback and filtering.
- Functional browser checks cover one-click submission and advancement, previous feedback above the next question, duplicate clicks, reload/pause/resume, session completion and continuation, export/reset/import, legacy answered sessions, illustrated search results, bookmarks, browsing exclusion and assisted keyboard answers.
- Production TypeScript check and Vite build pass. Dependency installation reports zero known vulnerabilities.
- Visually inspected representative source pages and desktop/mobile home, feedback and illustrated question screens. Automated accessibility checks do not replace assistive-technology user testing.

## Remaining before release

1. Independent legal/medical editorial review of the AI drafts and source applicability, resolving evidence gaps and source/key conflicts, short lessons and reviewed conceptual difference annotations. Current diff is explicitly textual only.
2. A complete manual audit of source text/keys/images; meaningful text alternatives for source illustrations still need editorial work.
3. Concept-level histories, misconceptions and related-question transfer checks. Current scheduler is question-level and does not claim validated personalized effectiveness.
4. Official exam simulation. Act 90/2024 §31 and Regulation 238/2025 §§12–14 are retained, including duration/pass counts and subject quotas. The bank-to-exam subject mapping, especially safety vs technical questions, is not yet verified. The simulation remains disabled.
5. Fine-grained question revisions and mature migrations. Current schema is v1. A dataset change preserves raw history but conservatively renews current-version learning evidence and clears the active session. Import from a different dataset version is explicitly rejected pending migration support. Spelling-only changes are not distinguished yet.
6. Full offline/install support, atomic content caching and release/deployment checks. The UI accurately states that opening the app/source PDFs requires connectivity.
7. Optional diagnostic, exam-date/daily-goal planning, issue reporting and localization beyond separated content. No accounts, sync or live AI are implemented.

Official questions and keys remain source-derived. AI explanations are separately labelled drafts with citations and unresolved items are withheld. No pass probabilities are claimed.
