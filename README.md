# RAG-based Flight Query Bot

## Project Overview
The RAG-based Flight Query Bot is a Streamlit-powered web application that allows users to query flight information using natural language (e.g., "Show me flights from New York to London"). It uses Retrieval-Augmented Generation (RAG) with an Ollama language model to extract entities from queries and retrieve flight data from a mock database. The project is deployed on a local Kubernetes cluster using Minikube and includes a CI/CD pipeline with GitHub Actions for automated testing.

### Architecture
```
  RAG-based-Flight-Query-Bot/
  ├── .github/
  │   └── workflows/
  │       └── test.yml
  ├── tests/
  │   └── test_mock_database.py
  ├── mock_database.py
  ├── query_handler.py
  ├── ollama_api.py
  ├── app.py (optional)
  ├── requirements.txt
  └── README.md
  ```
- **Frontend**: Streamlit UI (`app.py`) for user interaction.
- **Backend**: 
  - `query_handler.py`: Processes queries and extracts entities using Ollama.
  - `ollama_api.py`: Integrates with the Ollama LLM for natural language responses.
  - `mock_database.py`: Provides mock flight data and search functionality.
- **Deployment**: Kubernetes on Minikube with two services: `flight-assistant-service` (Streamlit) and `ollama-service` (Ollama server).
- **CI/CD**: GitHub Actions runs unit tests on every push or pull request.
---

## Setup Instructions

### Prerequisites
- **Windows, macOS, or Linux**
- **Python 3.10 or 3.11**
- **Docker Desktop** (for building images and running Minikube)
- **Minikube** (for local Kubernetes)
- **kubectl** (Kubernetes CLI)
- **Git** (for cloning the repository)

### Step 1: Clone the Repository
Clone this project to your local machine:
```bash
git clone https://github.com/RobuRishabh/RAG-based-Flight-Query-Bot.git
cd RAG-based-Flight-Query-Bot
```

### Step 2: Install Python Dependencies
Create a virtual environment and install required Python packages:
```bash
# Create a virtual environment (optional but recommended)
python -m venv flightquerybot

# Activate it (Windows)
flightquerybot\Scripts\activate

# Activate it (macOS/Linux)
source flightquerybot/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Set Up and Run the Local Ollama Server
The project uses a local Ollama server for language processing.

#### Install Ollama:
- Download and install Ollama from [ollama.com](https://ollama.com).
- Follow the installation instructions for your OS.

#### Pull the Model:
```bash
ollama pull llama2:latest
```
This downloads the `llama2:latest` model (default for this project).

#### Run the Ollama Server:
```bash
ollama serve
```
Keep this terminal open. The server runs at `http://localhost:11434`.

### Step 4: Set Up Minikube
Minikube creates a local Kubernetes cluster.

#### Install Minikube:
Follow the [official Minikube installation guide](https://minikube.sigs.k8s.io/docs/start/) for your OS.
Example for Windows (using PowerShell as admin):
#### Start Minikube:
```bash
minikube start
```

#### Verify Minikube:
```bash
minikube status
```
Ensure `host`, `kubelet`, and `apiserver` are `Running`.

---

## Deployment Steps

### Step 1: Build the Docker Image
Build the `flight-assistant` Docker image using Minikube’s Docker daemon:
```bash
# Set Minikube's Docker environment
eval $(minikube docker-env)

# Build the image
docker build -t flight-assistant:latest .
```

### Step 2: Apply Kubernetes YAML Files
Deploy the application and Ollama server to Minikube:
```bash
# Deploy Ollama server
kubectl apply -f ollama-deployment.yaml
kubectl apply -f ollama-service.yaml

# Deploy Flight Assistant app
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Step 3: Expose and Access the Services
#### Start Minikube Tunnel:
```bash
minikube tunnel
```
Keep this running to assign an external IP.

#### Get the Service URL:
```bash
minikube service flight-assistant-service --url
```
Example output: `http://192.168.49.2:8501`.

#### Access the App:
Open the URL in your browser to interact with the chatbot.

---

## Usage

### Interacting with the Chatbot UI
1. Open the Streamlit app in your browser.
2. Enter a query in the text box and press Enter.
3. The bot processes your query and displays flight details or a "no flights found" message.

#### Example Queries
- `"Show me flight NY100"` → Shows details for flight `NY100`.
- `"What are the flights from New York to London?"` → Lists matching flights.
- `"Flights from Chicago"` → Shows flights departing from Chicago.
- `"Flight XYZ999"` → Returns "No flights found" (invalid flight).

---

## CI/CD Explanation

### GitHub Actions Configuration
This project uses GitHub Actions for Continuous Integration (CI) to ensure code quality. The workflow is defined in `.github/workflows/test.yml`.

#### Workflow Details
- **Trigger**: Runs on every `push` or `pull_request` to the `main` branch.
- **Environment**: Uses an `ubuntu-latest` runner with Python 3.10.
- **Steps**:
  - Checkout code:
    ```yaml
    - uses: actions/checkout@v4
    ```
  - Set up Python:
    ```yaml
    - uses: actions/setup-python@v5
      with:
        python-version: '3.10'
    ```
  - Install dependencies:
    ```yaml
    - run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    ```
  - Run tests:
    ```yaml
    - run: |
        python -m unittest discover -s tests -p "test_*.py"
    ```

---

## Running Tests Locally
To test before pushing:
```bash
# Activate virtual environment
flightquerybot\Scripts\activate  # Windows
source flightquerybot/bin/activate  # macOS/Linux

# Run all tests
python -m unittest discover -s tests -p "test_*.py"
```
Expected output: `Ran X tests in Y.YYYs OK`.

---

## Documentation Notes

### Stopping Minikube
```bash
minikube stop
```

### Cleanup (Reset Everything)
```bash
minikube delete
```

### Troubleshooting
If the UI doesn’t load, check pod logs:
```bash
kubectl logs -l app=flight-assistant
kubectl logs -l app=ollama
```
Ensure `minikube tunnel` is running for external access.

---
