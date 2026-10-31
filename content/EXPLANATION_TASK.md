## Updated user direction (2026-10-20)

The user requested short, practical explanations and explicitly allowed extrapolation from the official correct answer. For remaining questions, `evidenceBasis: "official-answer"` permits a reasoned draft with `sources: []`. Do not invent extra facts or quantitative claims beyond the key. The app labels this basis. Existing source-grounded drafts retain their evidence. General web sources can be cited without exact quotes using `evidenceType: "web-reference"`, URL-derived sourceId, actual HTTPS URL, title, locator, and empty file/quote strings. Existing source-grounded legal drafts retain their exact citations; a few remaining legal rationales may explicitly derive from the official answer as well. Clear conflicts between official first-aid keys and current guidance remain flagged rather than rationalized.

# Source-grounded AI explanation drafting contract

User explicitly authorized GPT-6 Luna subagents to precompute explanations for all 837 official Czech firearms-permit questions, using the underlying law, guidelines, and illustrations. Working directory /home/ishir/Workspace/Zbrojni_trainer. Read BUILD_SPEC.md, especially source authority. You may draft legal/first-aid explanations; do not claim professional review or change official keys. No paid API calls or keys are needed. Do not deploy or push.

Inputs: public/data/questions.json; sources/source-manifest.json (61 retained official references); sources/references/law-*.txt (rendered official legal texts, includes navigation); source PDFs and original images public/data/images. Additional PDF page text is being prepared under sources/text and sources/passages.json by the parent agent. Use actual source excerpts, not memory. All existing question text/keys remain fixed.

Output: a JSON ARRAY at your assigned file in content/explanations/. Each record:
```
{
 "questionId":"q-1",
 "datasetVersion":"copy from question",
 "correctOptionId":"copy from question",
 "status":"ai-draft",
 "concise":"2–3 concise Czech sentences teaching why the official answer follows from the supporting rule. Do not merely repeat the answer.",
 "simpler":"Optional plain-language paraphrase without losing conditions.",
 "optionReasoning":{"A":"Short reason this exact answer is right/wrong.","B":"...","C":"..."},
 "decisiveDetail":"The condition/exception/negation/category that distinguishes the choices, or empty if unnecessary.",
 "sources":[{"sourceId":"source ID from sources/passages.json when available; otherwise sha256(URL)[:12] prefixed s-","url":"actual manifest URL","file":"actual repo-relative source text file or PDF path","locator":"§ / odst. or PDF page, precise enough to locate the quote","quote":"Exact contiguous quote from that retained source text (short enough for a learner; usually <500 characters)."}],
 "issues":[],
 "model":"gpt-6-luna"
}
```

If evidence is missing, source is illegible, image not inspected or official key conflicts with retrieved rule: use status `needs-source`, concise/simpler/decisiveDetail empty, optionReasoning empty strings for A/B/C, sources [] or actually inspected evidence, and a specific Czech `issues` entry. Do not generate unsupported authoritative prose just to reach 100% coverage. Aim for useful grounded drafts wherever the retained sources support them.

You must inspect illustrations used to reason about illustrated questions with view_image (and PDF skill as applicable). Purely textual source assertions do not establish an image's identity. Never cite another app's proprietary explanations. Use no universal answer-length shortcut. Respect current source versions and flag discrepancies.

Work through ALL assigned question numbers. Write progress incrementally to your own output file after every small batch, so work survives context compaction. Do not write src/, public/data/questions.json, shared scripts, or other agents' files. You may create your own helper files under content/explanations/ and tmp/. The parent handles app integration and automated validation. Send an early message with your initial source coverage and a small completed sample; then continue through the entire assignment without stopping at the sample. If a turn/context limit approaches, ensure partial results are saved and report exactly where to continue. A final response should give counts ai-draft/needs-source, source gaps and validation done.
