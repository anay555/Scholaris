from __future__ import annotations
from typing import Any, Dict, Protocol


class LLMClient(Protocol):
    def generate_structured(self, *, tool: str, schema: Dict[str, Any], user_input: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Return structured parameters dict matching provided schema.
        Implementations should not return raw text; they should map fields.
        """
        ...


class ParameterExtractor:
    """LLM-driven (pluggable) parameter extractor.

    In tests or local runs without a real LLM, the extractor falls back to
    heuristic defaults if the provided LLM client is a stub.
    """

    def __init__(self, llm_client: LLMClient, schema_provider: "SchemaProvider") -> None:
        self._llm = llm_client
        self._schemas = schema_provider

    def extract(self, *, tool: str, user_input: str, options: Dict[str, Any]) -> Dict[str, Any]:
        schema = self._schemas.get_input_schema(tool)
        # Allow test overrides
        if options and isinstance(options.get("__mock_params__"), dict):
            return options["__mock_params__"]
        # Ask the LLM to produce structured args
        try:
            params = self._llm.generate_structured(tool=tool, schema=schema, user_input=user_input, options=options)
            if not isinstance(params, dict):
                raise ValueError("LLM client returned non-dict params")
            return params
        except Exception:
            # Heuristic fallback: simple defaults per tool
            if tool == "note_maker":
                return {
                    "source_text": user_input,
                    "note_style": options.get("note_style", "bullet"),
                    "target_length": options.get("target_length", "medium"),
                    "language": options.get("language", "en"),
                }
            elif tool == "flashcard_generator":
                return {
                    "source_text": user_input,
                    "card_style": options.get("card_style", "qa"),
                    "num_cards": int(options.get("num_cards", 10)),
                    "difficulty": options.get("difficulty", "medium"),
                    "language": options.get("language", "en"),
                }
            elif tool == "concept_explainer":
                return {
                    "concept": user_input,
                    "prior_knowledge": options.get("prior_knowledge", "basic"),
                    "explanation_style": options.get("explanation_style", "step_by_step"),
                    "examples_count": int(options.get("examples_count", 2)),
                    "language": options.get("language", "en"),
                }
            else:
                raise


class SchemaProvider(Protocol):
    def get_input_schema(self, tool: str) -> Dict[str, Any]:
        ...
