# Zbrojní oprávnění — product and implementation specification

> **User update, 2026-10-29:** New practice sessions randomly select questions within unseen/due-review pools and shuffle their final order while preserving topic coverage and saved-session continuity. Clicking an answer (or pressing 1–3) submits and advances immediately; the previous result and explanation appear above the next question. Confidence/hints come before answering, and the final result appears on the summary. These requirements supersede the earlier deterministic scheduling and separate confirmation/Next controls below. Original A/B/C option order and official mock-exam verification requirements still apply.

Status: proposed v0.1 for implementation in Codex CLI. Product name is a working title.

## 1. Product intent

Build a Czech-first, mobile-friendly web app that teaches the official zbrojní oprávnění question bank and the understanding behind it. The experience should feel like a thoughtful tutor: open it, see one clear next action, practise, understand a mistake, and leave knowing what improved.

The app owns the learning workflow. Users should not need to create notes, configure flashcards, organise decks, engineer prompts, or understand a repetition algorithm. The official bank is prepared and available on first use.

Success means both reliable recall of official answers and understanding of the distinctions they test. A correct guess is useful evidence but does not establish mastery. All official questions must remain discoverable and eventually enter the learning plan.

Do not build a general document-upload platform for v1. Keep the internal content model reusable, but optimise the interface for this exam.

## 2. Primary audience and language

- Adults preparing for the Czech examination, including people unfamiliar with legal language or returning to study after many years.
- Czech interface, preserving Czech diacritics and the exact official question wording.
- An optional simpler explanation is available to everyone; do not label people by intelligence or reading ability.
- English translation and interface localisation are later features. Keep UI strings separate enough to add them without rewriting the app.

## 3. UX principles

1. One obvious next step. The primary action is usually “Pokračovat v učení”.
2. Short, manageable sessions. Default to around ten questions, with an easy way to continue or stop.
3. Explain the distinction. Feedback names the rule and the particular detail that changes the answer.
4. Progressive detail. Show a concise explanation first, then simpler wording, an example, and the source on demand.
5. Treat errors calmly. No shame, punitive streak resets, public rankings, or celebratory clutter after every answer.
6. Measure independent knowledge. Record hints and separate assisted answers from unaided answers.
7. Make trust visible. Show content version, source links and editorial status without cluttering the question screen.
8. Accessible throughout. Keyboard use, screen readers, visible focus, adequate contrast, large touch targets and reduced motion.

## 4. Navigation and screens

Use three main destinations: Dnes, Otázky, Pokrok. Place theory lessons in the question browser and link directly from feedback. Put settings and source/version information in secondary navigation.

### 4.1 First visit

Explain the value in one short screen: official questions, explanations and a personal revision plan. Let the user start immediately without registration. Offer a short diagnostic, which can be skipped. An exam date and daily study time are optional; no long questionnaire.

Clearly state that progress is stored on this device in the first version, with export/import available. Do not imply cloud backup or cross-device sync.

### 4.2 Dnes

The top of the screen answers: “What should I do now?” Show:

- One main action: continue/start a suggested session.
- A short reason, such as “Zopakujeme si pojmy, které se ti minule pletly.”
- A modest overview of due reviews and new material, without an intimidating backlog.
- Secondary entry to a mock exam and the question browser.

Do not make this a dashboard of many equally prominent widgets. Avoid a fabricated probability of passing.

### 4.3 Practice screen

Show one question at a time, with generous spacing and readable option cards.

- Exact official stem and all official options; include any original illustration.
- Topic and unobtrusive session position.
- Select an option, then explicitly confirm with “Odpovědět”. Selection alone must not reveal the answer.
- An optional pre-submission confidence choice: “Vím / Nejsem si jistý/á / Tipuji”. Default is unknown, never inferred certainty.
- An optional hint button. The first hint may point to a relevant condition; a further hint may show answer differences.
- Keyboard shortcuts for answer choices and submission, with no accidental double submission.
- Pause/exit preserves progress. A refresh restores the current session.

Preserve original answer ordering in v1, retaining stable option IDs. A future shuffled mode must be disabled for options that refer to letters or ordering; it must always maintain correct answer mappings.

