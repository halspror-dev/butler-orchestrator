import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from orchestrator import orchestrate

from memory import save_memory

BASE_DIR = os.path.dirname(__file__)

app = FastAPI(title="Butler API")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/")
async def index():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


class ChatRequest(BaseModel):
    message: str
    history: str = ""


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        worker, reply, proposal = orchestrate(req.message, history=req.history or None)
        return {"worker": worker, "reply": reply, "proposed_memory": proposal}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

class MemoryRequest(BaseModel):
    fact: str

@app.post("/save_memory")
async def save_memory_endpoint(req: MemoryRequest):
    try:
        save_memory(req.fact)
        return {"status": "saved", "fact": req.fact}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
