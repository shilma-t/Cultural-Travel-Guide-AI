# culture_agent_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from culture_agent import CultureAgent  # Import your existing CultureAgent class

# ----------- FastAPI app setup -----------
app = FastAPI(
    title="CultureAgent API",
    description="A microservice exposing CultureAgent for culturally sensitive travel guidance",
    version="1.0.0",
)

# ----------- Request/Response Models -----------
class QueryRequest(BaseModel):
    query: str
    enable_web_search: Optional[bool] = False

class QueryResponse(BaseModel):
    answer: str
    tl_dr: str
    sources: list[str]
    confidence: float
    flags: list[str]

# ----------- Initialize CultureAgent -----------
agent = CultureAgent()  # You can pass API keys here if needed

# ----------- API Endpoints -----------

@app.get("/")
def root():
    return {"message": "CultureAgent API is running. Use POST /query to ask questions."}

@app.post("/query", response_model=QueryResponse)
def query_culture_agent(request: QueryRequest):
    try:
        result = agent.generate_answer(request.query, enable_web_search=request.enable_web_search)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
