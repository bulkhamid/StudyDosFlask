from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_study_plan():
    # This request should trigger the study plan response.
    payload = {
        "query": "I need a 10-day study plan for Artificial Intelligence starting from 2025-03-01.",
        "course_material": "Optional course material if available."
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Check that the dummy study plan response contains an expected marker like "Day 1:"
    assert "Day 1:" in data["response"]

def test_assignment_hint():
    # This request should trigger the assignment hint response.
    payload = {
        "query": "Can you give me a hint on how to approach the assignment on neural networks?",
        "course_material": "Optional course material if available."
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Check that the dummy assignment hint contains a phrase like "consider reviewing"
    assert "consider reviewing" in data["response"].lower() or "break the problem" in data["response"].lower()

def test_unclear_query():
    # For a query that doesn't clearly indicate either type, the assistant should ask for clarification.
    payload = {
        "query": "What is the weather like today?"
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Ensure that the response asks for clarification.
    assert "please clarify" in data["response"].lower()
