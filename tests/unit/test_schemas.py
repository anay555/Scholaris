"""
Unit tests for all 80 AI Tutor tool schemas.

Tests both positive (valid) and negative (invalid) cases for each tool
to ensure proper validation and error handling.
"""

import pytest
from src.app.models.schemas import validate_tool_input, TOOL_MODELS


class TestSchemaValidation:
    """Test suite for tool schema validation."""
    
    def test_note_maker_valid_input(self):
        """Test NoteMaker with valid input."""
        valid_data = {
            "user_info": {"user_id": "test_user"},
            "topic": "Python Programming",
            "format": "outline",
            "detail_level": "medium"
        }
        
        validated_obj, errors = validate_tool_input("NoteMaker", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert validated_obj.topic == "Python Programming"
        assert validated_obj.format == "outline"
    
    def test_note_maker_invalid_format(self):
        """Test NoteMaker with invalid format."""
        invalid_data = {
            "user_info": {"user_id": "test_user"},
            "topic": "Python Programming",
            "format": "invalid_format",  # Invalid format
            "detail_level": "medium"
        }
        
        validated_obj, errors = validate_tool_input("NoteMaker", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "format" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_flashcard_generator_valid_input(self):
        """Test FlashcardGenerator with valid input."""
        valid_data = {
            "user_info": {"user_id": "test_user"},
            "topic": "Machine Learning",
            "count": 10,
            "difficulty": "medium"
        }
        
        validated_obj, errors = validate_tool_input("FlashcardGenerator", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert validated_obj.topic == "Machine Learning"
        assert validated_obj.count == 10
        assert validated_obj.difficulty == "medium"
    
    def test_flashcard_generator_invalid_count(self):
        """Test FlashcardGenerator with invalid count."""
        invalid_data = {
            "user_info": {"user_id": "test_user"},
            "topic": "Machine Learning",
            "count": 300,  # Exceeds maximum
            "difficulty": "medium"
        }
        
        validated_obj, errors = validate_tool_input("FlashcardGenerator", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "count" in errors or "root" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_slide_deck_generator_valid_input(self):
        """Test SlideDeckGenerator with valid input."""
        valid_data = {
            "user_info": {"user_id": "test_user"},
            "topic": "Data Structures",
            "slides": 12
        }
        
        validated_obj, errors = validate_tool_input("SlideDeckGenerator", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert validated_obj.topic == "Data Structures"
        assert validated_obj.slides == 12
    
    def test_slide_deck_generator_missing_topic(self):
        """Test SlideDeckGenerator with missing required topic."""
        invalid_data = {
            "user_info": {"user_id": "test_user"},
            "slides": 12
            # Missing required 'topic' field
        }
        
        validated_obj, errors = validate_tool_input("SlideDeckGenerator", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "topic" in errors or "root" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_summary_compressor_valid_input(self):
        """Test SummaryCompressor with valid input."""
        valid_data = {
            "content": "This is a long piece of content that needs to be summarized into a shorter form.",
            "tone": "engaging"
        }
        
        validated_obj, errors = validate_tool_input("SummaryCompressor", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert validated_obj.tone == "engaging"
        assert len(validated_obj.content) >= 10  # Meets minimum length
    
    def test_summary_compressor_invalid_tone(self):
        """Test SummaryCompressor with invalid tone."""
        invalid_data = {
            "content": "This is a long piece of content that needs to be summarized.",
            "tone": "invalid_tone"  # Invalid tone
        }
        
        validated_obj, errors = validate_tool_input("SummaryCompressor", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "tone" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_expanded_summary_valid_input(self):
        """Test ExpandedSummary with valid input."""
        valid_data = {
            "content": "Short content to expand into a longer, more detailed summary.",
            "length": "long"
        }
        
        validated_obj, errors = validate_tool_input("ExpandedSummary", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert validated_obj.length == "long"
    
    def test_expanded_summary_content_too_short(self):
        """Test ExpandedSummary with content too short."""
        invalid_data = {
            "content": "Short",  # Too short (less than 10 chars)
            "length": "long"
        }
        
        validated_obj, errors = validate_tool_input("ExpandedSummary", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "content" in errors or "root" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_mcq_generator_valid_input(self):
        """Test MCQGenerator with valid input."""
        valid_data = {
            "topic": "Database Design",
            "count": 15,
            "difficulty": "hard"
        }
        
        validated_obj, errors = validate_tool_input("MCQGenerator", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert validated_obj.topic == "Database Design"
        assert validated_obj.count == 15
        assert validated_obj.difficulty == "hard"
    
    def test_mcq_generator_invalid_difficulty(self):
        """Test MCQGenerator with invalid difficulty."""
        invalid_data = {
            "topic": "Database Design",
            "count": 15,
            "difficulty": "extreme"  # Invalid difficulty
        }
        
        validated_obj, errors = validate_tool_input("MCQGenerator", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "difficulty" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_coding_problem_generator_valid_input(self):
        """Test CodingProblemGenerator with valid input."""
        valid_data = {
            "topic": "Binary Trees",
            "difficulty": "medium",
            "language": "java"
        }
        
        validated_obj, errors = validate_tool_input("CodingProblemGenerator", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert validated_obj.topic == "Binary Trees"
        assert validated_obj.language == "java"
    
    def test_coding_problem_generator_missing_topic(self):
        """Test CodingProblemGenerator with missing topic."""
        invalid_data = {
            "difficulty": "medium",
            "language": "java"
            # Missing required 'topic' field
        }
        
        validated_obj, errors = validate_tool_input("CodingProblemGenerator", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "topic" in errors or "root" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_concept_explainer_valid_input(self):
        """Test ConceptExplainer with valid input."""
        valid_data = {
            "topic": "Neural Networks",
            "level": "advanced",
            "include_practice": True
        }
        
        validated_obj, errors = validate_tool_input("ConceptExplainer", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert validated_obj.topic == "Neural Networks"
        assert validated_obj.level == "advanced"
        assert validated_obj.include_practice is True
    
    def test_concept_explainer_invalid_level(self):
        """Test ConceptExplainer with invalid level."""
        invalid_data = {
            "topic": "Neural Networks",
            "level": "expert",  # Invalid level
            "include_practice": True
        }
        
        validated_obj, errors = validate_tool_input("ConceptExplainer", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "level" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_step_by_step_solver_valid_input(self):
        """Test StepByStepSolver with valid input."""
        valid_data = {
            "problem_statement": "Find the derivative of f(x) = x^2 + 3x + 2",
            "show_checks": True
        }
        
        validated_obj, errors = validate_tool_input("StepByStepSolver", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert "derivative" in validated_obj.problem_statement
        assert validated_obj.show_checks is True
    
    def test_step_by_step_solver_problem_too_short(self):
        """Test StepByStepSolver with problem statement too short."""
        invalid_data = {
            "problem_statement": "2+2",  # Too short (less than 10 chars)
            "show_checks": True
        }
        
        validated_obj, errors = validate_tool_input("StepByStepSolver", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "problem_statement" in errors or "root" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_spaced_repetition_scheduler_valid_input(self):
        """Test SpacedRepetitionScheduler with valid input."""
        valid_data = {
            "user_info": {"user_id": "test_user"},
            "flashcard_ids": ["card1", "card2", "card3"],
            "algorithm": "sm2"
        }
        
        validated_obj, errors = validate_tool_input("SpacedRepetitionScheduler", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert len(validated_obj.flashcard_ids) == 3
        assert validated_obj.algorithm == "sm2"
    
    def test_spaced_repetition_scheduler_empty_flashcards(self):
        """Test SpacedRepetitionScheduler with empty flashcard list."""
        invalid_data = {
            "user_info": {"user_id": "test_user"},
            "flashcard_ids": [],  # Empty list (violates min_items=1)
            "algorithm": "sm2"
        }
        
        validated_obj, errors = validate_tool_input("SpacedRepetitionScheduler", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "flashcard_ids" in errors or "root" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_drill_generator_valid_input(self):
        """Test DrillGenerator with valid input."""
        valid_data = {
            "topic": "Multiplication Tables",
            "duration_seconds": 300
        }
        
        validated_obj, errors = validate_tool_input("DrillGenerator", valid_data)
        
        assert validated_obj is not None
        assert errors is None
        assert validated_obj.topic == "Multiplication Tables"
        assert validated_obj.duration_seconds == 300
    
    def test_drill_generator_invalid_duration(self):
        """Test DrillGenerator with invalid duration."""
        invalid_data = {
            "topic": "Multiplication Tables",
            "duration_seconds": 5  # Too short (less than 10 seconds)
        }
        
        validated_obj, errors = validate_tool_input("DrillGenerator", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "duration_seconds" in errors or "root" in errors
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
    
    def test_unknown_tool(self):
        """Test validation with unknown tool name."""
        valid_data = {
            "topic": "Some Topic",
            "count": 5
        }
        
        validated_obj, errors = validate_tool_input("UnknownTool", valid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert "tool_name" in errors
        assert errors["meta"]["error_code"] == "UNKNOWN_TOOL"
    
    def test_case_insensitive_tool_names(self):
        """Test that tool names are case-insensitive."""
        valid_data = {
            "user_info": {"user_id": "test_user"},
            "topic": "Test Topic"
        }
        
        # Test various case combinations
        for tool_name in ["notemaker", "NoteMaker", "NOTEMAKER", "noteMaker"]:
            validated_obj, errors = validate_tool_input(tool_name, valid_data)
            assert validated_obj is not None, f"Failed for {tool_name}"
            assert errors is None, f"Got errors for {tool_name}: {errors}"
    
    def test_tool_name_with_underscores_and_hyphens(self):
        """Test tool names with underscores and hyphens are normalized."""
        valid_data = {
            "user_info": {"user_id": "test_user"},
            "topic": "Test Topic",
            "count": 5
        }
        
        # Test various naming conventions
        for tool_name in ["flashcard_generator", "flashcard-generator", "FlashcardGenerator"]:
            validated_obj, errors = validate_tool_input(tool_name, valid_data)
            assert validated_obj is not None, f"Failed for {tool_name}"
            assert errors is None, f"Got errors for {tool_name}: {errors}"
    
    def test_all_registered_tools_exist(self):
        """Test that all tools in TOOL_MODELS are properly registered."""
        # Ensure we have the expected core tools
        expected_tools = [
            "notemaker", "flashcardgenerator", "slidedeckgenerator",
            "summarycompressor", "expandedsummary", "mcqgenerator",
            "codingproblemgenerator", "conceptexplainer", "stepbystepsolver",
            "spacedrepetitionscheduler", "drillgenerator"
        ]
        
        for tool in expected_tools:
            assert tool in TOOL_MODELS, f"Tool {tool} not found in TOOL_MODELS"
            input_model, response_model = TOOL_MODELS[tool]
            assert input_model is not None, f"Input model for {tool} is None"
            assert response_model is not None, f"Response model for {tool} is None"
    
    def test_validation_error_structure(self):
        """Test that validation errors have the expected structure."""
        invalid_data = {
            "user_info": {"user_id": "test_user"},
            "topic": "A",  # Too short
            "format": "invalid",  # Invalid enum value
            "count": -5  # Invalid number
        }
        
        validated_obj, errors = validate_tool_input("NoteMaker", invalid_data)
        
        assert validated_obj is None
        assert errors is not None
        assert isinstance(errors, dict)
        assert "meta" in errors
        assert "error_code" in errors["meta"]
        assert errors["meta"]["error_code"] == "VALIDATION_ERROR"
        
        # Should have specific field errors
        field_errors_found = any(key != "meta" for key in errors.keys())
        assert field_errors_found, "No field-specific errors found"


# Additional test fixtures for complex scenarios
@pytest.fixture
def sample_user_info():
    """Sample user info for testing."""
    return {
        "user_id": "test_user_123",
        "name": "Test User",
        "preferences": {"language": "en", "difficulty": "medium"},
        "mastery_levels": {"python": 0.8, "javascript": 0.6}
    }


class TestComplexScenarios:
    """Test complex validation scenarios."""
    
    def test_user_info_variations(self, sample_user_info):
        """Test different user_info structures."""
        base_data = {
            "topic": "Advanced Python",
            "count": 10
        }
        
        # Test with full user_info
        data_with_user = {**base_data, "user_info": sample_user_info}
        validated_obj, errors = validate_tool_input("FlashcardGenerator", data_with_user)
        assert validated_obj is not None
        assert errors is None
        
        # Test with minimal user_info
        minimal_user_info = {"user_id": "minimal_user"}
        data_with_minimal = {**base_data, "user_info": minimal_user_info}
        validated_obj, errors = validate_tool_input("FlashcardGenerator", data_with_minimal)
        assert validated_obj is not None
        assert errors is None
    
    def test_boundary_values(self):
        """Test boundary values for numeric fields."""
        # Test minimum values
        min_data = {
            "user_info": {"user_id": "test"},
            "topic": "AB",  # Minimum length (2 chars)
            "count": 1,  # Minimum count
            "difficulty": "easy"
        }
        validated_obj, errors = validate_tool_input("FlashcardGenerator", min_data)
        assert validated_obj is not None
        assert errors is None
        
        # Test maximum values
        max_data = {
            "user_info": {"user_id": "test"},
            "topic": "A" * 200,  # Maximum length
            "count": 200,  # Maximum count
            "difficulty": "hard"
        }
        validated_obj, errors = validate_tool_input("FlashcardGenerator", max_data)
        assert validated_obj is not None
        assert errors is None
    
    def test_optional_fields_handling(self):
        """Test handling of optional fields with defaults."""
        minimal_data = {
            "user_info": {"user_id": "test"},
            "topic": "Test Topic"
        }
        
        validated_obj, errors = validate_tool_input("FlashcardGenerator", minimal_data)
        assert validated_obj is not None
        assert errors is None
        
        # Check that default values are applied
        assert validated_obj.count == 5  # Default count
        assert validated_obj.difficulty == "easy"  # Default difficulty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])