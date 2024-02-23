from fastapi import FastAPI, WebSocket, HTTPException, Request
from pydantic import BaseModel
from typing import List

import git
import os

app = FastAPI()


class CloneRequest(BaseModel):
    url: str
    dest_folder: str
    instructions: List[str] = []

def clone_repo(repo_url: str, dest_folder: str, instructions: List[str] = None):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    
    try:
        git.Repo.clone_from(repo_url, dest_folder)
        print("Repository cloned successfully.")
        if instructions:
            print("instructions found")
            os.chdir(dest_folder)
            for instruction in instructions:
                os.system(instruction)  

            print("Server started with instructions: {}".format(", ".join(instructions)))
    except Exception as e:
        return f"Failed to clone repository: {e}"

@app.post("/clone/")
async def http_clone_repo(request: Request, data: CloneRequest):
    url = data.url
    dest_folder = data.dest_folder
    instructions = data.instructions
    
    # Call the common cloning function
    result_message = clone_repo(url, dest_folder, instructions)

    return {"url": url, "dest_folder": dest_folder, "result_message": result_message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
