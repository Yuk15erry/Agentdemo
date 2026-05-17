"""
Streamlit Demo — Interactive UI for the Cross-Border Ecommerce AI System.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from datetime import datetime

# Import system components
from agents.market_insight_agent import MarketInsightAgent
from agents.copywriter_agent import CopywriterAgent
from agents.customer_service_agent import CustomerServiceAgent
from core.orchestrator import Orchestrator
from core.llm_simulator import LLMSimulator
from core.rag_engine import RAGEngine
from core.erp_connector import ERPConnector
from utils.token_counter import token_counter
from data import load_sample_data

# Page config
st.set_page_config(
    page_title="Cross-Border Ecommerce AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1A1A2E; margin-bottom: 1rem; }
    .agent-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   border-radius: 12px; padding: 1.5rem; color: white; margin: 0.5rem 0; }
    .metric-big { font-size: 2rem; font-weight: 700; }
    .token-alert { background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; border-radius: 8px; }
    .copy-box { background: #f8f9fa; border-radius: 8px; padding: 1.5rem; border: 1px solid #dee2e6; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the full system with all agents."""
    llm = LLMSimulator()
    rag = RAGEngine()
    erp = ERPConnector()
    
    # Load sample documents into RAG
    sample_data = load_sample_data()
    rag.load_documents(sample_data.get("faq_documents", []))
    
    market_agent = MarketInsightAgent(llm=llm)
    copy_agent = CopywriterAgent(llm=llm, brand_profile="tech_lifestyle")
    cs_agent = CustomerServiceAgent(llm=llm, rag_engine=rag, erp_connector=erp)
    
    orchestrator = Orchestrator(
        market_insight_agent=market_agent,
        copywriter_agent=copy_agent,
        customer_service_agent=cs_agent
    )
    
    return orchestrator, llm, rag


async def run_market_analysis(orchestrator, category, market, platforms):
    """Run market insight analysis."""
    with st.spinner("🔍 Analyzing competitor reviews..."):
        result = await orchestrator.market_insight.analyze_reviews(
            product_category=category,
            platforms=platforms,
            max_reviews=200
        )
    return result


async def run_copy_generation(orchestrator, pain_points, market, languages, rounds):
    """Run copy generation with refinement."""
    with st.spinner("✍️ Generating and refining copy..."):
        result = await orchestrator.copywriter.generate_copy(
            pain_points=pain_points,
            target_market=market,
            languages=languages,
            rounds=rounds
        )
    return result


async def run_customer_query(orchestrator, query, language):
    """Handle customer inquiry."""
    with st.spinner("🤖 Processing inquiry..."):
        result = await orchestrator.customer_service.handle_query(
            query=query,
            language=language
        )
    return result