### 4.4 Feedback

After submission, keep the question and options visible. Mark the selected choice and correct choice using text/icons as well as colour.

Show in this order:

1. Clear result.
2. A one- or two-sentence explanation of the deciding rule.
3. The reason the selected wrong answer fails, if applicable.
4. Optional “Rozdíly v odpovědích” to compare all three choices.
5. Optional “Vysvětlit jednoduše”, “Proč ostatní neplatí?”, “Související teorie” and source reference.
6. A clear next-question action.

Correct answers still receive a concise explanation. A correct low-confidence answer should be revisited earlier than repeated confident unaided success. Do not force users to read a long explanation after every answer.

### 4.5 Answer-difference view

This is a core feature. Compare the exact choices and emphasise the words or clauses that change meaning: negation, conjunction, deadline, scope, exception, category, permission or obligation.

Each highlight has a short explanation. Distinguish a textual difference from a verified conceptual distinction: an automatic text diff may suggest candidates, but only reviewed annotations may teach that a difference is decisive. Do not invent a universal shortcut such as “the longest answer is correct”.

Use underline/background plus a textual label; do not rely on red/green. Support character ranges within original strings, including Czech Unicode text. Never alter the official wording to simplify the comparison.

Illustrative design example, not an official question: one choice says “a”, another “nebo”. The annotation explains the difference between both conditions being required and either condition being sufficient. Production examples require a verified question-specific rule.

In normal practice, expose this after answering or when the learner explicitly asks for help. Answers after a pre-answer highlight are recorded as assisted. Later reviews should offer an opportunity to answer without that help.

### 4.6 Session end

Show a compact summary: what was practised, what improved, and what needs review. Separate assisted successes, independent successes and incorrect answers. Offer “Probrat chyby”, “Pokračovat” and “Hotovo”. Immediate retries do not count as delayed mastery.

### 4.7 Otázky and theory

Search all questions by text and official number. Filter by topic, unseen, incorrect, uncertain and bookmarked. Opening a question exposes the same explanation and source view used in practice. Browsing an answer does not count as a successful retrieval attempt.

Theory consists of short connected lessons with definitions, rules, examples and sources. Show which questions a lesson supports. Keep an easy route back to the interrupted practice session.

### 4.8 Mock exam

Provide timed, unaided exams using the verified current official sampling, scoring and pass rules. Keep all hint and explanatory features hidden until submission. Permit answer changes and unanswered questions according to the verified rules. Preserve the timer across refresh using timestamps.

If current exam rules are not verified, disable the official simulation and explain that it is awaiting verification. A separately labelled practice test may work without claiming official fidelity.

Results show the outcome under the loaded rule version, topic breakdown and a review of answers. Mock-exam attempts are recorded separately and must not use per-question feedback during the exam.

### 4.9 Pokrok

Report total coverage, unseen questions, delayed unaided performance, review needs and topic weaknesses. Define each mastery label in plain language. Readiness indicators require sufficient fresh, unassisted evidence and show limitations; do not equate seeing every question with being ready.

## 5. Adaptive practice

Keep scheduling deterministic, explainable and independent of any language-model call. Track individual questions and their associated concepts. Persist confidence, assistance, timestamp, selected option and result for each attempt.

For v1, use a documented simple policy with configurable intervals rather than inventing an opaque AI model:

- Prioritise due reviews and recent misconceptions while reserving room for unseen content.
- A starting ten-question session may contain six reviews, three unseen questions and one related-question check. Rebalance when a pool is empty.
- Avoid repeatedly drilling one topic while the rest of the bank remains unseen.
- A wrong confident answer is a useful signal to teach the associated distinction; it is not a diagnosis of the learner.
- A correct guess, assisted answer or immediate retry cannot establish mastery.
- Increase intervals after delayed unaided success. Shorten them after failure or uncertainty. Define the initial interval table in configuration and test it; do not market it as a validated personalised model.
- Use related questions to check transfer after a concept explanation, without assuming that one success proves every related question is known.
- Missing confidence remains unknown; slow responses alone do not count as poor knowledge.
- Handle newly added or revised questions explicitly. A changed answer/rule requires renewed review; a spelling correction need not discard all history.

