# GitHub Repo Analyzer

A FastAPI application that accepts GitHub repository URLs, queues them for analysis using Celery and Redis, and clones the repositories into temporary directories.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start Redis server (assuming it's installed):
   ```bash
   redis-server
   ```

3. Start the Celery worker:
   ```bash
   celery -A celery_app worker --loglevel=info
   ```

4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage

Send a POST request to `/analyze` with a JSON body containing the GitHub URL:

```json
{
  "github_url": "https://github.com/user/repo"
}
```

The response will include a task ID. You can check the task status using Celery's built-in monitoring or extend the API to query task results.# Project-Vulnerabilities-Analyzer
