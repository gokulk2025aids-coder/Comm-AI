import requests
import json

# Test the quiz endpoints
BASE_URL = "http://localhost:8000"

print("Testing Quiz Endpoints...")
print("=" * 50)

# Test 1: Get quiz questions
print("\n1. Testing GET /api/quiz/questions?count=5")
try:
    response = requests.get(f"{BASE_URL}/api/quiz/questions?count=5")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Number of questions: {len(data.get('questions', []))}")
        if data.get('questions'):
            print(f"First question: {data['questions'][0]['question']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Submit quiz answers
print("\n2. Testing POST /api/quiz/submit")
try:
    # Sample answers
    test_answers = {
        "answers": [
            {"question_id": 1, "selected": 1},
            {"question_id": 2, "selected": 1},
            {"question_id": 3, "selected": 1},
            {"question_id": 4, "selected": 2},
            {"question_id": 5, "selected": 1}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/quiz/submit",
        json=test_answers,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        if data.get('score'):
            score = data['score']
            print(f"Score: {score['correct']}/{score['total']} ({score['percentage']}%)")
            print(f"Grade: {score['grade']}")
            print(f"Message: {score['message']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Testing complete!")
print("\nIf you see errors, make sure:")
print("1. The server is running (start.bat)")
print("2. You're accessing http://localhost:8000")
print("3. The backend/email_quiz.py file exists")
