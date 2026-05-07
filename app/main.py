from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.tasks import clone_repo

app = FastAPI()

class RepoRequest(BaseModel):
    github_url: str
# Root message
@app.get("/")
async def root():
    return {"message": "GitHub Repo Analyzer API", "endpoint": "/analyze", "docs": "/docs"}

@app.post("/analyze")
async def analyze_repo(request: RepoRequest):
    if not request.github_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    
    # Task Queue
    task = clone_repo.delay(request.github_url)
    
    return {"task_id": task.id, "status": "queued"}