from typing import Any, Dict
import sys
from pathlib import Path

# Ensure 'src' is on sys.path for imports when running tests without installation
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from src.app.services.parameter_extractor import ParameterExtractor, LLMClient, SchemaProvider
from src.app.models.schemas import NoteMakerInput


class FakeLLM(LLMClient):
    def generate_structured(self, *, tool: str, schema: Dict[str, Any], user_input: str, options: Dict[str, Any]) -> Dict[str, Any]:
        assert tool == "note_maker"
        assert "fields" in schema
        return {
            "user_info": {"user_id": "test_user"},
            "topic": user_input,
            "format": options.get("note_style", "outline"),
            "detail_level": "medium"
        }


class FakeSchemaProvider(SchemaProvider):
    def get_input_schema(self, tool: str) -> Dict[str, Any]:
        return {"title": "NoteMakerInput", "fields": ["source_text", "note_style"]}


def test_parameter_extractor_with_fake_llm():
    extractor = ParameterExtractor(FakeLLM(), FakeSchemaProvider())
    params = extractor.extract(tool="note_maker", user_input="Photosynthesis basics", options={"note_style": "outline"})
    obj = NoteMakerInput.model_validate(params)
    assert obj.format == "outline"
    assert obj.topic.startswith("Photosynthesis")
