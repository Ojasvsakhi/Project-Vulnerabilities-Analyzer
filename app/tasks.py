# import tempfile
# import subprocess
# import os
# from urllib.parse import urlparse
# from celery_app import celery_app
# import tempfile
# @celery_app.task(bind=True)
# def clone_repo(self,github_url: str):
#     with tempfile.TemporaryDirectory() as repo_dir:
#         try:
#             subprocess.run(["git", "clone", github_url, repo_dir], check=True, capture_output=True, text=True)
#             self.update_state(state='ANALYZING', meta={'message': 'Cloning complete. Booting C++ Engine...'})
#             result = subprocess.run(
#                 ["./build/analyzer",repo_dir],
#                 capture_output=True,
#                 text=True
#             )
#             return {"status": "cloned", "path": repo_dir, "url": github_url,"tree": result.stdout}
#         except subprocess.CalledProcessError as e:
#             return {"status": "error", "error": str(e), "url": github_url}
import subprocess
import tempfile
import os
import shutil
import boto3
from dotenv import load_dotenv
from celery_app import celery_app 

load_dotenv()
def generate_directory_tree(startpath, max_depth=3):
    tree_str = []
    startpath = os.path.abspath(startpath)
    
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        if level > max_depth:
            continue
            
        indent = ' ' * 4 * level
        folder_name = os.path.basename(root)
        if folder_name == '.git':
            dirs[:] = []
            continue
            
        tree_str.append(f"{indent}|-- [{folder_name}/]")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree_str.append(f"{subindent}|-- {f}")
            
    return "\n".join(tree_str)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

@celery_app.task(bind=True)
def clone_repo(self, github_url):
    repo_name = github_url.split("/")[-1].replace(".git", "")
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(["git", "clone", github_url, temp_dir], check=True)
        repo_tree = generate_directory_tree(temp_dir)
        self.update_state(state='ANALYZING', meta={'status': 'Analyzing and compressing...','tree': repo_tree})
        
        result = subprocess.run(
            ["./build/analyzer", temp_dir],
            capture_output=True,
            text=True
            )
        archive_path = shutil.make_archive(f"/tmp/{repo_name}", 'gztar', temp_dir)
        
        s3_key = f"sessions/{repo_name}.tar.gz"
        s3.upload_file(archive_path, BUCKET_NAME, s3_key)
        
        os.remove(archive_path)

        return {
            "status": "cloned_and_stored",
            "url": github_url,
            "tree": repo_tree,
            "report": result.stdout,
            "s3_key": s3_key
        }