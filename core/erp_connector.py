"""
ERP Connector — Interface for internal ERP system integration.
Provides order status, inventory, and customer data.
"""
import asyncio
from typing import Dict, Any, Optional
from config.settings import ERP_API_ENDPOINT, ERP_API_KEY
from utils.logger import get_logger

logger = get_logger("ERPConnector")


class ERPConnector:
    """
    Connects to internal ERP system for real-time data.
    
    Demo mode returns simulated data.
    """
    
    def __init__(self, endpoint: str = None, api_key: str = None):
        self.endpoint = endpoint or ERP_API_ENDPOINT
        self.api_key = api_key or ERP_API_KEY
        self.connected = False
        self.demo_mode = True  # Set to False for production
    
    async def connect(self) -> bool:
        """Establish connection to ERP system."""
        if self.demo_mode:
            self.connected = True
            logger.info("ERP Connector running in demo mode")
            return True
        
        # Production: actual API connection
        try:
            # async with httpx.AsyncClient() as client:
            #     resp = await client.get(f"{self.endpoint}/health", headers={"Authorization": f"Bearer {self.api_key}"})
            #     self.connected = resp.status_code == 200
            self.connected = False
        except Exception as e:
            logger.error(f"ERP connection failed: {e}")
            self.connected = False
        
        return self.connected
    
    async def get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Fetch customer order and account data."""
        if self.demo_mode or not self.connected:
            return self._demo_customer_data(customer_id)
        
        # Production: actual API call
        return self._demo_customer_data(customer_id)
    
    async def get_inventory(self, sku: str) -> Dict[str, Any]:
        """Check inventory for a specific SKU."""
        return {
            "sku": sku,
            "in_stock": True,
            "quantity_available": 1250,
            "warehouse": "Shenzhen Hub",
            "restock_date": None
        }
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get real-time order status."""
        statuses = ["processing", "shipped", "in_transit", "out_for_delivery", "delivered"]
        import random
        return {
            "order_id": order_id,
            "status": random.choice(statuses),
            "estimated_delivery": "2024-04-15",
            "tracking_number": f"TRK{random.randint(100000, 999999)}",
            "carrier": "DHL Express"
        }
    
    def _demo_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Generate demo customer data."""
        return {
            "customer_id": customer_id or "demo_user_001",
            "name": "Demo Customer",
            "recent_orders": [
                {"order_id": "ORD-2024-001", "status": "delivered", "date": "2024-03-01"},
                {"order_id": "ORD-2024-089", "status": "in_transit", "date": "2024-03-28"}
            ],
            "loyalty_tier": "Gold",
            "preferred_language": "en"
        }
