from __future__ import annotations
from typing import Any, Dict, Tuple, Type
from pydantic import BaseModel, ValidationError

from ..models.schemas import (
    NoteMakerInput,
    FlashcardGeneratorInput,
    ConceptExplainerInput,
)


TOOL_INPUT_MODELS: Dict[str, Type[BaseModel]] = {
    "note_maker": NoteMakerInput,
    "flashcard_generator": FlashcardGeneratorInput,
    "concept_explainer": ConceptExplainerInput,
}


class ValidatorService:
    def __init__(self) -> None:
        pass

    def validate(self, tool: str, params: Dict[str, Any]) -> Tuple[Dict[str, Any], list[str]]:
        model = TOOL_INPUT_MODELS.get(tool)
        if not model:
            raise ValueError(f"Unknown tool: {tool}")
        warnings: list[str] = []
        try:
            obj = model.model_validate(params)
        except ValidationError as e:
            # Attempt a soft-coercion retry by constructing with from_attributes
            raise ValueError(f"Parameter validation failed: {e}")
        # Return model as dict ensuring field aliases and exclude None
        data = obj.model_dump(exclude_none=True)
        return data, warnings
