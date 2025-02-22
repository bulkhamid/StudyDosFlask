from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os

# Set your OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="CivicHacks 2025 Homework Assistant")

# Request and response models for the /hint endpoint
class HintRequest(BaseModel):
    course_material: str
    assignment_question: str

class HintResponse(BaseModel):
    hint: str

# Request and response models for the /study_plan endpoint
class StudyPlanRequest(BaseModel):
    topic: str
    start_date: str  # Expected in ISO format, e.g., "2025-03-01"
    days: int = 10   # Default to 10 days

class StudyPlanResponse(BaseModel):
    plan: str

@app.post("/hint", response_model=HintResponse)
async def get_hint(request: HintRequest):
    """
    Endpoint to generate a hint for an assignment.
    The assistant uses the provided course material and assignment question to create a hint that guides the student.
    """
    prompt = (
        f"Course Material:\n{request.course_material}\n"
        f"Assignment Question:\n{request.assignment_question}\n\n"
        "Provide a hint for solving the assignment that encourages critical thinking. Do not provide the full answer."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or substitute with another model if preferred
            messages=[
                {"role": "system", "content": "You are an academic assistant that provides hints for students' assignments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        hint = response.choices[0].message['content'].strip()
        return HintResponse(hint=hint)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/study_plan", response_model=StudyPlanResponse)
async def create_study_plan(request: StudyPlanRequest):
    """
    Endpoint to generate a study plan.
    Given a topic and a starting date, the AI returns a detailed plan covering the next 10 days.
    """
    prompt = (
        f"Generate a detailed {request.days}-day study plan for the topic: '{request.topic}'. "
        f"Start from {request.start_date} and include daily tasks and recommended preparation materials."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that creates detailed study plans for students."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        plan = response.choices[0].message['content'].strip()
        return StudyPlanResponse(plan=plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