Keep the scheduling interface replaceable so a well-tested scheduler such as FSRS can be evaluated later. The recommendation screen should be able to explain why each question was selected.

## 6. Content and authority

Known starting sources, to recheck at ingestion time:

- Official Ministry question bank, previously checked as 837 numbered questions: https://mv.gov.cz/soubor/mv-soubor-testovych-otazek-pro-teoretickou-cast-zkousky-odborne-zpusobilosti-a-komisionalni-zkousku.aspx
- Ministry legislation and training resources: https://mv.gov.cz/novy-zakon-o-zbranich
- Act 90/2024 in the official collection: https://e-sbirka.gov.cz/sb/2024/90

These links are starting points, not a claim that every source or rule has been verified for the implementation date. Obtain current exam regulations and applicable legal provisions from official sources. First-aid explanations also require appropriate current authoritative sources and review.

The official bank controls exam question wording and answer keys. Legal/theoretical sources support explanations. Keep these separate so a disagreement can be flagged instead of silently changing an official answer.

### 6.1 Ingestion pipeline

1. Download and retain the original source with retrieval date and SHA-256 checksum.
2. Extract question numbers, stems, options, answer keys, sections and illustrations. Correct-answer formatting may be lost in plain-text extraction; inspect the original formatting and do not infer keys from an LLM's reasoning.
3. Validate numbering, duplicates, missing choices, answer mappings, image references and extraction artefacts such as page headers.
4. Compare all extracted questions and keys against the original source before calling the dataset complete. Record the verification method and unresolved items.
5. Add concepts, explanations, option-specific feedback, source references and reviewed difference annotations.
6. Publish a versioned dataset with an explicit review status per item.

Do not scrape another app's proprietary explanations. Record content provenance and check applicable reuse terms before public release.

### 6.2 Editorial workflow

Use draft → reviewed → published statuses, with separate tracking for official-text/key verification and explanation review. Every explanation references supporting source sections and the relevant effective date where applicable. Store who/what performed review and when. AI may draft explanations but may not certify its own legal or medical accuracy.

If a reviewed explanation is unavailable, show the verified official answer and a truthful pending-review message. Never fill a gap with authoritative-sounding generated text. A reported question can be flagged for review without changing learner history.

### 6.3 Minimum content model

- SourceDocument: ID, title, URL, retrieval/effective dates, checksum, version, local asset reference.
- Question: stable ID, official number, exact stem, stable option IDs/text, correct option ID, topic/concept IDs, source/page, dataset version, official verification status.
- Explanation: concise/simpler text, per-option reasoning, optional example, source-section references, review status/date.
- DifferenceAnnotation: option ID, start/end offsets, exact expected text, category, explanatory note, review status. Validate offsets against expected text when building.
- Lesson: title, concepts, sections, source references, related questions, review status.
- ExamRules: version, effective date, sampling quotas, duration, scoring/pass criteria and official references; include any relevant applicant variant only when verified.
- Attempt: question/version, option selected, mode, result, confidence or unknown, assistance flags, timestamps and session ID.
- LearnerState: question/concept history, next review, interval, mastery evidence and bookmarks.

## 7. Technical starting point

Default unless the user chooses otherwise: TypeScript, React, Vite, Tailwind CSS, and IndexedDB for local learner data. Use a small persistence wrapper with schema migrations. Load versioned static JSON content and local assets. Use a maintained accessible component primitive library only where it saves real effort; avoid building a large design system first.

This delivers a static-hostable app without accounts, a database server or paid AI calls. Store content separately from components, scheduler separately from rendering, and learner data separately from published content. Define interfaces so server sync can be added later.

Provide JSON export/import of progress with schema version, validation and explicit merge/replace behaviour. Users can reset their local progress with confirmation. Keep runtime API secrets out of the browser; no AI API integration in v1.

Add an installable/offline experience after the basic flow works. Cache content versions atomically so a partly downloaded update cannot mix question keys from different versions. User progress must survive a content update. If full offline support is deferred, say so accurately in the UI.

