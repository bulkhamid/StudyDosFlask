from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import os
from datetime import date
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from openai import AsyncOpenAI
from pymongo import MongoClient
import gridfs

# Initialize asynchronous OpenAI client
aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="CivicHacks 2025 Unified Assistant with MongoDB Integration")

# MongoDB Atlas integration
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
study_db = mongo_client["test"]  # Database name
fs = gridfs.GridFS(study_db)      # Initialize GridFS instance

# Pydantic models for requests and responses
class AssistantRequest(BaseModel):
    query: str
    course_material: Optional[str] = None  # Optional override

class AssistantResponse(BaseModel):
    response: str

def get_course_material_from_db() -> str:
    """
    Retrieve course material from MongoDB stored in GridFS.
    """
    combined = []
    for grid_out in fs.find():
        title = grid_out.filename
        try:
            content = grid_out.read().decode('utf-8')
        except Exception:
            content = "<binary content>"
        if title or content:
            combined.append(f"{title}: {content}")
    return "\n".join(combined) if combined else "No course material available."

def get_today_date() -> str:
    return date.today().strftime("%Y-%m-%d")

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
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

async def generate_code_completion(prompt: str, max_tokens: int = 100, model: str = "o1-mini") -> str:
    """
    Generates a code-completion hint using the chat completions endpoint.
    Note: This model supports only a temperature of 1.
    """
    try:
        response = await aclient.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=1,  # Must be 1 for o1-mini.
            max_tokens=max_tokens
        )
        result = response.choices[0].message.content.strip()
        if not result:
            result = "Hint: Review the key steps required to complete this function."
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Code Completion API error: {str(e)}")

@app.post("/assistant", response_model=AssistantResponse)
async def unified_assistant(request: AssistantRequest):
    query_lower = request.query.lower()
    course_material = request.course_material if request.course_material else get_course_material_from_db()

    if "code completion" in query_lower or "complete code" in query_lower:
        prompt = (
            f"You are a helpful code completion assistant. Complete the following code snippet by giving hints and guiding the approach, "
            f"but do not provide the complete solution:\n\n"
            f"{request.query}\n"
            f"Context: {course_material}"
        )
        completed_code = await generate_code_completion(prompt, max_tokens=150, model="o1-mini")
        return AssistantResponse(response=completed_code)

    elif "study plan" in query_lower or "plan" in query_lower:
        today = get_today_date()
        user_message = (
            f"Generate a detailed 10-day study plan starting from {today} for the following request. "
            f"Reference the 'syllabus' file if relevant.\n\n"
            f"Query: {request.query}\n"
            f"Course Material: {course_material}\n"
        )
        system_message = "You are an academic assistant that creates detailed study plans for students."
        plan = await generate_openai_chat_response(system_message, user_message, max_tokens=300)
        return AssistantResponse(response=plan)
    
    elif "assignment" in query_lower or "homework" in query_lower or "hint" in query_lower:
        lecture_info = get_course_material_from_db()  # Get lecture details from MongoDB.
        user_message = (
            f"Provide a hint to help with the assignment. Do not provide the full solution.\n"
            f"Query: {request.query}\n"
            f"Course Material: {course_material}\n"
            f"Lecture Info: {lecture_info}\n"
        )
        system_message = (
            "You are an academic assistant that provides hints for assignments, "
            "encouraging critical thinking without giving full answers."
        )
        hint = await generate_openai_chat_response(system_message, user_message, max_tokens=150)
        return AssistantResponse(response=hint)
    
    else:
        return AssistantResponse(response="Please clarify if you need a study plan, assignment hint, or code completion. Your query did not specify a clear request.")


# (Optional) Keep image recognition endpoint for demonstration.
@app.post("/image_recognition", response_model=AssistantResponse)
async def image_recognition(file: UploadFile = File(...)):
    """
    Simulated image recognition endpoint for demonstration purposes.
    """
    try:
        # Read the file (not storing it, just simulating processing)
        contents = await file.read()
        recognized_text = "Recognized text from image: Test Image"
        return AssistantResponse(response=recognized_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image recognition error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read the file from the request.
        contents = await file.read()
        # Save the file to GridFS with its filename.
        file_id = fs.put(contents, filename=file.filename)
        return {"file_id": str(file_id), "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))