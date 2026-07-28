# AI News Agent (`ai-news-agent`)

Serverless AI Breaking News Orchestrator built with GCP, FastAPI, Vertex AI (`gemini-2.5-flash`), and GCP Text-to-Speech (`en-US-Studio-O`).

## Architecture & Tech Stack
* **Cloud Platform**: 100% Google Cloud Platform (GCP) Serverless (`gen-lang-client-0771706827`)
* **Backend Framework**: Python FastAPI (`main.py`)
* **AI Orchestration**: Vertex AI SDK (`google-genai`) targeting `gemini-2.5-flash` in `us-central1`
* **Audio Synthesis**: `google-cloud-texttospeech` with `en-US-Studio-O` voice model
* **Authentication**: Application Default Credentials (ADC) for local dev, Workload Identity Federation for GitHub Actions CI/CD

## Project Structure
```text
ai-news-agent/
├── main.py              # FastAPI application endpoints (/health, /generate/script, /generate/audio)
├── setup_gcp_env.ps1    # PowerShell script to enable GCP APIs & provision Workload Identity Federation
├── requirements.txt     # Python dependency specifications
└── venv/                # Python virtual environment
```

## Quick Start Guide

### 1. Execute GCP Environment Setup
Run the infrastructure setup script in Windows PowerShell:
```powershell
.\setup_gcp_env.ps1
```

### 2. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Run FastAPI Application
```powershell
uvicorn main:app --reload
```
Access interactive API documentation at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Endpoints

### `GET /health`
Returns system health and active GCP configuration context.

### `POST /generate/script`
Generates a 2-sentence breaking news hook script.
* **Request Body**: `{"prompt": "Major breakthrough in fusion energy power plants."}`
* **Response**: `{"script": "Scientists have achieved net energy gain...", "model": "gemini-2.5-flash"}`

### `POST /generate/audio`
Synthesizes news script text into an MP3 audio file.
* **Request Body**: `{"text": "Breaking news: Scientists have achieved net energy gain..."}`
* **Response**: `audio/mpeg` stream (MP3 format).
