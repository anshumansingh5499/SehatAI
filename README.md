# SehatAI — AI Medical Symptom Triage for India

> Built with Python · LangChain · FastAPI · OpenAI GPT · ChromaDB

🔴 Live Demo: https://sehatai.streamlit.app/

## The Problem
India has 1 doctor per 1,456 patients. Millions rely 
on Google for health decisions. SehatAI provides 
structured, safe symptom triage using AI.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| AI/LLM | LangChain, OpenAI GPT-3.5, RAG |
| Backend | Python, FastAPI, Pydantic |
| Vector DB | ChromaDB, HuggingFace Embeddings |
| Frontend | Streamlit |
| Safety | Emergency guardrails, Disclaimers |

## How to Run
pip install -r requirements.txt
uvicorn app.main:app --reload
streamlit run frontend/ui.py

## What I Learned
- RAG pipeline implementation in production
- Prompt engineering for medical safety
- FastAPI REST API design patterns
- Vector database integration
