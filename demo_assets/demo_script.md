# AI Tutor Orchestrator - Hackathon Demo Script

**Duration: 5 minutes total**

## Section A — 90-Second Scripted Walkthrough

### Opening (10 seconds)
**Speaker:** "Welcome to the AI Tutor Orchestrator! This system intelligently routes student requests to specialized AI tutors. Let me show you three scenarios in action."

Time 0:00–0:30 — Flashcard Generator
- Exact user utterance: "I'm struggling with calculus derivatives and need some practice problems"
- Orchestrator actions:
  1) tool_selector_node → flashcard_generator (intent cue: "practice problems")
  2) parameter_extractor_node → infers difficulty = easy (phrases: "struggling"), num_cards = 5 (safe default), language = en; uses CURRENT_MESSAGE as source_text
  3) parameter_validator_node → validates against schema (length bounds, enums)
  4) tool_caller_node → mock tool returns n cards
- Expected output (summary):
  {
    "tool": "flashcard_generator",
    "parameters": {"source_text": "...derivatives...", "card_style": "qa", "num_cards": 5, "difficulty": "easy", "language": "en"},
    "result": {"cards": [{"front": "Q1", "back": "A1"}, ...], "format": "qa"}
  }

Time 0:30–1:00 — Note Maker
- Exact user utterance: "Make notes on the water cycle in an outline format — include analogies"
- Orchestrator actions:
  1) tool_selector_node → note_maker (intent cues: "Make notes", "outline")
  2) parameter_extractor_node → note_style=outline (explicit), include_sections includes ["examples"] (from "analogies"), target_length=medium (default), language=en; source_text from CURRENT_MESSAGE
  3) validate → ok; call tool → notes content
- Expected output (summary):
  {
    "tool": "note_maker",
    "parameters": {"source_text": "...water cycle...", "note_style": "outline", "target_length": "medium", "language": "en"},
    "result": {"notes": "Notes (outline)...", "sections": ["summary", "key_points"]}
  }

Time 1:00–1:30 — Concept Explainer
- Exact user utterance: "Explain photosynthesis at an intermediate level. Give 2 practice questions."
- Orchestrator actions:
  1) tool_selector_node → concept_explainer (intent: "Explain")
  2) parameter_extractor_node → concept="photosynthesis", prior_knowledge=intermediate, examples_count=2, include_quiz=true ("practice questions"), language=en
  3) validate → ok; call tool → explanation + examples + quiz
- Expected output (summary):
  {
    "tool": "concept_explainer",
    "parameters": {"concept": "photosynthesis", "prior_knowledge": "intermediate", "examples_count": 2, "include_quiz": true},
    "result": {"explanation": "...", "examples": ["Example 1", "Example 2"], "key_points": ["definition", "intuition"], "quiz_questions": ["Q1", "Q2"]}
  }

Section B — Full 5-minute spoken script

0:00–0:30 — Opening
“Hi, we built an Autonomous AI Tutor Orchestrator. It’s schema-driven: we extract structured parameters from user input, validate with Pydantic, and route to tools like Note Maker, Flashcard Generator, and Concept Explainer. Today, I’ll show accuracy-focused extraction, strict validation, and a clean UX flow.”

0:30–1:00 — Architecture at a glance
“Our architecture has five steps: parameter_extractor_node (LLM with schema-guided prompt), parameter_validator_node (Pydantic models from the PDF), tool_selector_node (intent→tool mapping), tool_caller_node (retries/backoff, mock mode), response_formatter_node (normalized outputs). This keeps the system reliable and extensible.”

1:00–2:30 — Demo Scenario 1: Flashcards
“Let’s ask: ‘I’m struggling with calculus derivatives and need some practice problems.’ The workflow selects Flashcard Generator. The extractor infers difficulty ‘easy’ from ‘struggling’, defaults num_cards to 5, language to ‘en’, and uses the message as source_text. Validators check bounds. The tool client returns QA cards. You can see per-field parameters and the generated cards.”

2:30–3:30 — Demo Scenario 2: Note Maker
“Next, ‘Make notes on the water cycle in an outline format — include analogies.’ Tool: Note Maker. The extractor sets note_style=outline (explicit), includes examples (from ‘analogies’), and target_length=medium as default. Validation passes; the mock tool returns structured notes with sections. This demonstrates schema-driven, low-friction note-making.”

3:30–4:15 — Demo Scenario 3: Concept Explainer
“Finally, ‘Explain photosynthesis at an intermediate level. Give 2 practice questions.’ Tool: Concept Explainer. The extractor sets prior_knowledge=intermediate, examples_count=2, include_quiz=true. We get a concise explanation, examples, and a short quiz. The response formatter standardizes the output structure.”

4:15–4:45 — Why this works well
“Accuracy comes from schema-first prompts and Pydantic validation. Tool reliability comes from adapters with retry/backoff and mock mode. UX is transparent: if required fields are missing, we ask one clarifying question instead of failing.”

4:45–5:00 — Close
“This is production-ready scaffolding with tests, Docker, and an evaluation harness to measure extraction accuracy. Thank you!”

Appendix: Expected JSON snippets (abbreviated)
- Flashcards result: {"cards": [{"front": "Q1", "back": "A1"}, ...], "format": "qa"}
- Note Maker result: {"notes": "Notes (outline)...", "sections": ["summary", "key_points"]}
- Concept Explainer result: {"explanation": "...", "examples": ["Example 1", "Example 2"], "key_points": ["definition", "intuition"], "quiz_questions": ["Q1", "Q2"]}
