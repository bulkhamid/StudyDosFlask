from dotenv import load_dotenv
load_dotenv()  # Load variables from .env file

import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import openai
from openai import AsyncOpenAI

# Initialize an asynchronous OpenAI client with your API key.
aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="CivicHacks 2025 Unified Assistant with Multi-Modal Features")

# Models for text-based requests
class AssistantRequest(BaseModel):
    query: str
    course_material: Optional[str] = None  # Optional parameter

class AssistantResponse(BaseModel):
    response: str

# Simulated database retrieval for default course material.
def get_course_material_from_db() -> str:
    return "Default course material from our database."

# Async helper for chat-style completions (study plans & assignment hints)
async def generate_openai_chat_response(
    system_message: str,
    user_message: str,
    max_tokens: int = 150,
    model: str = "gpt-3.5-turbo"
) -> str:
    try:
        response = await aclient.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )
        # Access the message content using attribute notation.
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

# Async helper for code completion using the chat completions endpoint.
# Note: This helper is designed to provide hints rather than complete answers
# so that users engage in critical thinking rather than simply copying code.
async def generate_code_completion(prompt: str, max_tokens: int = 100, model: str = "o1-mini") -> str:
    try:
        response = await aclient.chat.completions.create(
            model=model,
            messages=[
                # We only send a user message; for this model, system messages are not supported.
                {"role": "user", "content": prompt}
            ],
            temperature=1,  # o1-mini supports only the default temperature of 1.
            max_completion_tokens=max_tokens
        )
        result = response.choices[0].message.content.strip()
        # If the response is empty, return a hint message.
        if not result:
            result = "Hint: Review the key steps required to complete this function."
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Code Completion API error: {str(e)}")

@app.post("/assistant", response_model=AssistantResponse)
async def unified_assistant(request: AssistantRequest):
    """
    Unified endpoint that routes requests based on query content.
    
    Recognized intents:
      - Code completion: If the query mentions "code completion" or "complete code",
        the assistant will provide a code snippet hint.
      - Study plan: If the query mentions "study plan" or "plan", it returns a 10-day study plan.
      - Assignment hint: If the query mentions "assignment", "homework", or "hint",
        it provides guiding hints without giving full answers.
    
    The assistant is designed to help students by nudging them in the right direction,
    encouraging critical thinking and independent learning.
    """
    query_lower = request.query.lower()
    # Use provided course_material or fallback to default material.
    course_material = request.course_material if request.course_material else get_course_material_from_db()

    if "code completion" in query_lower or "complete code" in query_lower:
        # Create a prompt that instructs the model to provide a hint for code completion.
        prompt = (
            f"You are a helpful code completion assistant. "
            f"Complete the following code snippet by giving hints and guiding the approach, "
            f"but do not provide the complete solution:\n\n"
            f"{request.query}\n"
            f"Context: {course_material}"
        )
        completed_code = await generate_code_completion(prompt, max_tokens=150, model="o1-mini")
        return AssistantResponse(response=completed_code)

    elif "study plan" in query_lower or "plan" in query_lower:
        user_message = (
            f"Generate a detailed 10-day study plan for the following request:\n"
            f"Query: {request.query}\n"
            f"Course Material: {course_material}"
        )
        system_message = "You are an academic assistant that creates detailed study plans for students."
        plan = await generate_openai_chat_response(system_message, user_message, max_tokens=300)
        return AssistantResponse(response=plan)
    
    elif "assignment" in query_lower or "homework" in query_lower or "hint" in query_lower:
        user_message = (
            f"Provide a hint to help with the assignment. Do not provide the full solution.\n"
            f"Query: {request.query}\n"
            f"Course Material: {course_material}"
        )
        system_message = (
            "You are an academic assistant that provides hints for assignments, "
            "encouraging critical thinking without giving full answers."
        )
        hint = await generate_openai_chat_response(system_message, user_message, max_tokens=150)
        return AssistantResponse(response=hint)
    
    else:
        return AssistantResponse(response="Please clarify if you need a study plan, assignment hint, or code completion. Your query did not specify a clear request.")

# Endpoint for file uploading (e.g., for file analysis or storage)
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload a file. In production, this could be processed, stored, or analyzed.
    For now, it returns a dummy response.
    """
    try:
        contents = await file.read()
        return {"filename": file.filename, "size": len(contents), "message": "File received successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

# Endpoint for image recognition (simulated for demonstration)
@app.post("/image_recognition", response_model=AssistantResponse)
async def image_recognition(file: UploadFile = File(...)):
    """
    Endpoint for image recognition. This dummy implementation simulates extracting text or features from an image.
    """
    try:
        contents = await file.read()
        # Simulate image processing, e.g., OCR.
        recognized_text = "Recognized text from image: Test Image"
        return AssistantResponse(response=recognized_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image recognition error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

