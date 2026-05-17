"""FastAPI routes for the Cross-Border Ecommerce AI System."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from agents.market_insight_agent import MarketInsightAgent
from agents.copywriter_agent import CopywriterAgent
from agents.customer_service_agent import CustomerServiceAgent
from core.orchestrator import Orchestrator
from core.llm_simulator import LLMSimulator
from core.rag_engine import RAGEngine
from core.erp_connector import ERPConnector
from utils.token_counter import token_counter

app = FastAPI(
    title="Cross-Border Ecommerce AI API",
    description="Multi-Agent Marketing & Customer Service System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize on startup
llm = LLMSimulator()
rag = RAGEngine()
erp = ERPConnector()
from data import load_sample_data
sample_data = load_sample_data()
rag.load_documents(sample_data.get("faq_documents", []))

market_agent = MarketInsightAgent(llm=llm)
copy_agent = CopywriterAgent(llm=llm)
cs_agent = CustomerServiceAgent(llm=llm, rag_engine=rag, erp_connector=erp)

orchestrator = Orchestrator(
    market_insight_agent=market_agent,
    copywriter_agent=copy_agent,
    customer_service_agent=cs_agent
)


# Request/Response models
class MarketAnalysisRequest(BaseModel):
    product_category: str = "wireless earbuds"
    platforms: List[str] = ["amazon", "shopee"]
    max_reviews: int = Field(default=200, le=500)

class CopyGenerationRequest(BaseModel):
    pain_points: List[Dict[str, Any]]
    target_market: str = "Southeast Asia"
    languages: List[str] = ["en"]
    rounds: int = Field(default=3, ge=1, le=5)

class CustomerQueryRequest(BaseModel):
    query: str
    language: str = "en"
    customer_context: Optional[Dict] = None


@app.get("/")
async def root():
    return {"system": "Cross-Border Ecommerce AI", "status": "running", "mode": "demo"}

@app.post("/market/analyze")
async def analyze_market(request: MarketAnalysisRequest):
    """Analyze competitor reviews and extract insights."""
    result = await orchestrator.market_insight.analyze_reviews(
        product_category=request.product_category,
        platforms=request.platforms,
        max_reviews=request.max_reviews
    )
    return result

@app.post("/copy/generate")
async def generate_copy(request: CopyGenerationRequest):
    """Generate marketing copy with refinement."""
    result = await orchestrator.copywriter.generate_copy(
        pain_points=request.pain_points,
        target_market=request.target_market,
        languages=request.languages,
        rounds=request.rounds
    )
    return result

@app.post("/customer/query")
async def handle_customer_query(request: CustomerQueryRequest):
    """Handle a customer service inquiry."""
    result = await orchestrator.customer_service.handle_query(
        query=request.query,
        language=request.language,
        customer_context=request.customer_context
    )
    return result

@app.get("/system/status")
async def get_system_status():
    """Get full system status and token usage."""
    return orchestrator.get_system_status()

@app.get("/tokens/summary")
async def get_token_summary():
    """Get token consumption summary."""
    return {
        "daily": token_counter.get_daily_summary(),
        "cost_estimate": token_counter.estimate_cost()
    }

@app.post("/pipeline/full")
async def run_full_pipeline(
    category: str = "wireless earbuds",
    market: str = "Southeast Asia",
    languages: str = "en,th,id,vi",
    rounds: int = 3
):
    """Run the full marketing pipeline."""
    lang_list = [l.strip() for l in languages.split(",")]
    result = await orchestrator.run_full_marketing_pipeline(
        product_category=category,
        target_market=market,
        languages=lang_list,
        refinement_rounds=rounds
    )
    return result
