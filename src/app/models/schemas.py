"""
Pydantic schemas for Scholaris - The AI Educational Orchestrator.

This module contains strict input/output models for 80+ supported educational tools
with comprehensive validation, constraints, and error handling.
"""

from typing import Optional, Dict, List, Any, Union, Tuple, Literal
from pydantic import BaseModel, Field, field_validator
from pydantic.types import constr, conint, confloat
from enum import Enum
import re


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


# ===== CONTENT CATEGORY TOOLS =====

class NoteMakerInput(BaseToolInput):
    """Input for creating structured lecture notes."""
    user_info: Dict[str, Any] = Field(..., description="User profile and preferences")
    topic: str = Field(..., description="Topic for note creation", min_length=2, max_length=200)
    format: str = Field("outline", description="Note format: outline, bullets, paragraph")
    detail_level: str = Field("medium", description="Detail level: short, medium, long")
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        if v not in ['outline', 'bullets', 'paragraph']:
            raise ValueError('Format must be outline, bullets, or paragraph')
        return v
    
    @field_validator('detail_level')
    @classmethod
    def validate_detail_level(cls, v):
        if v not in ['short', 'medium', 'long']:
            raise ValueError('Detail level must be short, medium, or long')
        return v


class NoteMakerResponse(BaseToolResponse):
    pass


class FlashcardGeneratorInput(BaseToolInput):
    """Input for generating Q/A flashcards."""
    user_info: Dict[str, Any] = Field(..., description="User profile and preferences")
    topic: constr(min_length=2, max_length=200) = Field(..., description="Topic for flashcard creation")
    count: conint(ge=1, le=200) = Field(5, description="Number of flashcards to generate")
    difficulty: str = Field("easy", description="Difficulty level: easy, medium, hard")
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v not in ['easy', 'medium', 'hard']:
            raise ValueError('Difficulty must be easy, medium, or hard')
        return v


class FlashcardGeneratorResponse(BaseToolResponse):
    pass


class SlideDeckGeneratorInput(BaseToolInput):
    """Input for generating lecture slides."""
    user_info: Dict[str, Any] = Field(..., description="User profile and preferences")
    topic: constr(min_length=2, max_length=200) = Field(..., description="Topic for slide generation")
    slides: conint(ge=1, le=60) = Field(6, description="Number of slides to generate")


class SlideDeckGeneratorResponse(BaseToolResponse):
    pass


class SummaryCompressorInput(BaseToolInput):
    """Input for ultra-short summaries."""
    content: constr(min_length=10, max_length=20000) = Field(..., description="Content to summarize")
    tone: str = Field("neutral", description="Summary tone: neutral, engaging, formal")
    
    @field_validator('tone')
    @classmethod
    def validate_tone(cls, v):
        if v not in ['neutral', 'engaging', 'formal']:
            raise ValueError('Tone must be neutral, engaging, or formal')
        return v


class SummaryCompressorResponse(BaseToolResponse):
    pass


class ExpandedSummaryInput(BaseToolInput):
    """Input for long-form summaries."""
    content: constr(min_length=10, max_length=40000) = Field(..., description="Content to summarize")
    length: str = Field("long", description="Summary length: short, medium, long")
    
    @field_validator('length')
    @classmethod
    def validate_length(cls, v):
        if v not in ['short', 'medium', 'long']:
            raise ValueError('Length must be short, medium, or long')
        return v


class ExpandedSummaryResponse(BaseToolResponse):
    pass


# ===== ASSESSMENT CATEGORY TOOLS =====

class MCQGeneratorInput(BaseToolInput):
    """Input for multiple choice questions."""
    topic: constr(min_length=2, max_length=200) = Field(..., description="Topic for MCQ generation")
    count: conint(ge=1, le=200) = Field(10, description="Number of questions to generate")
    difficulty: str = Field("medium", description="Difficulty level: easy, medium, hard")
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v not in ['easy', 'medium', 'hard']:
            raise ValueError('Difficulty must be easy, medium, or hard')
        return v


class MCQGeneratorResponse(BaseToolResponse):
    pass


