"""
Integration tests for multi-tool orchestration.

Tests end-to-end workflow execution for 5 key tools:
- NoteMaker
- FlashcardGenerator  
- StepByStepSolver
- SlideDeckGenerator
- SpacedRepetitionScheduler

All tests run offline with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch
from src.app.workflows.langgraph_workflow import run_workflow, mock_llm_extractor
from src.app.services.tool_client import ToolClient, create_default_tool_client
from src.app.models.schemas import UserInfo


class TestOrchestrationMultiTools:
    """Integration tests for orchestrating multiple AI tutor tools."""
    
    @pytest.fixture
    def sample_user_info(self):
        """Sample user info for testing."""
        return {
            "user_id": "test_user_123",
            "name": "Test Student",
            "preferences": {"language": "en", "difficulty": "medium"},
            "mastery_levels": {"python": 0.7, "math": 0.6, "biology": 0.5}
        }
    
    @pytest.fixture 
    def tool_client(self):
        """Mock tool client with registered tools."""
        client = create_default_tool_client()
        return client
    
    @pytest.fixture
    def mock_extractor(self):
        """Mock LLM extractor for predictable parameter extraction."""
        def extractor_func(user_message: str, chat_history):
            # Return different extractions based on message content
            message_lower = user_message.lower()
            
            if "notes" in message_lower and "python" in message_lower:
                return {
                    "tool_candidates": ["NoteMaker"],
                    "parameters": {
                        "topic": "Python Programming",
                        "format": "outline",
                        "detail_level": "medium"
                    },
                    "missing_required": [],
                    "clarifying_question": None,
                    "ambiguous_tools": [],
                    "confidence": 0.9
                }
            elif "flashcards" in message_lower and "machine learning" in message_lower:
                return {
                    "tool_candidates": ["FlashcardGenerator"],
                    "parameters": {
                        "topic": "Machine Learning",
                        "count": 8,
                        "difficulty": "medium"
                    },
                    "missing_required": [],
                    "clarifying_question": None,
                    "ambiguous_tools": [],
                    "confidence": 0.9
                }
            elif "solve" in message_lower and "derivative" in message_lower:
                return {
                    "tool_candidates": ["StepByStepSolver"],
                    "parameters": {
                        "problem_statement": "Find the derivative of f(x) = x^2 + 3x + 2",
                        "show_checks": True
                    },
                    "missing_required": [],
                    "clarifying_question": None,
                    "ambiguous_tools": [],
                    "confidence": 0.95
                }
            elif "slides" in message_lower and "data structures" in message_lower:
                return {
                    "tool_candidates": ["SlideDeckGenerator"],
                    "parameters": {
                        "topic": "Data Structures",
                        "slides": 10
                    },
                    "missing_required": [],
                    "clarifying_question": None,
                    "ambiguous_tools": [],
                    "confidence": 0.9
                }
            elif "schedule" in message_lower and "review" in message_lower:
                return {
                    "tool_candidates": ["SpacedRepetitionScheduler"],
                    "parameters": {
                        "flashcard_ids": ["card1", "card2", "card3"],
                        "algorithm": "sm2"
                    },
                    "missing_required": [],
                    "clarifying_question": None,
                    "ambiguous_tools": [],
                    "confidence": 0.8
                }
            else:
                # Default fallback
                return {
                    "tool_candidates": ["ConceptExplainer"],
                    "parameters": {"topic": "General Topic"},
                    "missing_required": ["topic"],
                    "clarifying_question": "What specific topic would you like help with?",
                    "ambiguous_tools": [],
                    "confidence": 0.5
                }
        
        return extractor_func
    
    def test_notemaker_orchestration(self, sample_user_info, tool_client, mock_extractor):
        """Test end-to-end orchestration for NoteMaker tool."""
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "I need notes on Python Programming in outline format"
        }
        
        response = run_workflow(payload, tool_client, mock_extractor)
        
        # Verify successful orchestration
        assert response["status"] == "ok"
        assert response["data"] is not None
        assert response["meta"]["tool"] == "NoteMaker"
        assert response["meta"]["stage"] == "completed"
        assert "duration_s" in response["meta"]
        
        # Verify mock response structure
        data = response["data"]
        assert "notes" in data
        assert data["notes"]["title"] == "Notes on Python Programming"
        assert "outline" in data["notes"]["content"]
        assert data["tool"] == "NoteMaker"
    
    def test_flashcard_generator_orchestration(self, sample_user_info, tool_client, mock_extractor):
        """Test end-to-end orchestration for FlashcardGenerator tool."""
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "Create 8 flashcards about Machine Learning"
        }
        
        response = run_workflow(payload, tool_client, mock_extractor)
        
        # Verify successful orchestration
        assert response["status"] == "ok"
        assert response["data"] is not None
        assert response["meta"]["tool"] == "FlashcardGenerator"
        assert response["meta"]["stage"] == "completed"
        
        # Verify flashcard response structure
        data = response["data"]
        assert "flashcards" in data
        assert len(data["flashcards"]) == 8
        assert data["tool"] == "FlashcardGenerator"
        
        # Check individual flashcard structure
        for i, card in enumerate(data["flashcards"]):
            assert "front" in card
            assert "back" in card
            assert "difficulty" in card
            assert f"Mock Question {i+1} about Machine Learning" == card["front"]
            assert card["difficulty"] == "medium"
    
    def test_step_by_step_solver_orchestration(self, sample_user_info, tool_client, mock_extractor):
        """Test end-to-end orchestration for StepByStepSolver tool."""
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "Help me solve this derivative problem step by step"
        }
        
        response = run_workflow(payload, tool_client, mock_extractor)
        
        # Verify successful orchestration
        assert response["status"] == "ok"
        assert response["data"] is not None
        assert response["meta"]["tool"] == "StepByStepSolver"
        assert response["meta"]["stage"] == "completed"
        
        # Verify solution steps structure
        data = response["data"]
        assert "solution_steps" in data
        assert len(data["solution_steps"]) == 3
        assert data["tool"] == "StepByStepSolver"
        
        # Check step structure
        steps = data["solution_steps"]
        assert steps[0]["step"] == 1
        assert steps[0]["description"] == "Analyze the problem"
        assert steps[0]["result"] == "Problem understood"
        assert steps[1]["step"] == 2
        assert steps[2]["step"] == 3
    
    def test_slide_deck_generator_orchestration(self, sample_user_info, tool_client, mock_extractor):
        """Test end-to-end orchestration for SlideDeckGenerator tool."""
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "Generate 10 slides about Data Structures"
        }
        
        response = run_workflow(payload, tool_client, mock_extractor)
        
        # Verify successful orchestration
        assert response["status"] == "ok"
        assert response["data"] is not None
        assert response["meta"]["tool"] == "SlideDeckGenerator"
        assert response["meta"]["stage"] == "completed"
        
        # Verify slide deck structure
        data = response["data"]
        assert "slides" in data
        assert len(data["slides"]) == 10
        assert data["tool"] == "SlideDeckGenerator"
        
        # Check individual slide structure
        for i, slide in enumerate(data["slides"]):
            assert "slide_number" in slide
            assert "title" in slide
            assert "content" in slide
            assert "speaker_notes" in slide
            assert slide["slide_number"] == i + 1
            assert "Data Structures" in slide["title"]
    
    def test_spaced_repetition_scheduler_orchestration(self, sample_user_info, tool_client, mock_extractor):
        """Test end-to-end orchestration for SpacedRepetitionScheduler tool."""
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "Schedule my flashcards for spaced review"
        }
        
        response = run_workflow(payload, tool_client, mock_extractor)
        
        # Verify successful orchestration
        assert response["status"] == "ok"
        assert response["data"] is not None
        assert response["meta"]["tool"] == "SpacedRepetitionScheduler"
        assert response["meta"]["stage"] == "completed"
        
        # Verify schedule structure
        data = response["data"]
        assert "schedule" in data
        schedule = data["schedule"]
        assert schedule["algorithm"] == "sm2"
        assert "next_reviews" in schedule
        assert len(schedule["next_reviews"]) == 3
        
        # Check that cards are scheduled for different days
        review_dates = list(schedule["next_reviews"].values())
        assert len(set(review_dates)) == 3  # All different dates
    
    def test_ambiguous_tool_handling(self, sample_user_info, tool_client):
        """Test handling of ambiguous tool selection."""
        # Use default mock extractor that detects multiple tools
        def ambiguous_extractor(user_message, chat_history):
            return {
                "tool_candidates": ["NoteMaker", "FlashcardGenerator", "ConceptExplainer"],
                "parameters": {"topic": "Python Programming"},
                "missing_required": [],
                "clarifying_question": "I can help with NoteMaker, FlashcardGenerator, ConceptExplainer. Which would you prefer?",
                "ambiguous_tools": ["NoteMaker", "FlashcardGenerator", "ConceptExplainer"],
                "confidence": 0.7
            }
        
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "Help me with Python"  # Ambiguous request
        }
        
        response = run_workflow(payload, tool_client, ambiguous_extractor)
        
        # Verify ambiguous handling
        assert response["status"] == "ok"
        assert response["data"] is None  # No tool executed
        assert "clarifying_question" in response
        assert "ambiguous_tools" in response
        assert len(response["ambiguous_tools"]) == 3
        assert response["meta"]["stage"] == "tool_selection"
    
    def test_missing_required_parameters(self, sample_user_info, tool_client):
        """Test handling of missing required parameters."""
        def incomplete_extractor(user_message, chat_history):
            return {
                "tool_candidates": ["FlashcardGenerator"],
                "parameters": {"count": 5},  # Missing required 'topic'
                "missing_required": ["topic"],
                "clarifying_question": "What topic would you like flashcards about?",
                "ambiguous_tools": [],
                "confidence": 0.6
            }
        
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "Make 5 flashcards"  # Missing topic
        }
        
        response = run_workflow(payload, tool_client, incomplete_extractor)
        
        # Verify missing parameter handling
        assert response["status"] == "ok"
        assert response["data"] is None  # No tool executed
        assert "clarifying_question" in response
        assert "topic" in response["clarifying_question"]
        assert response["meta"]["stage"] == "parameter_validation"
        assert "missing_required" in response["meta"]
        assert "topic" in response["meta"]["missing_required"]
    
    def test_tool_client_error_handling(self, sample_user_info, mock_extractor):
        """Test handling of tool client errors."""
        # Create a tool client that will fail
        failing_client = ToolClient()
        # Don't register any tools, causing failures
        
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "Create notes about Python Programming"
        }
        
        response = run_workflow(payload, failing_client, mock_extractor)
        
        # Verify error handling
        assert response["status"] == "error"
        assert response["data"] is None
        assert "error" in response
        assert "Unknown tool" in response["error"]
        assert response["meta"]["stage"] == "error"
        assert "selected_tool" in response["meta"]
    
    def test_workflow_with_chat_history(self, sample_user_info, tool_client, mock_extractor):
        """Test workflow execution with chat history context."""
        chat_history = [
            {"role": "user", "content": "Hi, I'm studying Python"},
            {"role": "assistant", "content": "Great! How can I help you with Python?"},
            {"role": "user", "content": "I need help understanding functions"}
        ]
        
        payload = {
            "user_info": sample_user_info,
            "chat_history": chat_history,
            "current_message": "Create notes on Python Programming functions"
        }
        
        response = run_workflow(payload, tool_client, mock_extractor)
        
        # Verify successful execution with context
        assert response["status"] == "ok"
        assert response["data"] is not None
        assert response["meta"]["tool"] == "NoteMaker"
        
        # Verify that the mock extractor received the chat history
        # (This would be more sophisticated in a real implementation)
        data = response["data"]
        assert "Python Programming" in data["notes"]["title"]
    
    def test_workflow_performance_metadata(self, sample_user_info, tool_client, mock_extractor):
        """Test that performance metadata is included in responses."""
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "Generate flashcards about Machine Learning"
        }
        
        response = run_workflow(payload, tool_client, mock_extractor)
        
        # Verify performance metadata
        assert response["status"] == "ok"
        assert "meta" in response
        assert "duration_s" in response["meta"]
        assert isinstance(response["meta"]["duration_s"], (int, float))
        assert response["meta"]["duration_s"] >= 0
        assert response["meta"]["duration_s"] < 10  # Should be fast for mocked calls
        
        # Check that endpoint information is included
        assert "endpoint" in response["meta"]
        assert "mock://local" in response["meta"]["endpoint"]
    
    def test_multiple_tool_candidates_selection(self, sample_user_info, tool_client):
        """Test selection from multiple valid tool candidates."""
        def multi_candidate_extractor(user_message, chat_history):
            return {
                "tool_candidates": ["ConceptExplainer", "NoteMaker"],  # Multiple valid options
                "parameters": {"topic": "Machine Learning Basics"},
                "missing_required": [],
                "clarifying_question": None,
                "ambiguous_tools": [],
                "confidence": 0.8
            }
        
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "Explain machine learning basics"
        }
        
        response = run_workflow(payload, tool_client, multi_candidate_extractor)
        
        # Verify that a tool was selected and executed
        assert response["status"] == "ok"
        assert response["data"] is not None
        assert response["meta"]["tool"] in ["ConceptExplainer", "NoteMaker"]
        assert response["meta"]["stage"] == "completed"
    
    def test_workflow_error_recovery(self, sample_user_info, tool_client):
        """Test workflow error recovery and fallback behavior."""
        def error_prone_extractor(user_message, chat_history):
            # Simulate an extractor that raises an exception
            raise Exception("Mock LLM service unavailable")
        
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": "Help me with anything"
        }
        
        # The workflow should catch the exception and provide a fallback
        response = run_workflow(payload, tool_client, error_prone_extractor)
        
        # Verify graceful error handling
        # Note: The workflow should fall back to a default tool or ask for clarification
        # depending on the implementation
        assert "status" in response
        # The specific behavior depends on implementation - could be error or fallback
    
    @pytest.mark.parametrize("tool_name,expected_fields", [
        ("NoteMaker", ["notes"]),
        ("FlashcardGenerator", ["flashcards"]),
        ("StepByStepSolver", ["solution_steps"]),
        ("SlideDeckGenerator", ["slides"]),
        ("SpacedRepetitionScheduler", ["schedule"])
    ])
    def test_tool_response_consistency(self, tool_name, expected_fields, sample_user_info, tool_client):
        """Test that each tool returns consistent response structure."""
        # Mock extractor that always selects the specified tool
        def tool_specific_extractor(user_message, chat_history):
            base_params = {"topic": "Test Topic"}
            if tool_name == "FlashcardGenerator":
                base_params.update({"count": 5, "difficulty": "easy"})
            elif tool_name == "SlideDeckGenerator":
                base_params.update({"slides": 5})
            elif tool_name == "SpacedRepetitionScheduler":
                base_params = {"flashcard_ids": ["card1"], "algorithm": "sm2"}
            elif tool_name == "StepByStepSolver":
                base_params = {"problem_statement": "Solve this test problem", "show_checks": True}
            
            return {
                "tool_candidates": [tool_name],
                "parameters": base_params,
                "missing_required": [],
                "clarifying_question": None,
                "ambiguous_tools": [],
                "confidence": 0.9
            }
        
        payload = {
            "user_info": sample_user_info,
            "chat_history": [],
            "current_message": f"Use {tool_name} for testing"
        }
        
        response = run_workflow(payload, tool_client, tool_specific_extractor)
        
        # Verify consistent response structure
        assert response["status"] == "ok"
        assert response["data"] is not None
        assert response["meta"]["tool"] == tool_name
        
        # Verify tool-specific fields are present
        data = response["data"]
        for field in expected_fields:
            assert field in data, f"Field '{field}' missing from {tool_name} response"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])