def main():
    st.markdown('<div class="main-header">🌍 Cross-Border Ecommerce AI</div>', unsafe_allow_html=True)
    st.markdown("**Multi-Agent Marketing & Customer Service System** | Demo Mode")
    
    # Initialize
    orchestrator, llm, rag = initialize_system()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        st.markdown("### 🎯 Product Settings")
        product_category = st.selectbox(
            "Product Category",
            ["wireless earbuds", "smart watch", "bluetooth speaker", "power bank", "phone case"]
        )
        target_market = st.selectbox(
            "Target Market",
            ["Southeast Asia", "Latin America", "Middle East", "Europe", "North America"]
        )
        platforms = st.multiselect(
            "Competitor Platforms",
            ["amazon", "shopee", "lazada", "tokopedia", "aliexpress"],
            default=["amazon", "shopee", "lazada"]
        )
        
        st.markdown("### 🌐 Languages")
        languages = st.multiselect(
            "Target Languages",
            ["en", "th", "id", "vi", "zh", "ja", "ko", "es", "ar"],
            default=["en", "th", "id", "vi"]
        )
        
        st.markdown("### 🔄 Refinement")
        refinement_rounds = st.slider("Copy Refinement Rounds", 1, 5, 3)
        
        st.markdown("---")
        st.markdown("### 📊 Live Token Monitor")
        token_summary = token_counter.get_daily_summary()
        st.metric("Tokens Used Today", f"{token_summary['total_tokens']:,}")
        st.metric("Daily Limit", f"{token_summary['daily_limit']:,}")
        if token_summary['usage_percent'] > 0:
            st.progress(min(token_summary['usage_percent'] / 100, 1.0))
            st.caption(f"{token_summary['usage_percent']}% of daily limit")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Market Insights", 
        "✍️ Copy Generation", 
        "🤖 Customer Service",
        "📊 System Monitor"
    ])
    
    # Tab 1: Market Insights
    with tab1:
        st.markdown("## 🔍 Market Insight Agent")
        st.markdown("Analyze competitor reviews to extract pain points and opportunities.")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🚀 Run Market Analysis", type="primary", use_container_width=True):
                result = asyncio.run(run_market_analysis(
                    orchestrator, product_category, target_market, platforms
                ))
                st.session_state["market_result"] = result
        
        if "market_result" in st.session_state:
            result = st.session_state["market_result"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Reviews Analyzed", result["total_reviews_analyzed"])
            with col2:
                avg_rating = result["sentiment_summary"]["average_rating"]
                st.metric("Avg Rating", f"{avg_rating}/5")
            with col3:
                st.metric("Pain Points Found", len(result["pain_points"]))
            
            st.markdown("### 🎯 Top Pain Points")
            pain_df = pd.DataFrame(result["pain_points"])
            st.dataframe(
                pain_df[["category", "severity", "frequency", "business_impact"]],
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("### 💡 Opportunities")
            for opp in result.get("opportunities", []):
                with st.expander(f"💎 {opp['opportunity']}"):
                    st.markdown(f"**Gap:** {opp['gap']}")
                    st.markdown(f"**Target:** {opp['target_segment']}")
                    st.markdown(f"**Market Size:** {opp['estimated_market_size']}")
    
    # Tab 2: Copy Generation
    with tab2:
        st.markdown("## ✍️ Copywriter Agent")
        st.markdown("Generate high-conversion copy with multi-round chain-of-thought refinement.")
        
        if st.button("🎨 Generate Copy", type="primary", use_container_width=True):
            pain_points = st.session_state.get("market_result", {}).get("pain_points", [
                {"category": "Battery Life", "severity": 8, "description": "Battery drains too fast"},
                {"category": "Comfort", "severity": 7, "description": "Earbuds fall out during exercise"}
            ])
            
            result = asyncio.run(run_copy_generation(
                orchestrator, pain_points, target_market, languages, refinement_rounds
            ))
            st.session_state["copy_result"] = result
        
        if "copy_result" in st.session_state:
            result = st.session_state["copy_result"]
            final_copy = result.get("final_copy", {})
            
            st.markdown("### 📝 Final Copy (English)")
            st.markdown('<div class="copy-box">', unsafe_allow_html=True)
            
            st.markdown("**Headlines:**")
            for h in final_copy.get("headlines", [])[:5]:
                st.markdown(f"- {h}")
            
            st.markdown("**Body Copy:**")
            st.markdown(f"> {final_copy.get('body_copy', '')}")
            
            st.markdown("**Key Propositions:**")
            for prop in final_copy.get("key_propositions", []):
                st.markdown(f"- ✅ {prop}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Localized versions
            st.markdown("### 🌐 Localized Versions")
            localized = result.get("localized_versions", {})
            cols = st.columns(min(len(localized), 3))
            for i, (lang, copy_data) in enumerate(localized.items()):
                with cols[i % 3]:
                    st.markdown(f"**{lang.upper()}**")
                    st.info(copy_data.get("headline", copy_data.get("body_preview", "")))
            
            # Refinement history
            st.markdown("### 🔄 Refinement Process")
            for ref in result.get("refinement_history", []):
                with st.expander(f"Round {ref['round']}: {ref['stage']}"):
                    if "critique" in ref:
                        st.json(ref["critique"])
    
    # Tab 3: Customer Service
    with tab3:
        st.markdown("## 🤖 Customer Service Agent")
        st.markdown("RAG-powered multilingual customer inquiry handling.")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            customer_query = st.text_area(
                "Customer Query",
                "Does this support fast charging? How long does shipping take to Bangkok?",
                height=100
            )
        with col2:
            query_language = st.selectbox("Language", ["en", "th", "id", "vi", "zh", "ja", "ko", "es"])
        
        if st.button("💬 Handle Inquiry", type="primary", use_container_width=True):
            result = asyncio.run(run_customer_query(
                orchestrator, customer_query, query_language
            ))
            st.session_state["cs_result"] = result
        
        if "cs_result" in st.session_state:
            result = st.session_state["cs_result"]
            
            st.markdown("### 💬 Response")
            st.markdown(f"""
            <div style="background: #e8f5e9; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #4caf50;">
                <strong>Detected Intent:</strong> {result['detected_intent']}<br><br>
                {result['response']}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Intent", result["detected_intent"])
            with col2:
                st.metric("ERP Context", "✅ Used" if result["erp_context_used"] else "❌ Not used")
    
    # Tab 4: System Monitor
    with tab4:
        st.markdown("## 📊 System Monitor")
        
        # Token usage
        token_summary = token_counter.get_daily_summary()
        cost_estimate = token_counter.estimate_cost()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tokens Today", f"{token_summary['total_tokens']:,}")
        with col2:
            st.metric("Daily Limit", f"{token_summary['daily_limit']:,}")
        with col3:
            st.metric("Est. Cost", f"${cost_estimate['estimated_cost_usd']:.2f}")
        
        # Per-agent breakdown
        st.markdown("### 📈 Per-Agent Token Usage")
        by_agent = token_summary.get("by_agent", {})
        if by_agent:
            agent_df = pd.DataFrame([
                {"Agent": k, "Tokens": v, "Percentage": f"{v/token_summary['total_tokens']*100:.1f}%"}
                for k, v in by_agent.items()
            ])
            st.dataframe(agent_df, use_container_width=True, hide_index=True)
        
        # System status
        st.markdown("### 🏗️ System Status")
        status = orchestrator.get_system_status()
        st.json({
            "workflows_completed": status["workflows_completed"],
            "token_usage_percent": f"{token_summary['usage_percent']}%",
            "llm_calls": llm.get_stats(),
            "rag_stats": rag.get_stats()
        })


if __name__ == "__main__":
    main()
