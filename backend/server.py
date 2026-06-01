from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import sys
import os

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    ticker: str
    date: str
    provider: str = "ollama"

@app.get("/")
def home():
    return {
        "status": "TradingAgents backend chal raha hai!",
        "provider": "ollama",
        "model": "llama3.2"
    }

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "ollama"
        config["deep_think_llm"] = "llama3.2"
        config["quick_think_llm"] = "llama3.2"
        config["ollama_base_url"] = "http://localhost:11434/v1"

        ta = TradingAgentsGraph(debug=False, config=config)
        _, decision = ta.propagate(req.ticker, req.date)

        return {
            "success": True,
            "ticker": req.ticker,
            "date": req.date,
            "decision": decision
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