## 8. Visual direction

Calm, crisp and approachable. A restrained neutral palette with one accent, readable Czech typography, generous line height and clear hierarchy. Mobile-first question screens should feel comfortable with one hand. Desktop should use readable content widths, not stretched text or a dashboard full of empty cards.

Use selected/hover/focus/disabled/loading/error states consistently. Respect reduced-motion preferences. Avoid military decoration, weapon imagery as background, dense admin tables, marketing hero sections in the study flow, and oversized statistics that compete with the next action.

## 9. Scope and delivery order

### Milestone 1 — a complete, small learning loop

- Start with 15–25 real official questions across varied topics, including close answer variants and an illustration where available.
- Verify exact text and keys for this sample; keep unfinished explanations visibly pending review.
- Build Dnes → question → submission → explanation/difference view → next → summary.
- Persist attempts and resume state locally.
- Include the basic question browser and progress overview.
- Make the flow usable on mobile and desktop before expanding the bank.

### Milestone 2 — complete bank and adaptive practice

- Ingest and validate the full current bank, with a completeness report.
- Add deterministic scheduling, confidence and assistance tracking, concept links and short theory lessons.
- Expand reviewed explanations and difference annotations; report coverage honestly.
- Add progress export/import and robust version migrations.

### Milestone 3 — exam fidelity and release readiness

- Implement simulation from verified official rules.
- Verify keyboard, screen-reader semantics, contrast, mobile layout and browser refresh behaviour.
- Add offline/install support if feasible without compromising content consistency.
- Document remaining editorial review and deployment steps.

Later: optional accounts/sync, instructor review tools, question-level issue reporting to a server, audio, multilingual explanations, opt-in conversational tutor, and richer readiness modelling. Live AI must use approved sources and must never overwrite official answer keys.

## 10. Acceptance criteria

- The user can start practising from the home screen without creating an account.
- Every displayed official question and answer key maps to a versioned source record.
- Selecting an option does not submit it. Submission is recorded once.
- Feedback addresses the selected answer and offers an explanation after correct answers too.
- Difference highlights have correct offsets and meaningful reviewed notes; the official text stays intact.
- Hinted answers remain visibly distinct from independent success in history and progress.
- Refreshing mid-session restores the active question and completed answers without duplicate attempts.
- Due reviews do not permanently prevent new-question coverage.
- Question search and filters work across the loaded dataset.
- Dataset counts reflect the actual loaded version, rather than a hard-coded 837.
- No guessed answer keys, fabricated citations, invented official exam rules, or placeholder pass probabilities.
- Exams show no answer feedback or hints before submission and survive refresh without resetting time.
- Local progress export/import round-trips and rejects malformed or incompatible data clearly.
- The core study flow is keyboard-operable, readable at mobile widths and does not rely on colour alone.
- Production build and focused automated tests pass; report any unrun checks or unresolved content gaps.

## 11. Verification strategy

Use unit tests for scheduling decisions, assisted/confidence handling, source-data validation, annotation offsets and progress migrations. Use integration or browser tests for submission, reload/resume, feedback, progress export/import and exam timing/submission. Verify representative mobile and desktop layouts visually. Test content parsing against source fixtures, with explicit checks that PDF formatting has not lost the correct-answer markers.

Avoid large suites that only mirror component implementation. Prioritise failures that would teach a wrong answer, lose progress, misreport mastery or invalidate exam behaviour.

## 12. Instructions to the implementing Codex agent

Read this specification and applicable AGENTS.md files. Inspect the repository before changing it. Work through milestones in order, making routine implementation choices without repeated approval requests. First deliver the working vertical slice, then expand it. Use clearly labelled fixtures only when required; never present invented questions as official.

Maintain a short implementation-status document recording completed scope, source/data verification, checks run and remaining work. If network or source access is blocked, complete independent UI work and report the specific blocker; do not silently substitute unverified content. Do not publish, deploy, create a remote repository or push without user authorisation.

The result should be a working app with truthful content status, not only a plan or a static mockup.
