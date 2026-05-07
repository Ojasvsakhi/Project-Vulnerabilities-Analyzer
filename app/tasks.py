import tempfile
import subprocess
import os
from urllib.parse import urlparse
from celery_app import celery_app

@celery_app.task
def clone_repo(github_url: str):
    parsed = urlparse(github_url)
    repo_path = parsed.path.strip('/')
    repo_name = repo_path.replace('/', '_')
    
    repo_dir = f"/tmp/repos/{repo_name}"
    os.makedirs(repo_dir, exist_ok=True)
    
    try:
        subprocess.run(["git", "clone", github_url, repo_dir], check=True, capture_output=True, text=True)
        return {"status": "cloned", "path": repo_dir, "url": github_url}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": str(e), "url": github_url}