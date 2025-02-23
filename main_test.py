import pytest
from fastapi.testclient import TestClient
from main import app
from types import SimpleNamespace  # used to create dummy message objects

client = TestClient(app)

# Dummy async functions to simulate OpenAI API responses.
async def dummy_chat_acreate(model, messages, temperature, max_tokens=None, max_completion_tokens=None):
    # Examine the system message to decide which dummy text to return.
    system_message = messages[0]["content"].lower() if messages else ""
    if "study plan" in system_message:
        dummy_text = (
            "Day 1: Outline study goals.\n"
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
    elif "assignment" in system_message or "homework" in system_message or "hint" in system_message:
        dummy_text = "Consider breaking the assignment into smaller parts and reviewing the lecture concepts."
    else:
        dummy_text = "Dummy chat response."
    
    class DummyChoice:
        def __init__(self, content):
            self.message = SimpleNamespace(content=content)
    class DummyResponse:
        def __init__(self, content):
            self.choices = [DummyChoice(content)]
    return DummyResponse(dummy_text)

async def dummy_code_acreate(model, messages, temperature, max_tokens=None, max_completion_tokens=None):
    dummy_code = "def completed_function():\n    pass"
    class DummyChoice:
        def __init__(self, content):
            self.message = SimpleNamespace(content=content)
    class DummyResponse:
        def __init__(self, content):
            self.choices = [DummyChoice(content)]
    return DummyResponse(dummy_code)

# Dispatch based on model: use dummy code completion for "o1-mini", else dummy chat.
async def dummy_create(model, messages, temperature, max_tokens=None, max_completion_tokens=None):
    if model == "o1-mini":
        return await dummy_code_acreate(model, messages, temperature, max_tokens, max_completion_tokens)
    else:
        return await dummy_chat_acreate(model, messages, temperature, max_tokens, max_completion_tokens)

@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    # Patch the asynchronous chat completions call with our dummy_create.
    monkeypatch.setattr("main.aclient.chat.completions.create", dummy_create)

def test_study_plan():
    payload = {
        "query": "I need a 10-day study plan for DL4DS.",
        "course_material": "Some optional course material."
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    # Check that our dummy study plan response is returned.
    assert "Day 1:" in data["response"]

def test_assignment_hint():
    payload = {
        "query": "Can you give me a hint on how to approach the assignment?",
        "course_material": "Some optional course material."
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    # Check that our dummy assignment hint is returned.
    assert "consider breaking" in data["response"].lower()

def test_code_completion():
    payload = {
        "query": "Please perform code completion: complete code for a function that adds two numbers.",
        "course_material": "Some optional context for code."
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    # Our dummy code completion returns a function definition.
    assert "def completed_function():" in data["response"]

def test_unclear_query():
    payload = {
        "query": "What is the weather like today?"
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    # Since our query does not match any intent, we expect a clarification message.
    assert "please clarify" in data["response"].lower()

def test_missing_query():
    payload = {
        "course_material": "Some optional course material."
    }
    response = client.post("/assistant", json=payload)
    # FastAPI should return a 422 error because "query" is required.
    assert response.status_code == 422

def test_malformed_request():
    response = client.post("/assistant", data="this is not json")
    assert response.status_code == 422

def test_file_upload():
    files = {"file": ("test.txt", b"Hello World", "text/plain")}
    response = client.post("/upload/", files=files)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.txt"
    assert "File received successfully" in data["message"]

def test_image_recognition():
    files = {"file": ("image.png", b"fake image bytes", "image/png")}
    response = client.post("/image_recognition", files=files)
    assert response.status_code == 200, response.text
    data = response.json()
    # Our image recognition endpoint returns a fixed string.
    assert "recognized text from image" in data["response"].lower()
