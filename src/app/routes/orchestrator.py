from typing import Any, Dict, Literal, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..workflows.langgraph_workflow import get_orchestration_workflow


router = APIRouter()


class OrchestrateRequest(BaseModel):
    tool: Literal["note_maker", "flashcard_generator", "concept_explainer"] = Field(..., description="Target tool to orchestrate")
    user_input: str = Field(..., description="Raw user input text or concept")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional extraction/tool options")


class OrchestrateResponse(BaseModel):
    tool: str
    params: Dict[str, Any]
    result: Dict[str, Any]
    warnings: list[str] = Field(default_factory=list)


@router.post("/orchestrate", response_model=OrchestrateResponse)
def orchestrate(req: OrchestrateRequest) -> OrchestrateResponse:
    workflow = get_orchestration_workflow()
    try:
        output = workflow.invoke({
            "tool": req.tool,
            "user_input": req.user_input,
            "options": req.options or {},
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return OrchestrateResponse(
        tool=req.tool,
        params=output.get("validated_params", output.get("params", {})),
        result=output.get("result", {}),
        warnings=output.get("warnings", []),
    )
