from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="CivicHacks 2025 Unified Academic Assistant (Dummy Responses)")

# Request and response models for the unified endpoint.
class AssistantRequest(BaseModel):
    query: str
    course_material: Optional[str] = None  # This is optional

class AssistantResponse(BaseModel):
    response: str

@app.post("/assistant", response_model=AssistantResponse)
async def unified_assistant(request: AssistantRequest):
    """
    This endpoint analyzes the user's query to determine if they need a study plan or an assignment hint.
    
    System instructions:
    - If the query mentions "study plan" or similar, provide a structured study plan.
    - If the query mentions "assignment", "homework", or "hint", provide a guiding hint that encourages critical thinking.
    - The 'course_material' parameter is optional; if provided, it can be used to tailor the response (not implemented in this dummy version).
    """
    query_lower = request.query.lower()
    
    if "study plan" in query_lower or "plan" in query_lower:
        dummy_plan = (
            "Day 1: Outline your study goals.\n"
            "Day 2: Review lecture notes.\n"
            "Day 3: Read assigned materials.\n"
            "Day 4: Work on practice problems.\n"
            "Day 5: Group study session.\n"
            "Day 6: Recap and revise.\n"
            "Day 7: Take a mock test.\n"
            "Day 8: Address weak areas.\n"
            "Day 9: Final review.\n"
            "Day 10: Relax and prepare for the exam."
        )
        return AssistantResponse(response=dummy_plan)
    
    elif "assignment" in query_lower or "homework" in query_lower or "hint" in query_lower:
        dummy_hint = (
            "Consider reviewing the underlying theory and break the problem into smaller parts. "
            "Focus on understanding the concept rather than memorizing solutions."
        )
        return AssistantResponse(response=dummy_hint)
    
    else:
        return AssistantResponse(response="Please clarify if you need a study plan or an assignment hint. Your query did not specify a clear request.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
