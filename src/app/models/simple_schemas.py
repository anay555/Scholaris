"""
Simplified Pydantic schemas for testing the 80-tool AI Tutor Orchestrator.
"""

from typing import Optional, Dict, List, Any, Tuple
from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    name: Optional[str] = Field(None, description="User's name")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")
    mastery_levels: Optional[Dict[str, float]] = Field(default_factory=dict, description="Topic mastery levels (0-1)")


class OrchestratorRequest(BaseModel):
    user_info: UserInfo = Field(..., description="Information about the user")
    chat_history: List[Dict[str, str]] = Field(default_factory=list, description="Previous conversation messages")
    current_message: str = Field(..., min_length=1, max_length=2000, description="User's current message")


class OrchestratorResponse(BaseModel):
    status: str = Field(..., description="Response status: 'ok' or 'error'")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    clarifying_question: Optional[str] = Field(None, description="Question to ask user for clarification")
    ambiguous_tools: Optional[List[str]] = Field(None, description="List of potential matching tools")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseToolInput(BaseModel):
    """Base class for all tool inputs with common validation."""
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True


class BaseToolResponse(BaseModel):
    """Standard response format for all tools."""
    status: str = Field(..., description="Response status: 'ok' or 'error'")
    data: Optional[Dict[str, Any]] = Field(None, description="Tool-specific response data")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the response")


# Simplified tool schemas without complex validation
class NoteMakerInput(BaseToolInput):
    """Input for creating structured lecture notes."""
    user_info: Dict[str, Any] = Field(..., description="User profile and preferences")
    topic: str = Field(..., min_length=2, max_length=200, description="Topic for note creation")
    format: str = Field("outline", description="Note format: outline, bullets, paragraph")
    detail_level: str = Field("medium", description="Detail level: short, medium, long")


class NoteMakerResponse(BaseToolResponse):
    """Response from NoteMaker tool."""
    pass


class FlashcardGeneratorInput(BaseToolInput):
    """Input for generating Q/A flashcards."""
    user_info: Dict[str, Any] = Field(..., description="User profile and preferences")
    topic: str = Field(..., min_length=2, max_length=200, description="Topic for flashcard creation")
    count: int = Field(5, ge=1, le=200, description="Number of flashcards to generate")
    difficulty: str = Field("easy", description="Difficulty level: easy, medium, hard")


class FlashcardGeneratorResponse(BaseToolResponse):
    """Response from FlashcardGenerator tool."""
    pass


class StepByStepSolverInput(BaseToolInput):
    """Input for step-by-step problem solving."""
    problem_statement: str = Field(..., min_length=10, max_length=5000, description="Problem to solve")
    show_checks: bool = Field(True, description="Show intermediate checks")


class StepByStepSolverResponse(BaseToolResponse):
    """Response from StepByStepSolver tool."""
    pass


class SlideDeckGeneratorInput(BaseToolInput):
    """Input for generating lecture slides."""
    user_info: Dict[str, Any] = Field(..., description="User profile and preferences")
    topic: str = Field(..., min_length=2, max_length=200, description="Topic for slide generation")
    slides: int = Field(6, ge=1, le=60, description="Number of slides to generate")


class SlideDeckGeneratorResponse(BaseToolResponse):
    """Response from SlideDeckGenerator tool."""
    pass


class SpacedRepetitionSchedulerInput(BaseToolInput):
    """Input for spaced repetition scheduling."""
    user_info: Dict[str, Any] = Field(..., description="User profile and preferences")
    flashcard_ids: List[str] = Field(..., min_length=1, description="Flashcard IDs to schedule")
    algorithm: str = Field("sm2", description="Scheduling algorithm: sm2, leitner")


class SpacedRepetitionSchedulerResponse(BaseToolResponse):
    """Response from SpacedRepetitionScheduler tool."""
    pass


# Tool registry mapping for validation (simplified for key tools)
TOOL_MODELS = {
    "notemaker": (NoteMakerInput, NoteMakerResponse),
    "flashcardgenerator": (FlashcardGeneratorInput, FlashcardGeneratorResponse),
    "slidedeckgenerator": (SlideDeckGeneratorInput, SlideDeckGeneratorResponse),
    "stepbystepsolver": (StepByStepSolverInput, StepByStepSolverResponse),
    "spacedrepetitionscheduler": (SpacedRepetitionSchedulerInput, SpacedRepetitionSchedulerResponse),
}


def validate_tool_input(tool_name: str, data: dict) -> Tuple[Optional[BaseModel], Optional[dict]]:
    """
    Validates input data for a specific tool.
    
    Args:
        tool_name: Name of the tool (case-insensitive)
        data: Input data dictionary to validate
        
    Returns:
        Tuple of (validated_model_instance, errors_dict)
        - On success: (model_instance, None)
        - On failure: (None, {"field": ["error messages"], "meta": {"error_code": "..."}})
    """
    normalized_name = tool_name.lower().replace("_", "").replace("-", "")
    
    if normalized_name not in TOOL_MODELS:
        return None, {
            "tool_name": [f"Unknown tool: {tool_name}"],
            "meta": {"error_code": "UNKNOWN_TOOL"}
        }
    
    input_model, _ = TOOL_MODELS[normalized_name]
    
    try:
        validated_instance = input_model(**data)
        return validated_instance, None
    except Exception as e:
        # Convert Pydantic validation errors to structured format
        errors = {"meta": {"error_code": "VALIDATION_ERROR"}}
        
        if hasattr(e, 'errors'):
            for error in e.errors():
                field = '.'.join(str(x) for x in error['loc']) if error.get('loc') else 'root'
                if field not in errors:
                    errors[field] = []
                errors[field].append(error['msg'])
        else:
            errors['root'] = [str(e)]
            
        return None, errors