class CodingProblemGeneratorInput(BaseToolInput):
    """Input for coding problems."""
    topic: constr(min_length=2, max_length=200) = Field(..., description="Topic for coding problem")
    difficulty: str = Field("medium", description="Difficulty level: easy, medium, hard")
    language: str = Field("python", description="Programming language")
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v not in ['easy', 'medium', 'hard']:
            raise ValueError('Difficulty must be easy, medium, or hard')
        return v


class CodingProblemGeneratorResponse(BaseToolResponse):
    pass


# ===== PEDAGOGY CATEGORY TOOLS =====

class ConceptExplainerInput(BaseToolInput):
    """Input for concept explanations."""
    topic: constr(min_length=2, max_length=200) = Field(..., description="Concept to explain")
    level: str = Field("intermediate", description="Explanation level: beginner, intermediate, advanced")
    include_practice: bool = Field(False, description="Include practice exercises")
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        if v not in ['beginner', 'intermediate', 'advanced']:
            raise ValueError('Level must be beginner, intermediate, or advanced')
        return v


class ConceptExplainerResponse(BaseToolResponse):
    pass


class StepByStepSolverInput(BaseToolInput):
    """Input for step-by-step problem solving."""
    problem_statement: constr(min_length=10, max_length=5000) = Field(..., description="Problem to solve")
    show_checks: bool = Field(True, description="Show intermediate checks")


class StepByStepSolverResponse(BaseToolResponse):
    pass


# ===== PRACTICE CATEGORY TOOLS =====

class SpacedRepetitionSchedulerInput(BaseToolInput):
    """Input for spaced repetition scheduling."""
    user_info: Dict[str, Any] = Field(..., description="User profile and preferences")
    flashcard_ids: List[str] = Field(..., min_length=1, description="Flashcard IDs to schedule")
    algorithm: str = Field("sm2", description="Scheduling algorithm: sm2, leitner")
    
    @field_validator('algorithm')
    @classmethod
    def validate_algorithm(cls, v):
        if v not in ['sm2', 'leitner']:
            raise ValueError('Algorithm must be sm2 or leitner')
        return v


class SpacedRepetitionSchedulerResponse(BaseToolResponse):
    pass


class DrillGeneratorInput(BaseToolInput):
    """Input for drill generation."""
    topic: constr(min_length=2, max_length=200) = Field(..., description="Drill topic")
    duration_seconds: conint(ge=10, le=3600) = Field(60, description="Drill duration")


class DrillGeneratorResponse(BaseToolResponse):
    pass


# Abbreviated implementation showing pattern for all 80 tools
# In production, all tools would have full Input/Response classes

# Tool registry mapping for validation
TOOL_MODELS = {
    "notemaker": (NoteMakerInput, NoteMakerResponse),
    "flashcardgenerator": (FlashcardGeneratorInput, FlashcardGeneratorResponse),
    "slidedeckgenerator": (SlideDeckGeneratorInput, SlideDeckGeneratorResponse),
    "summarycompressor": (SummaryCompressorInput, SummaryCompressorResponse),
    "expandedsummary": (ExpandedSummaryInput, ExpandedSummaryResponse),
    "mcqgenerator": (MCQGeneratorInput, MCQGeneratorResponse),
    "codingproblemgenerator": (CodingProblemGeneratorInput, CodingProblemGeneratorResponse),
    "conceptexplainer": (ConceptExplainerInput, ConceptExplainerResponse),
    "stepbystepsolver": (StepByStepSolverInput, StepByStepSolverResponse),
    "spacedrepetitionscheduler": (SpacedRepetitionSchedulerInput, SpacedRepetitionSchedulerResponse),
    "drillgenerator": (DrillGeneratorInput, DrillGeneratorResponse),
    # Note: In production implementation, all 80 tools would be mapped here
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


# Legacy compatibility function
def get_input_schema_dict(tool: str) -> dict:
    """Legacy function for backward compatibility."""
    normalized_name = tool.lower().replace("_", "").replace("-", "")
    if normalized_name not in TOOL_MODELS:
        raise ValueError(f"Unknown tool: {tool}")
    
    model, _ = TOOL_MODELS[normalized_name]
    return {
        "title": model.__name__,
        "fields": [
            {"name": f, "annotation": str(t), "required": getattr(t, 'required', True)}
            for f, t in model.__fields__.items()
        ],
    }
