# StudyDos

**Study Smarter, Think Deeper**

StudyDos is a cost-efficient, AI-powered academic assistant designed to empower students with guided hints, tailored study plans, and code completion support—while preserving critical thinking and academic integrity. With multi-modal features such as file uploads and simulated image recognition, StudyDos adapts to various learning styles and course materials.

## Features

- **Tailored Academic Guidance:**  
  Provides assignment hints and detailed study plans without giving away complete solutions.
  
- **Code Completion:**  
  Uses a cost-efficient AI model for code completions to help with programming assignments.
  
- **Multi-Modal Input:**  
  Supports file uploads and simulated image recognition for enhanced content analysis.
  
- **Unified Endpoint:**  
  A single, intelligent endpoint distinguishes between study plan requests, assignment hints, and code completion needs.
  
- **Secure Configuration:**  
  Environment variables are managed via a `.env` file using python-dotenv for easy and secure configuration.

## Getting Started

### Prerequisites

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)
- An OpenAI API key

### Installation

1. **Clone the Repository:**

   ```
   git clone https://github.com/your_username/StudyDos.git
   cd StudyDos
   ```

2. **Create and Activate a Virtual Environment:**

    ```
    python -m venv env
    # On Windows:
    env\Scripts\activate
    # On Unix or MacOS:
    source env/bin/activate
    ```
3. **Install Dependencies:**
    ```
    pip install -r requirements.txt
    ```
4. **Create a .env File:**
    
    In the project root, create a `.env` file with your OpenAI API key:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```
### API Endpoints
- `POST /assistant`
    A unified endpoint that returns:

    - A detailed 10-day study plan if the query contains keywords like "study plan" or "plan".
    - A guided assignment hint if the query contains keywords like "assignment", "homework", or "hint".
    - Code completion for programming-related queries if the query contains keywords like "code completion" or "complete code".
- `POST /upload`
    Upload files (e.g., text documents) for further processing.

- `POST /image_recognition`
    Simulated image recognition endpoint that returns dummy recognized text from an image.

### Testing
#### Automated Tests
    Tests are written using pytest. To run the tests:
    ```pytest --maxfail=1 --disable-warnings -q```

#### Postman Collection
An updated Postman collection is provided to test all endpoints. Import the `CivicHacks_MultiModal_Tests.postman_collection.json` file into Postman and run the collection to verify functionality.


### Project Story
StudyDos was inspired by the need for academic tools that guide students without spoon-feeding answers. We created an AI assistant that supports deeper learning by offering hints and structured study plans while also providing code assistance for programming assignments. Through integrating OpenAI’s latest multi-modal features with FastAPI, we built a system that is both cost-efficient and versatile. Despite challenges such as API migration and multi-modal integration, our team delivered a robust prototype that empowers students to learn actively and responsibly.

### What's Next
- Enhanced AI Capabilities: Implement adaptive learning algorithms for personalized study recommendations.
- Robust Database Integration: Expand course material management for more tailored responses.
- User Feedback Integration: Build analytics and feedback loops to continuously refine the assistant.
- Expanded Multi-Modal Support: Improve image recognition and file processing to handle a broader range of academic content.

### License
This project is licensed under the MIT License.


**StudyDos** – Your smart study buddy for a brighter academic future.