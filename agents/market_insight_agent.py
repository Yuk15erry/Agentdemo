"""
Market Insight Agent — Scrapes competitor reviews, performs long-text analysis,
and extracts actionable pain points for product positioning.
"""
import json
from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger("MarketInsightAgent")


class MarketInsightAgent(BaseAgent):
    """
    Analyzes competitor product reviews to extract:
    - Customer pain points
    - Sentiment trends
    - Feature requests
    - Competitive gaps
    """
    
    def __init__(self, llm=None):
        super().__init__(name="MarketInsightAgent", llm=llm)
        self.reviews_cache: List[Dict] = []
        
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute market insight extraction."""
        product_category = kwargs.get("product_category", "wireless earbuds")
        platforms = kwargs.get("platforms", ["amazon", "shopee"])
        max_reviews = kwargs.get("max_reviews", 200)
        
        return await self.analyze_reviews(product_category, platforms, max_reviews)
    
    async def analyze_reviews(
        self, 
        product_category: str, 
        platforms: List[str] = None,
        max_reviews: int = 200
    ) -> Dict[str, Any]:
        """
        Full analysis pipeline: scrape → analyze → extract insights.
        """
        platforms = platforms or ["amazon"]
        
        logger.info(f"Starting review analysis for '{product_category}' across {platforms}")
        
        # Step 1: Simulate review scraping
        reviews = await self._scrape_reviews(product_category, platforms, max_reviews)
        self.reviews_cache = reviews
        self._record_tokens(json.dumps(reviews), operation="scrape_reviews")
        
        # Step 2: Long-text sentiment analysis
        sentiment = await self._analyze_sentiment(reviews)
        self._record_tokens(json.dumps(sentiment), operation="sentiment_analysis")
        
        # Step 3: Pain point extraction
        pain_points = await self._extract_pain_points(reviews, sentiment)
        self._record_tokens(json.dumps(pain_points), operation="pain_point_extraction")
        
        # Step 4: Generate opportunities
        opportunities = await self._identify_opportunities(pain_points, product_category)
        self._record_tokens(json.dumps(opportunities), operation="opportunity_analysis")
        
        result = {
            "product_category": product_category,
            "platforms": platforms,
            "total_reviews_analyzed": len(reviews),
            "sentiment_summary": sentiment,
            "pain_points": pain_points,
            "opportunities": opportunities,
            "recommended_actions": self._generate_actions(pain_points, opportunities)
        }
        
        logger.info(f"Analysis complete: {len(pain_points)} pain points found")
        return result
    
    async def _scrape_reviews(self, category: str, platforms: List[str], max_count: int) -> List[Dict]:
        """Simulate scraping reviews from multiple platforms."""
        # In production, this would use real scraping APIs
        sample_reviews = self._load_sample_reviews(category)
        
        # Simulate platform-specific data
        reviews = []
        for i, review in enumerate(sample_reviews[:max_count]):
            reviews.append({
                "id": f"rev_{i}",
                "platform": platforms[i % len(platforms)],
                "rating": review.get("rating", 3),
                "title": review.get("title", ""),
                "content": review.get("content", ""),
                "language": review.get("language", "en"),
                "verified_purchase": review.get("verified", True),
                "date": review.get("date", "2024-01-15"),
                "helpful_count": review.get("helpful", 0)
            })
        
        logger.info(f"Scraped {len(reviews)} reviews from {len(platforms)} platforms")
        return reviews
    
    async def _analyze_sentiment(self, reviews: List[Dict]) -> Dict:
        """Long-text sentiment analysis across all reviews."""
        # Simulate LLM-powered sentiment analysis
        total = len(reviews)
        positive = sum(1 for r in reviews if r["rating"] >= 4)
        neutral = sum(1 for r in reviews if r["rating"] == 3)
        negative = sum(1 for r in reviews if r["rating"] <= 2)
        
        prompt = f"""Analyze sentiment for {total} product reviews.
        Positive reviews: {positive}
        Neutral reviews: {neutral}  
        Negative reviews: {negative}
        
        Extract key sentiment themes and emotional drivers."""
        
        llm_response = await self._llm_call(prompt, "You are a market analyst specializing in ecommerce review analysis.")
        
        return {
            "distribution": {
                "positive": round(positive / total * 100, 1),
                "neutral": round(neutral / total * 100, 1),
                "negative": round(negative / total * 100, 1)
            },
            "average_rating": round(sum(r["rating"] for r in reviews) / total, 2),
            "key_themes": llm_response,
            "total_analyzed": total
        }
    
    async def _extract_pain_points(self, reviews: List[Dict], sentiment: Dict) -> List[Dict]:
        """Extract specific pain points from negative and neutral reviews."""
        negative_reviews = [r for r in reviews if r["rating"] <= 3]
        
        prompt = f"""From {len(negative_reviews)} critical reviews, extract the TOP 5 customer pain points.
        Reviews: {json.dumps(negative_reviews[:50], indent=2)}
        
        For each pain point provide:
        1. Category (e.g., battery, comfort, connectivity)
        2. Severity (1-10)
        3. Frequency (how many reviews mention it)
        4. Customer quotes
        5. Business impact"""
        
        llm_response = await self._llm_call(prompt, "Extract structured pain points from customer reviews.")
        
        # Parse simulated response into structured format
        pain_points = [
            {
                "category": "Battery Life",
                "severity": 8,
                "frequency": "42% of negative reviews",
                "description": "Battery drains faster than advertised during calls",
                "customer_quote": "Says 8 hours but barely lasts 4 on a call",
                "business_impact": "High return rate, trust erosion",
                "sentiment_intensity": -0.72
            },
            {
                "category": "Comfort & Fit",
                "severity": 7,
                "frequency": "35% of negative reviews",
                "description": "Earbuds fall out during exercise, cause ear fatigue",
                "customer_quote": "Can't use them for running, always slipping out",
                "business_impact": "Lost fitness segment market share",
                "sentiment_intensity": -0.65
            },
            {
                "category": "Connectivity",
                "severity": 6,
                "frequency": "28% of negative reviews",
                "description": "Bluetooth drops connection when phone is in pocket",
                "customer_quote": "Constant disconnects when walking outside",
                "business_impact": "Negative app store reviews",
                "sentiment_intensity": -0.58
            },
            {
                "category": "Sound Quality",
                "severity": 5,
                "frequency": "22% of negative reviews",
                "description": "Bass is weak, sound leaks at high volume",
                "customer_quote": "My old $20 buds sound better than these",
                "business_impact": "Unfavorable comparisons to competitors",
                "sentiment_intensity": -0.45
            },
            {
                "category": "Charging Case",
                "severity": 4,
                "frequency": "18% of negative reviews",
                "description": "Case hinge feels flimsy, doesn't charge consistently",
                "customer_quote": "Case stopped working after 2 months",
                "business_impact": "Warranty claims increasing",
                "sentiment_intensity": -0.40
            }
        ]
        
        return pain_points
    
    async def _identify_opportunities(self, pain_points: List[Dict], category: str) -> List[Dict]:
        """Identify market opportunities based on competitor weaknesses."""
        prompt = f"""Based on these pain points in the {category} market:
        {json.dumps(pain_points, indent=2)}
        
        Identify 3-5 specific opportunities for a new entrant."""
        
        await self._llm_call(prompt, "You are a product strategist.")
        
        return [
            {
                "opportunity": "Long-battery sports earbuds",
                "gap": "No competitor offers reliable 10+ hour battery for active users",
                "target_segment": "Fitness enthusiasts aged 25-40",
                "estimated_market_size": "$2.3B in SEA",
                "difficulty": "Medium"
            },
            {
                "opportunity": "Secure-fit design patent",
                "gap": "Universal complaint about fit during movement",
                "target_segment": "All active users",
                "estimated_market_size": "Cross-segment",
                "difficulty": "High (R&D required)"
            },
            {
                "opportunity": "Premium connectivity chip",
                "gap": "Bluetooth stability issues across brands",
                "target_segment": "Urban professionals",
                "estimated_market_size": "$1.8B",
                "difficulty": "Medium"
            }
        ]
    
    def _generate_actions(self, pain_points: List[Dict], opportunities: List[Dict]) -> List[str]:
        """Generate recommended actions."""
        return [
            "Prioritize battery optimization in next product iteration",
            "Develop marketing copy highlighting 'secure-fit' design",
            "Partner with Qualcomm for advanced Bluetooth chip integration",
            "Create comparison content addressing top 3 pain points vs competitors",
            "Launch 'try-for-30-days' program to build fit confidence"
        ]
    
    def _load_sample_reviews(self, category: str) -> List[Dict]:
        """Load sample review data."""
        # In production, this would be real scraped data
        return [
            {"rating": 2, "title": "Battery dies too fast", "content": "Advertised 8 hours but I get maybe 3-4. Very disappointing for the price.", "language": "en", "verified": True, "date": "2024-03-15", "helpful": 127},
            {"rating": 1, "title": "Keeps falling out", "content": "These are unusable for running. They slip out every 5 minutes no matter which tip size I use.", "language": "en", "verified": True, "date": "2024-03-14", "helpful": 89},
            {"rating": 5, "title": "Great sound quality!", "content": "Best earbuds I've owned. The noise cancellation is incredible for the price point.", "language": "en", "verified": True, "date": "2024-03-13", "helpful": 56},
            {"rating": 3, "title": "OK but connection drops", "content": "Sound is decent but Bluetooth keeps cutting out when my phone is in my pocket. Frustrating.", "language": "en", "verified": True, "date": "2024-03-12", "helpful": 45},
            {"rating": 1, "title": "Case broke after 2 months", "content": "The charging case hinge snapped. Now it won't close properly and doesn't charge the buds.", "language": "en", "verified": True, "date": "2024-03-11", "helpful": 78},
            {"rating": 2, "title": "Weak bass", "content": "For $100+ I expected much better bass. My old $30 pair has deeper sound. Returning these.", "language": "en", "verified": True, "date": "2024-03-10", "helpful": 34},
            {"rating": 4, "title": "Good for calls", "content": "Call quality is excellent. People say I sound crystal clear. Music is decent too.", "language": "en", "verified": True, "date": "2024-03-09", "helpful": 22},
            {"rating": 2, "title": "Ear pain after 1 hour", "content": "These hurt my ears after about an hour of use. The shape is just not ergonomic.", "language": "en", "verified": False, "date": "2024-03-08", "helpful": 67},
            {"rating": 5, "title": "Best budget premium buds", "content": "Can't believe these are under $80. Beats my friend's $200 Sony pair in comfort.", "language": "en", "verified": True, "date": "2024-03-07", "helpful": 91},
            {"rating": 3, "title": "Average overall", "content": "Nothing special. They work fine but don't stand out. Expected more from the hype.", "language": "en", "verified": True, "date": "2024-03-06", "helpful": 15},
            {"rating": 1, "title": "ไม่คุ้มค่าเลย (Not worth it)", "content": "เสียงไม่ดี แบตหมดเร็วมาก ไม่แนะนำให้ซื้อ", "language": "th", "verified": True, "date": "2024-03-05", "helpful": 44},
            {"rating": 2, "title": "Conexión terrible", "content": "La conexión Bluetooth se cae constantemente. Muy frustrante para el precio.", "language": "es", "verified": True, "date": "2024-03-04", "helpful": 33},
        ]
