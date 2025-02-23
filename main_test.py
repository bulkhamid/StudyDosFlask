import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Dummy async function for chat-based responses (study plan & assignment hint)
async def dummy_chat_acreate(model, messages, temperature, max_tokens):
    system_message = messages[0]["content"]
    if "study plans" in system_message:
        dummy_text = (
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
    elif "assignments" in system_message:
        dummy_text = "Consider reviewing the theory and breaking the problem into manageable parts."
    else:
        dummy_text = "Dummy chat response."
    
    class DummyChoice:
        def __init__(self, content):
            self.message = {"content": content}
    class DummyResponse:
        def __init__(self, content):
            self.choices = [DummyChoice(content)]
    return DummyResponse(dummy_text)

# Dummy async function for code completion responses
async def dummy_code_acreate(model, prompt, temperature, max_tokens):
    dummy_code = "def completed_function():\n    pass"
    class DummyChoice:
        def __init__(self, text):
            self.text = text
    class DummyResponse:
        def __init__(self, text):
            self.choices = [DummyChoice(text)]
    return DummyResponse(dummy_code)

# Patch both async API calls
@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    monkeypatch.setattr("main.openai.ChatCompletion.acreate", dummy_chat_acreate)
    monkeypatch.setattr("main.openai.Completion.acreate", dummy_code_acreate)

def test_study_plan():
    payload = {
        "query": "I need a 10-day study plan for Artificial Intelligence starting from 2025-03-01.",
        "course_material": "Optional course material if available."
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Day 1:" in data["response"]

def test_assignment_hint():
    payload = {
        "query": "Can you give me a hint on how to approach the assignment on neural networks?",
        "course_material": "Optional course material if available."
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    response_text = data["response"].lower()
    assert "consider reviewing" in response_text or "breaking the problem" in response_text

def test_code_completion():
    payload = {
        "query": "Please perform code completion: complete code for a function that adds two numbers.",
        "course_material": "Optional context for code."
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Our dummy returns a function definition
    assert "def completed_function():" in data["response"]

def test_unclear_query():
    payload = {
        "query": "What is the weather like today?"
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "please clarify" in data["response"].lower()

def test_missing_query():
    payload = {
        "course_material": "Optional course material if available."
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 422

def test_malformed_request():
    response = client.post("/assistant", data="this is not json")
    assert response.status_code == 422

def test_file_upload():
    files = {"file": ("test.txt", b"Hello World", "text/plain")}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["size"] == len(b"Hello World")
    assert "File received successfully." in data["message"]

def test_image_recognition():
    files = {"file": ("image.png", b"fake image bytes", "image/png")}
    response = client.post("/image_recognition", files=files)
    assert response.status_code == 200
    data = response.json()
    # Our dummy image recognition returns a fixed string.
    assert "recognized text from image" in data["response"].lower()