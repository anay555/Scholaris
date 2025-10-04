"""
Intelligent workflow orchestration for Scholaris - The AI Educational Orchestrator.

This module implements a workflow-based approach to parameter extraction,
validation, tool selection, and execution for 80+ supported educational tools.
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from ..services.tool_client import ToolClient
from ..models.schemas import validate_tool_input, OrchestratorResponse

logger = logging.getLogger(__name__)


# Tool selection mapping based on keywords and patterns
TOOL_SELECTION_MAP = {
    # Content generation tools
    "notes": ["NoteMaker", "AnnotatedNotes", "CornellNotesGenerator"],
    "summary": ["SummaryCompressor", "ExpandedSummary"],
    "slides": ["SlideDeckGenerator"],
    "handout": ["HandoutCreator"],
    "study guide": ["StudyGuideAssembler"],
    "checklist": ["RevisionChecklistGenerator"],
    "transcript": ["LectureTranscriptCleaner"],
    
    # Assessment tools
    "flashcard": ["FlashcardGenerator", "FlashcardBank"],
    "quiz": ["MCQGenerator", "ShortAnswerQuizMaker", "AdaptiveQuizDesigner"],
    "test": ["ClozeTestGenerator", "UnitTestGenerator"],
    "exam": ["ExamPaperAssembler"],
    "coding": ["CodingProblemGenerator", "DebuggingExerciseMaker"],
    "grade": ["AutomaticGrader"],
    "peer review": ["PeerReviewPromptGenerator"],
    
    # Pedagogy tools
    "explain": ["ConceptExplainer"],
    "analogy": ["AnalogyMaker"],
    "solve": ["StepByStepSolver"],
    "intuition": ["IntuitionBuilder"],
    "question": ["SocraticQuestioner"],
    "error": ["ErrorDiagnosisAssistant"],
    "example": ["ExampleBankGenerator"],
    "counterexample": ["CounterexampleFinder"],
    "proof": ["ProofSketcher"],
    "history": ["HistoricalContextProvider"],
    
    # Practice tools
    "practice": ["PracticeSessionPlanner", "MixedPracticeCreator"],
    "spaced repetition": ["SpacedRepetitionScheduler"],
    "drill": ["DrillGenerator"],
    "simulation": ["SimulationTaskMaker"],
    "application": ["RealWorldApplicationFinder"],
    "reflect": ["ReflectionPromptGenerator"],
    "hint": ["AutoHintProvider"],
    "mastery": ["MasteryCheckpointCreator"],
    
    # Personalization tools
    "learning path": ["LearningPathRecommender"],
    "skill gap": ["SkillGapAnalyzer"],
    "goal": ["GoalSettingAssistant"],
    "pace": ["PaceAdjuster"],
    "tone": ["PersonaStyler"],
    "motivate": ["MotivationBooster"],
    "learning style": ["LearningStyleDetector"],
    "profile": ["ProfileSummaryExporter"],
    "schedule": ["TimeTablePlanner"],
}


def mock_llm_extractor(user_message: str, chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Mock LLM parameter extractor for demonstration.
    
    In production, this would call an actual LLM service to extract
    intent and parameters from natural language.
    
    Args:
        user_message: Current user message
        chat_history: Previous conversation messages
        
    Returns:
        Dictionary with extracted parameters and metadata
    """
    # Simple keyword-based extraction for demo purposes
    message_lower = user_message.lower()
    
    # Default extraction result
    extraction = {
        "tool_candidates": [],
        "parameters": {},
        "missing_required": [],
        "clarifying_question": None,
        "ambiguous_tools": [],
        "confidence": 0.5
    }
    
    # Basic intent detection based on keywords
    detected_tools = []
    for keyword, tools in TOOL_SELECTION_MAP.items():
        if keyword in message_lower:
            detected_tools.extend(tools)
    
    # Remove duplicates and limit candidates
    detected_tools = list(set(detected_tools))[:3]
    
    if not detected_tools:
        # Fallback to common tools
        if "help" in message_lower or "struggling" in message_lower:
            detected_tools = ["ConceptExplainer"]
        elif "learn" in message_lower:
            detected_tools = ["NoteMaker", "FlashcardGenerator"]
        else:
            detected_tools = ["ConceptExplainer"]
    
    extraction["tool_candidates"] = detected_tools
    
    # Extract basic parameters based on common patterns
    parameters = {}
    
    # Extract topic (look for quotes or after common phrases)
    if '"' in user_message:
        # Extract quoted topic
        start = user_message.find('"')
        end = user_message.find('"', start + 1)
        if start != -1 and end != -1:
            parameters["topic"] = user_message[start+1:end]
    elif " about " in message_lower:
        # Extract topic after "about"
        about_idx = message_lower.find(" about ")
        topic_start = about_idx + 7
        topic_end = min(len(user_message), topic_start + 50)
        parameters["topic"] = user_message[topic_start:topic_end].strip()
    elif " on " in message_lower:
        # Extract topic after "on"
        on_idx = message_lower.find(" on ")
        topic_start = on_idx + 4
        topic_end = min(len(user_message), topic_start + 50)
        parameters["topic"] = user_message[topic_start:topic_end].strip()
    
    # Extract difficulty level
    if "easy" in message_lower or "beginner" in message_lower:
        parameters["difficulty"] = "easy"
        parameters["level"] = "beginner"
    elif "hard" in message_lower or "advanced" in message_lower:
        parameters["difficulty"] = "hard"
        parameters["level"] = "advanced"
    elif "medium" in message_lower or "intermediate" in message_lower:
        parameters["difficulty"] = "medium"
        parameters["level"] = "intermediate"
    
    # Extract count/number
    import re
    numbers = re.findall(r'\b(\d+)\b', user_message)
    if numbers:
        count = int(numbers[0])
        parameters["count"] = min(count, 50)  # Cap at reasonable limit
        parameters["num_questions"] = min(count, 50)
        parameters["slides"] = min(count, 30)
    
    extraction["parameters"] = parameters
    
    # Check for ambiguous tools
    if len(detected_tools) > 1:
        extraction["ambiguous_tools"] = detected_tools
        extraction["clarifying_question"] = f"I can help with {', '.join(detected_tools[:3])}. Which would you prefer?"
    
    # Check for missing required fields
    if detected_tools:
        primary_tool = detected_tools[0]
        if primary_tool in ["NoteMaker", "FlashcardGenerator", "ConceptExplainer"] and not parameters.get("topic"):
            extraction["missing_required"] = ["topic"]
            extraction["clarifying_question"] = "What specific topic would you like help with?"
    
    return extraction


