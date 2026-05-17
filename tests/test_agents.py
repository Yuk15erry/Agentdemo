"""Unit tests for the agent system."""
import pytest
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.market_insight_agent import MarketInsightAgent
from agents.copywriter_agent import CopywriterAgent
from agents.customer_service_agent import CustomerServiceAgent
from core.llm_simulator import LLMSimulator
from core.rag_engine import RAGEngine
from core.erp_connector import ERPConnector
from core.orchestrator import Orchestrator
from utils.token_counter import TokenCounter


@pytest.fixture
def llm():
    return LLMSimulator()


@pytest.fixture
def token_counter_fresh():
    tc = TokenCounter(daily_limit=10000000)
    tc.reset()
    return tc


@pytest.fixture
def market_agent(llm):
    return MarketInsightAgent(llm=llm)


@pytest.fixture
def copy_agent(llm):
    return CopywriterAgent(llm=llm, brand_profile="tech_lifestyle")


@pytest.fixture
def cs_agent(llm):
    rag = RAGEngine()
    erp = ERPConnector()
    return CustomerServiceAgent(llm=llm, rag_engine=rag, erp_connector=erp)


@pytest.fixture
def orchestrator(market_agent, copy_agent, cs_agent):
    return Orchestrator(
        market_insight_agent=market_agent,
        copywriter_agent=copy_agent,
        customer_service_agent=cs_agent
    )


class TestMarketInsightAgent:
    """Test Market Insight Agent functionality."""
    
    @pytest.mark.asyncio
    async def test_review_analysis(self, market_agent):
        result = await market_agent.analyze_reviews(
            product_category="wireless earbuds",
            platforms=["amazon"],
            max_reviews=10
        )
        
        assert "pain_points" in result
        assert "sentiment_summary" in result
        assert "opportunities" in result
        assert result["total_reviews_analyzed"] <= 10
        assert len(result["pain_points"]) > 0
    
    @pytest.mark.asyncio
    async def test_pain_point_structure(self, market_agent):
        result = await market_agent.analyze_reviews("test", ["amazon"], 5)
        
        for pp in result["pain_points"]:
            assert "category" in pp
            assert "severity" in pp
            assert isinstance(pp["severity"], (int, float))
            assert 1 <= pp["severity"] <= 10


class TestCopywriterAgent:
    """Test Copywriter Agent functionality."""
    
    @pytest.mark.asyncio
    async def test_copy_generation(self, copy_agent):
        pain_points = [
            {"category": "Battery", "severity": 8, "description": "Short battery life"},
            {"category": "Fit", "severity": 7, "description": "Falls out during exercise"}
        ]
        
        result = await copy_agent.generate_copy(
            pain_points=pain_points,
            target_market="Southeast Asia",
            languages=["en", "th"],
            rounds=2
        )
        
        assert "final_copy" in result
        assert "localized_versions" in result
        assert len(result["refinement_history"]) >= 2
        assert "en" in result["localized_versions"]
    
    @pytest.mark.asyncio
    async def test_refinement_improves_copy(self, copy_agent):
        pain_points = [{"category": "Test", "severity": 5, "description": "Test issue"}]
        
        result = await copy_agent.generate_copy(
            pain_points=pain_points,
            target_market="Test",
            languages=["en"],
            rounds=3
        )
        
        # Verify refinement history grows
        assert len(result["refinement_history"]) == 3


class TestCustomerServiceAgent:
    """Test Customer Service Agent functionality."""
    
    @pytest.mark.asyncio
    async def test_query_handling(self, cs_agent):
        result = await cs_agent.handle_query(
            query="How long does the battery last?",
            language="en"
        )
        
        assert "response" in result
        assert "detected_intent" in result
        assert len(result["response"]) > 10
    
    @pytest.mark.asyncio
    async def test_multilingual_support(self, cs_agent):
        languages = ["en", "th", "id", "vi"]
        
        for lang in languages:
            result = await cs_agent.handle_query(
                query="Test query about shipping",
                language=lang
            )
            assert result["language"] == lang
            assert result["response"]  # Non-empty response
    
    @pytest.mark.asyncio
    async def test_intent_detection(self, cs_agent):
        # Shipping intent
        result = await cs_agent.handle_query("When will my order arrive?", "en")
        assert result["detected_intent"] in ["shipping", "order_status"]
        
        # Pricing intent
        result = await cs_agent.handle_query("How much does this cost?", "en")
        assert result["detected_intent"] == "pricing"
        
        # Product inquiry
        result = await cs_agent.handle_query("What's the battery capacity?", "en")
        assert result["detected_intent"] == "product_inquiry"


class TestOrchestrator:
    """Test Orchestrator coordination."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self, orchestrator):
        result = await orchestrator.run_full_marketing_pipeline(
            product_category="wireless earbuds",
            target_market="Southeast Asia",
            languages=["en", "th"],
            platforms=["amazon"],
            refinement_rounds=2
        )
        
        assert result["status"] == "completed"
        assert "market_insights" in result
        assert "generated_copy" in result
        assert "token_usage" in result
    
    @pytest.mark.asyncio
    async def test_customer_inquiry(self, orchestrator):
        result = await orchestrator.handle_customer_inquiry(
            query="What is the return policy?",
            language="en"
        )
        
        assert "response" in result
        assert "detected_intent" in result


class TestTokenCounter:
    """Test token counting functionality."""
    
    def test_token_counting(self):
        tc = TokenCounter()
        tc.reset()
        
        tokens = tc.record("TestAgent", "This is a test message for counting.")
        assert tokens > 0
    
    def test_daily_summary(self):
        tc = TokenCounter(daily_limit=10000)
        tc.reset()
        
        tc.record("Agent1", "Test message one two three")
        tc.record("Agent2", "Another test message here")
        
        summary = tc.get_daily_summary()
        assert summary["total_tokens"] > 0
        assert "Agent1" in summary["by_agent"]
        assert "Agent2" in summary["by_agent"]
    
    def test_cost_estimation(self):
        tc = TokenCounter(daily_limit=1000000)
        tc.reset()
        
        tc.record("Agent1", "Test " * 1000)  # Generate significant tokens
        
        cost = tc.estimate_cost("gpt-4o-mini")
        assert "estimated_cost_usd" in cost
        assert isinstance(cost["estimated_cost_usd"], float)
