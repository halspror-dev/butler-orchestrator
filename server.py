import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from orchestrator import orchestrate

app = FastAPI(title="Butler API")


class ChatRequest(BaseModel):
    message: str
    history: str = ""


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        worker, reply = orchestrate(req.message, history=req.history or None)
        return {"worker": worker, "reply": reply}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
