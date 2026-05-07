from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from celery.result import AsyncResult
from app.tasks import clone_repo
from celery_app import celery_app
app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")
class RepoRequest(BaseModel):
    github_url: str
# Root message
@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/analyze")
async def analyze_repo(request: RepoRequest):
    if not request.github_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    
    # Task Queue
    task = clone_repo.delay(request.github_url)
    
    return {"task_id": task.id, "status": "queued"}
@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_res=AsyncResult(task_id,app=celery_app)
    return {
        "task_id": task_id,
        "status": task_res.status,
        "result": task_res.result if task_res.ready() else None
    }