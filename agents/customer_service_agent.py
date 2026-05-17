"""
Customer Service Agent — RAG-powered multilingual inquiry handling
with ERP integration for order-aware responses.
"""
import json
from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger("CustomerServiceAgent")


class CustomerServiceAgent(BaseAgent):
    """
    Handles customer inquiries in multiple languages using:
    - RAG (Retrieval-Augmented Generation) for product knowledge
    - ERP connector for order status, inventory, shipping
    - Persona-based responses for higher conversion
    """
    
    def __init__(self, llm=None, rag_engine=None, erp_connector=None):
        super().__init__(name="CustomerServiceAgent", llm=llm)
        self.rag_engine = rag_engine
        self.erp_connector = erp_connector
        self.conversation_history: List[Dict] = []
        self.persona = "friendly_expert"
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Handle a customer inquiry."""
        query = kwargs.get("query", "")
        language = kwargs.get("language", "en")
        customer_context = kwargs.get("customer_context", {})
        
        return await self.handle_query(query, language, customer_context)
    
    async def handle_query(
        self,
        query: str,
        language: str = "en",
        customer_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process customer query through RAG + ERP pipeline.
        
        Pipeline:
        1. Detect language and intent
        2. Retrieve relevant product knowledge (RAG)
        3. Fetch order/account data (ERP)
        4. Generate personalized response
        5. Include upsell if appropriate
        """
        customer_context = customer_context or {}
        
        logger.info(f"Handling query in {language}: '{query[:100]}...'")
        
        # Step 1: Intent detection
        intent = await self._detect_intent(query, language)
        self._record_tokens(query, operation="intent_detection")
        
        # Step 2: RAG retrieval
        rag_results = await self._retrieve_knowledge(query, intent) if self.rag_engine else []
        self._record_tokens(json.dumps(rag_results), operation="rag_retrieval")
        
        # Step 3: ERP data fetch
        erp_data = await self._fetch_erp_data(customer_context) if self.erp_connector else {}
        self._record_tokens(json.dumps(erp_data), operation="erp_fetch")
        
        # Step 4: Generate response
        response = await self._generate_response(query, intent, rag_results, erp_data, language)
        self._record_tokens(response, operation="response_generation")
        
        # Step 5: Conversion optimization
        if intent in ["product_inquiry", "shipping", "pricing"]:
            response = await self._add_conversion_elements(response, intent, language)
            self._record_tokens(response, operation="conversion_optimization")
        
        # Store conversation
        self.conversation_history.append({
            "query": query,
            "language": language,
            "intent": intent,
            "response": response,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
        result = {
            "query": query,
            "language": language,
            "detected_intent": intent,
            "response": response,
            "rag_sources": [r.get("source", "") for r in rag_results],
            "erp_context_used": bool(erp_data),
            "conversion_elements_added": intent in ["product_inquiry", "shipping", "pricing"]
        }
        
        logger.info(f"Response generated for intent: {intent}")
        return result
    
    async def _detect_intent(self, query: str, language: str) -> str:
        """Detect customer intent from query."""
        prompt = f"""Classify this customer query into one intent:
        Query ({language}): "{query}"
        
        Options: product_inquiry, shipping, pricing, complaint, technical_support, order_status, return_request, general"""
        
        await self._llm_call(prompt, "Classify customer service intents.")
        
        # Simple keyword-based classification as fallback
        query_lower = query.lower()
        if any(w in query_lower for w in ["ship", "deliver", "track", "ส่ง", "배송"]):
            return "shipping"
        elif any(w in query_lower for w in ["price", "cost", "discount", "ราคา", "가격"]):
            return "pricing"
        elif any(w in query_lower for w in ["battery", "sound", "connect", "fit", "quality", "spec"]):
            return "product_inquiry"
        elif any(w in query_lower for w in ["return", "refund", "คืน", "환불"]):
            return "return_request"
        elif any(w in query_lower for w in ["order", "status", "คำสั่ง", "주문"]):
            return "order_status"
        elif any(w in query_lower for w in ["broken", "not work", "issue", "problem", "เสีย", "문제"]):
            return "technical_support"
        return "general"
    
    async def _retrieve_knowledge(self, query: str, intent: str) -> List[Dict]:
        """Retrieve relevant product knowledge using RAG."""
        if not self.rag_engine:
            # Return simulated knowledge
            return [
                {"source": "product_specs", "content": "Battery: 12hr continuous, 50hr with case. Bluetooth 5.3, IPX6 waterproof.", "relevance": 0.95},
                {"source": "faq_shipping", "content": "Free shipping to SEA countries. Delivery: 3-7 business days. Express: 1-3 days.", "relevance": 0.82},
                {"source": "faq_returns", "content": "30-day no-questions-asked return policy. Free return shipping label provided.", "relevance": 0.78}
            ]
        return await self.rag_engine.search(query, top_k=5)
    
    async def _fetch_erp_data(self, context: Dict) -> Dict:
        """Fetch order/inventory data from ERP system."""
        if not self.erp_connector:
            return {"order_status": "N/A (demo mode)", "inventory": "In stock"}
        return await self.erp_connector.get_customer_data(context.get("customer_id", ""))
    
    async def _generate_response(
        self, query: str, intent: str, rag: List[Dict], erp: Dict, language: str
    ) -> str:
        """Generate natural, helpful response in target language."""
        rag_context = "\n".join([r.get("content", "") for r in rag[:3]])
        
        prompt = f"""Customer query ({language}): "{query}"
        Intent: {intent}
        Product knowledge: {rag_context}
        Order info: {json.dumps(erp)}
        
        Generate a helpful, warm response in {language}. 
        Be conversational and human-like. Include relevant details from product knowledge.
        Keep it concise but thorough."""
        
        await self._llm_call(prompt, f"You are a helpful customer service agent. Respond in {language}.")
        
        # Simulate responses based on language
        responses = {
            "en": {
                "product_inquiry": "Great question! Our earbuds feature a 12-hour battery life (50 hours with the charging case), so they'll easily last through your longest days. They're also IPX6 water-resistant — perfect for workouts! The SecureFit™ design means they stay put no matter how much you move. Would you like me to share some customer reviews? 🎧",
                "shipping": "We offer free standard shipping to most countries! Delivery typically takes 3-7 business days. Need it faster? Express shipping (1-3 days) is available for a small fee. I can check your order status if you share your order number! 📦",
                "pricing": "Our earbuds are priced at $79.99, which includes free shipping and a 30-day money-back guarantee. We're actually running a promotion right now — use code WELCOME10 for 10% off your first order! Want me to help you place an order? ✨",
                "general": "Thanks for reaching out! I'm here to help with any questions about our products, shipping, or your order. What can I assist you with today? 😊"
            },
            "th": {
                "product_inquiry": "คำถามดีมากครับ! หูฟังของเราใช้งานได้ต่อเนื่อง 12 ชั่วโมง (50 ชั่วโมงพร้อมเคสชาร์จ) กันน้ำระดับ IPX6 เหมาะสำหรับการออกกำลังกายมากๆ ดีไซน์ SecureFit™ ช่วยให้กระชับไม่หลุดง่าย สนใจให้ผมส่งรีวิวจากลูกค้าให้ดูไหมครับ? 🎧",
                "shipping": "เรามีบริการจัดส่งฟรีถึงประเทศไทยครับ ใช้เวลาประมาณ 5-10 วันทำการ ถ้าต้องการด่วนมีบริการแบบ Express 3-5 วันครับ แจ้งหมายเลขคำสั่งซื้อมาได้เลย จะเช็คสถานะให้ครับ 📦",
                "pricing": "ราคาอยู่ที่ $79.99 หรือประมาณ 2,900 บาท รวมค่าจัดส่งฟรีและรับประกันคืนเงิน 30 วันครับ ตอนนี้มีโปรโมชั่นใช้โค้ด WELCOME10 ลด 10% สำหรับออเดอร์แรก สนใจสั่งซื้อเลยไหมครับ? ✨",
                "general": "ขอบคุณที่ติดต่อมาครับ! ผมยินดีช่วยเหลือทุกคำถามเกี่ยวกับสินค้า การจัดส่ง หรือคำสั่งซื้อ มีอะไรให้ช่วยไหมครับ? 😊"
            }
        }
        
        default = responses.get("en", responses["en"])
        lang_responses = responses.get(language, default)
        return lang_responses.get(intent, lang_responses.get("general", "How can I help you today? 😊"))
    
    async def _add_conversion_elements(self, response: str, intent: str, language: str) -> str:
        """Add subtle conversion elements to response."""
        conversion_phrases = {
            "en": "\n\nBy the way — we're offering free returns for 30 days, so you can try them completely risk-free! 😊",
            "th": "\n\nอ้อ — เรามีนโยบายคืนสินค้าฟรีภายใน 30 วัน ลองใช้ได้แบบไม่ต้องกังวลเลยครับ! 😊",
            "id": "\n\nOmong-omong — kami menawarkan pengembalian gratis 30 hari, jadi bisa dicoba tanpa risiko! 😊",
            "vi": "\n\nÀ này — chúng tôi có chính sách đổi trả miễn phí 30 ngày, bạn cứ yên tâm dùng thử nhé! 😊"
        }
        
        suffix = conversion_phrases.get(language, conversion_phrases["en"])
        return response + suffix
    
    def get_conversation_stats(self) -> Dict:
        """Get statistics about handled conversations."""
        intents = {}
        for conv in self.conversation_history:
            intent = conv.get("intent", "unknown")
            intents[intent] = intents.get(intent, 0) + 1
        
        return {
            "total_conversations": len(self.conversation_history),
            "intent_distribution": intents,
            "languages_served": list(set(c.get("language") for c in self.conversation_history))
        }
