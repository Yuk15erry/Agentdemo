"""Sample data loader for demo mode."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent


def load_sample_data() -> dict:
    """Load all sample data for the demo."""
    data = {
        "faq_documents": [],
        "brand_profiles": {},
        "sample_reviews": []
    }
    
    # Load FAQ documents
    faq_path = DATA_DIR / "faq_data.json"
    if faq_path.exists():
        with open(faq_path, "r", encoding="utf-8") as f:
            faq_data = json.load(f)
            data["faq_documents"] = faq_data.get("documents", [])
    
    # Load brand profiles
    brand_path = DATA_DIR / "brand_profiles.json"
    if brand_path.exists():
        with open(brand_path, "r", encoding="utf-8") as f:
            data["brand_profiles"] = json.load(f)
    
    # Load sample reviews
    reviews_path = DATA_DIR / "sample_reviews.json"
    if reviews_path.exists():
        with open(reviews_path, "r", encoding="utf-8") as f:
            data["sample_reviews"] = json.load(f)
    
    return data
