from fastapi import FastAPI, WebSocket, HTTPException, Body
from pydantic import BaseModel
from typing import List
import git
import os
import asyncio

app = FastAPI()

# Define a Pydantic model for the request body
class CloneRequest(BaseModel):
    github_url: str
    instructions: List[str] = []

# Directory to clone the repositories into
destination_folder = "./clone-repo"

# WebSocket endpoint for logging
connected_websockets = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        while True:
            # Just to keep the connection open
            await websocket.receive_text()
    finally:
        connected_websockets.remove(websocket)

# HTTP POST endpoint to receive the cloning request
@app.post("/clone-repo/")
async def clone_repo_request(clone_request: CloneRequest):
    github_url = clone_request.github_url
    instruc = clone_request.instructions
    await clone_repo(github_url, destination_folder, instruc)

async def run_server(instruction: str, websocket: WebSocket):
    try:
        process = await asyncio.create_subprocess_exec(
            *instruction.split(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await websocket.send_text(line.decode())

        await process.wait()
        return process.returncode
    except Exception as e:
        await websocket.send_text(f"Error executing instruction: {instruction}, {e}")
        return 1

async def run_instruction(instruction: str, websocket: WebSocket):
    if instruction.startswith("node"):
        # Run server command in the background
        asyncio.create_task(run_server(instruction, websocket))
    else:
        # Run other instructions as usual
        await asyncio.create_task(_run_instruction(instruction, websocket))

async def run_instruction(instruction: str, websocket: WebSocket):
    try:
        process = await asyncio.create_subprocess_exec(
            *instruction.split(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        await websocket.send_text(f"Output of '{instruction}':\n{stdout.decode()}\nErrors:\n{stderr.decode()}")
        return process.returncode

    except Exception as e:
        await websocket.send_text(f"Error executing instruction: {instruction}, {e}")
        return 1

# ... (other code remains unchanged)

async def clone_repo(repo_url: str, dest_folder: str, instructions: List[str] = []):
    print(f"Instructions :: {instructions}")
    for websocket in connected_websockets:
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
            await websocket.send_text(f"Directory {dest_folder} created.")
        else:
            await websocket.send_text(f"Directory {dest_folder} already exists.")

        try:
            await websocket.send_text(f"Cloning repository from {repo_url} into {dest_folder}")
            git.Repo.clone_from(repo_url, dest_folder)
            await websocket.send_text("Repository cloned successfully.")

            os.chdir(dest_folder)
            for instruction in instructions:
                return_code = await run_instruction(instruction, websocket)
                if return_code != 0:
                    raise Exception(f"Failed to execute instruction: {instruction}, Return Code: {return_code}")

            await websocket.send_text("All instructions completed.")

        except Exception as e:
            await websocket.send_text(f"Failed to clone repository: {e}")

        await websocket.send_text("Clone process completed.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