def parameter_extractor_node(payload: Dict[str, Any], llm_extractor: Callable) -> Dict[str, Any]:
    """
    Extract parameters from user message using LLM.
    
    Args:
        payload: Contains user_info, chat_history, current_message
        llm_extractor: Function to call for parameter extraction
        
    Returns:
        Updated payload with extracted parameters
    """
    try:
        extraction_result = llm_extractor(
            payload["current_message"], 
            payload.get("chat_history", [])
        )
        
        payload.update({
            "tool_candidates": extraction_result.get("tool_candidates", []),
            "extracted_parameters": extraction_result.get("parameters", {}),
            "missing_required": extraction_result.get("missing_required", []),
            "clarifying_question": extraction_result.get("clarifying_question"),
            "ambiguous_tools": extraction_result.get("ambiguous_tools", []),
            "extraction_confidence": extraction_result.get("confidence", 0.5)
        })
        
        logger.info(f"Extracted parameters for tools: {extraction_result.get('tool_candidates', [])}")
        
    except Exception as e:
        logger.error(f"Parameter extraction failed: {e}")
        payload.update({
            "extraction_error": str(e),
            "tool_candidates": ["ConceptExplainer"],  # Fallback
            "extracted_parameters": {},
            "missing_required": ["topic"],
            "clarifying_question": "I need more information. What topic would you like help with?"
        })
    
    return payload


