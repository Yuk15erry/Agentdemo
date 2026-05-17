"""
Orchestrator — Coordinates the three agents for end-to-end workflows.
"""
import asyncio
from typing import Dict, Any, List, Optional
from utils.token_counter import token_counter
from utils.logger import get_logger

logger = get_logger("Orchestrator")


class Orchestrator:
    """
    Coordinates Market Insight, Copywriter, and Customer Service agents.
    
    Supports workflows:
    1. Full pipeline: Market analysis → Copy generation
    2. Customer inquiry handling
    3. Token usage monitoring across all agents
    """
    
    def __init__(
        self,
        market_insight_agent=None,
        copywriter_agent=None,
        customer_service_agent=None
    ):
        self.market_insight = market_insight_agent
        self.copywriter = copywriter_agent
        self.customer_service = customer_service_agent
        self.workflow_history: List[Dict] = []
    
    async def run_full_marketing_pipeline(
        self,
        product_category: str,
        target_market: str,
        languages: List[str],
        platforms: List[str] = None,
        refinement_rounds: int = 3
    ) -> Dict[str, Any]:
        """
        End-to-end pipeline: Market Insight → Copy Generation.
        
        Steps:
        1. Analyze competitor reviews
        2. Extract pain points
        3. Generate and refine copy
        4. Localize for target languages
        """
        logger.info(f"Starting full pipeline for '{product_category}' → {target_market}")
        
        workflow = {
            "workflow_id": f"wf_{len(self.workflow_history) + 1}",
            "product_category": product_category,
            "target_market": target_market,
            "start_time": __import__('datetime').datetime.now().isoformat()
        }
        
        # Step 1: Market Insight
        logger.info("Step 1/2: Running Market Insight Agent...")
        market_insights = await self.market_insight.analyze_reviews(
            product_category=product_category,
            platforms=platforms or ["amazon", "shopee"],
            max_reviews=200
        )
        workflow["market_insights"] = market_insights
        
        # Step 2: Copy Generation
        logger.info("Step 2/2: Running Copywriter Agent...")
        copy_result = await self.copywriter.generate_copy(
            pain_points=market_insights.get("pain_points", []),
            target_market=target_market,
            languages=languages,
            rounds=refinement_rounds
        )
        workflow["copy_result"] = copy_result
        
        # Get token summary
        token_summary = token_counter.get_daily_summary()
        workflow["token_usage"] = token_summary
        workflow["end_time"] = __import__('datetime').datetime.now().isoformat()
        
        self.workflow_history.append(workflow)
        
        logger.info(f"Pipeline complete. Tokens used: {token_summary['total_tokens']:,}")
        
        return {
            "status": "completed",
            "workflow_id": workflow["workflow_id"],
            "market_insights": market_insights,
            "generated_copy": copy_result,
            "token_usage": token_summary,
            "recommendations": market_insights.get("recommended_actions", [])
        }
    
    async def handle_customer_inquiry(
        self,
        query: str,
        language: str = "en",
        customer_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Handle a single customer inquiry."""
        logger.info(f"Handling inquiry in {language}")
        
        result = await self.customer_service.handle_query(
            query=query,
            language=language,
            customer_context=customer_context
        )
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "agents": {
                "market_insight": self.market_insight.get_status() if self.market_insight else None,
                "copywriter": self.copywriter.get_status() if self.copywriter else None,
                "customer_service": self.customer_service.get_status() if self.customer_service else None
            },
            "token_usage": token_counter.get_daily_summary(),
            "cost_estimate": token_counter.estimate_cost(),
            "workflows_completed": len(self.workflow_history)
        }
