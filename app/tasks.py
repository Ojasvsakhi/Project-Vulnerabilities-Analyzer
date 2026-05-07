import tempfile
import subprocess
import os
from urllib.parse import urlparse
from celery_app import celery_app
import tempfile
@celery_app.task
def clone_repo(github_url: str):
    with tempfile.TemporaryDirectory() as repo_dir:
        try:
            subprocess.run(["git", "clone", github_url, repo_dir], check=True, capture_output=True, text=True)
            result = subprocess.run(
                ["./build/analyzer",repo_dir],
                capture_output=True,
                text=True
            )
            return {"status": "cloned", "path": repo_dir, "url": github_url,"tree": stdout}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "error": str(e), "url": github_url}