def parameter_validator_node(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate extracted parameters against tool schemas.
    
    Args:
        payload: Contains tool candidates and extracted parameters
        
    Returns:
        Updated payload with validation results
    """
    tool_candidates = payload.get("tool_candidates", [])
    extracted_params = payload.get("extracted_parameters", {})
    user_info = payload.get("user_info", {})
    
    validation_results = {}
    selected_tool = None
    
    # Try to validate parameters against each candidate tool
    for tool_name in tool_candidates:
        # Merge user_info with extracted parameters
        full_params = {**extracted_params}
        if user_info:
            full_params["user_info"] = user_info
            
        validated_obj, errors = validate_tool_input(tool_name, full_params)
        
        validation_results[tool_name] = {
            "validated": validated_obj is not None,
            "errors": errors,
            "validated_obj": validated_obj
        }
        
        # Select first tool that validates successfully
        if validated_obj is not None and selected_tool is None:
            selected_tool = tool_name
            payload["validated_parameters"] = full_params
            payload["validated_object"] = validated_obj
    
    payload.update({
        "validation_results": validation_results,
        "selected_tool": selected_tool,
        "validation_success": selected_tool is not None
    })
    
    # Check if we still have missing required fields
    if not selected_tool:
        missing_fields = set()
        for tool_name, result in validation_results.items():
            if result["errors"]:
                for field, messages in result["errors"].items():
                    if field != "meta" and "required" in str(messages).lower():
                        missing_fields.add(field)
        
        payload["missing_required"] = list(missing_fields)
        if missing_fields and not payload.get("clarifying_question"):
            payload["clarifying_question"] = f"I need more information about: {', '.join(missing_fields)}"
    
    logger.info(f"Validation results: selected_tool={selected_tool}, success={selected_tool is not None}")
    return payload


def tool_selector_node(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select the most appropriate tool based on validation results and context.
    
    Args:
        payload: Contains validation results and tool candidates
        
    Returns:
        Updated payload with final tool selection
    """
    # If validation already selected a tool, use it
    if payload.get("selected_tool") and payload.get("validation_success"):
        logger.info(f"Tool already selected by validator: {payload['selected_tool']}")
        return payload
    
    # Otherwise, apply additional selection logic
    tool_candidates = payload.get("tool_candidates", [])
    user_message = payload.get("current_message", "").lower()
    
    # Priority-based selection
    if tool_candidates:
        # Prefer tools based on user intent signals
        if "explain" in user_message or "understand" in user_message:
            for tool in ["ConceptExplainer", "IntuitionBuilder", "AnalogyMaker"]:
                if tool in tool_candidates:
                    payload["selected_tool"] = tool
                    break
        
        elif "practice" in user_message or "exercise" in user_message:
            for tool in ["PracticeSessionPlanner", "DrillGenerator", "FlashcardGenerator"]:
                if tool in tool_candidates:
                    payload["selected_tool"] = tool
                    break
        
        elif "notes" in user_message:
            for tool in ["NoteMaker", "CornellNotesGenerator", "AnnotatedNotes"]:
                if tool in tool_candidates:
                    payload["selected_tool"] = tool
                    break
        
        # Default to first candidate
        if not payload.get("selected_tool"):
            payload["selected_tool"] = tool_candidates[0]
    
    else:
        # Fallback selection
        payload["selected_tool"] = "ConceptExplainer"
        payload["tool_candidates"] = ["ConceptExplainer"]
    
    logger.info(f"Final tool selection: {payload.get('selected_tool')}")
    return payload


def tool_caller_node(payload: Dict[str, Any], tool_client: ToolClient) -> Dict[str, Any]:
    """
    Call the selected tool with validated parameters.
    
    Args:
        payload: Contains selected tool and validated parameters
        tool_client: ToolClient instance for making tool calls
        
    Returns:
        Updated payload with tool response
    """
    selected_tool = payload.get("selected_tool")
    validated_params = payload.get("validated_parameters", {})
    
    if not selected_tool:
        payload["tool_error"] = "No tool selected"
        return payload
    
    try:
        # Call the tool
        response = tool_client.call_tool(selected_tool, validated_params)
        
        payload.update({
            "tool_response": response,
            "tool_success": response.get("status") == "ok",
            "tool_data": response.get("data"),
            "tool_meta": response.get("meta", {})
        })
        
        if response.get("status") != "ok":
            payload["tool_error"] = response.get("error", "Tool call failed")
            
        logger.info(f"Tool call completed: {selected_tool}, status={response.get('status')}")
        
    except Exception as e:
        logger.error(f"Tool call error: {e}")
        payload.update({
            "tool_error": str(e),
            "tool_success": False
        })
    
    return payload


def response_formatter_node(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the final orchestrator response.
    
    Args:
        payload: Contains all workflow results
        
    Returns:
        Final orchestrator response
    """
    # Check for early termination conditions
    if payload.get("missing_required") and not payload.get("tool_success"):
        return {
            "status": "ok",
            "data": None,
            "clarifying_question": payload.get("clarifying_question", "I need more information to help you."),
            "ambiguous_tools": payload.get("ambiguous_tools", []),
            "meta": {
                "stage": "parameter_validation",
                "missing_required": payload.get("missing_required", []),
                "extraction_confidence": payload.get("extraction_confidence", 0.0)
            }
        }
    
    if payload.get("ambiguous_tools") and len(payload.get("ambiguous_tools", [])) > 1:
        return {
            "status": "ok", 
            "data": None,
            "clarifying_question": payload.get("clarifying_question", "Which tool would you prefer?"),
            "ambiguous_tools": payload.get("ambiguous_tools", []),
            "meta": {
                "stage": "tool_selection",
                "candidates": payload.get("ambiguous_tools", [])
            }
        }
    
    # Handle tool call results
    if payload.get("tool_success"):
        return {
            "status": "ok",
            "data": payload.get("tool_data"),
            "meta": {
                "tool": payload.get("selected_tool"),
                "duration_s": payload.get("tool_meta", {}).get("duration_s", 0),
                "endpoint": payload.get("tool_meta", {}).get("endpoint"),
                "stage": "completed"
            }
        }
    
    else:
        # Handle errors
        error_msg = payload.get("tool_error", payload.get("extraction_error", "An error occurred"))
        return {
            "status": "error",
            "data": None,
            "error": error_msg,
            "meta": {
                "stage": "error",
                "selected_tool": payload.get("selected_tool"),
                "error_details": {
                    "tool_error": payload.get("tool_error"),
                    "extraction_error": payload.get("extraction_error"),
                    "validation_results": payload.get("validation_results", {})
                }
            }
        }


def run_workflow(
    payload: Dict[str, Any], 
    tool_client: ToolClient, 
    llm_extractor: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Execute the complete orchestrator workflow.
    
    Args:
        payload: Input containing user_info, chat_history, current_message
        tool_client: ToolClient instance for tool calls
        llm_extractor: Optional LLM extractor function (defaults to mock)
        
    Returns:
        Final orchestrator response dictionary
    """
    if llm_extractor is None:
        llm_extractor = mock_llm_extractor
    
    logger.info(f"Starting workflow for message: {payload.get('current_message', '')[:100]}...")
    
    try:
        # Execute workflow nodes in sequence
        payload = parameter_extractor_node(payload, llm_extractor)
        payload = parameter_validator_node(payload)
        payload = tool_selector_node(payload)
        payload = tool_caller_node(payload, tool_client)
        response = response_formatter_node(payload)
        
        logger.info(f"Workflow completed with status: {response.get('status')}")
        return response
        
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        return {
            "status": "error",
            "data": None,
            "error": f"Workflow execution failed: {str(e)}",
            "meta": {
                "stage": "workflow_error",
                "error_type": type(e).__name__
            }
        }


# Legacy compatibility function
def get_orchestration_workflow():
    """Legacy function for backward compatibility."""
    from ..services.tool_client import default_tool_client
    
    def workflow_wrapper(state):
        payload = {
            "user_info": state.get("user_info", {}),
            "chat_history": state.get("chat_history", []),
            "current_message": state.get("user_input", state.get("current_message", ""))
        }
        return run_workflow(payload, default_tool_client)
    
    return workflow_wrapper
