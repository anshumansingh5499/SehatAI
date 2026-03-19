import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from app.chain import build_rag_chain
from app.guardrails import check_emergency

load_dotenv()

app = FastAPI(title="SehatAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

print("Building RAG chain...")
rag_chain = build_rag_chain()
print("RAG chain ready!")


class SymptomRequest(BaseModel):
    message: str
    session_id: str = "default"


class TriageResponse(BaseModel):
    response: str
    is_emergency: bool
    sources: list[str] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResponse)
async def triage(request: SymptomRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    emergency = check_emergency(request.message)
    if emergency["is_emergency"]:
        return TriageResponse(
            response=emergency["message"],
            is_emergency=True
        )

    last_error = None
    for attempt in range(3):
        try:
            result = rag_chain({
                "question": request.message,
                "session_id": request.session_id
            })

            answer = (
                result.get("answer") or
                result.get("result") or
                str(list(result.values())[0])
            )

            sources = []
            if "source_documents" in result:
                sources = list(set([
                    doc.metadata.get("source", "").split("\\")[-1].split("/")[-1]
                    for doc in result["source_documents"]
                    if doc.metadata.get("source")
                ]))

            return TriageResponse(
                response=answer,
                is_emergency=False,
                sources=sources
            )

        except Exception as e:
            last_error = str(e)
            print(f"Attempt {attempt + 1} failed: {e}")
            if "429" in str(e) or "quota" in str(e).lower():
                wait = (attempt + 1) * 20
                print(f"Rate limited — waiting {wait}s...")
                time.sleep(wait)
                continue
            break

    raise HTTPException(
        status_code=500,
        detail=f"Error: {last_error}"
    )