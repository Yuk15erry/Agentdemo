#!/usr/bin/env python3
"""
CLI Demo — Command-line interface for the Cross-Border Ecommerce AI System.
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich import print as rprint

from agents.market_insight_agent import MarketInsightAgent
from agents.copywriter_agent import CopywriterAgent
from agents.customer_service_agent import CustomerServiceAgent
from core.orchestrator import Orchestrator
from core.llm_simulator import LLMSimulator
from core.rag_engine import RAGEngine
from core.erp_connector import ERPConnector
from utils.token_counter import token_counter

console = Console()


async def demo_market_insight(orchestrator):
    """Demo the Market Insight Agent."""
    console.rule("[bold blue]🔍 Market Insight Agent Demo")
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Analyzing competitor reviews...", total=100)
        
        result = await orchestrator.market_insight.analyze_reviews(
            product_category="wireless earbuds",
            platforms=["amazon", "shopee", "lazada"],
            max_reviews=200
        )
        progress.update(task, completed=100)
    
    # Display results
    console.print(f"\n[bold]Analyzed {result['total_reviews_analyzed']} reviews[/bold]")
    console.print(f"Average Rating: {result['sentiment_summary']['average_rating']}/5")
    
    table = Table(title="Top Pain Points")
    table.add_column("Category", style="red")
    table.add_column("Severity", justify="center")
    table.add_column("Frequency")
    table.add_column("Business Impact")
    
    for pp in result["pain_points"]:
        table.add_row(pp["category"], str(pp["severity"]), pp["frequency"], pp["business_impact"])
    
    console.print(table)
    
    return result


async def demo_copywriter(orchestrator, pain_points):
    """Demo the Copywriter Agent."""
    console.rule("[bold green]✍️ Copywriter Agent Demo")
    
    result = await orchestrator.copywriter.generate_copy(
        pain_points=pain_points,
        target_market="Southeast Asia",
        languages=["en", "th", "id", "vi"],
        rounds=3
    )
    
    final_copy = result["final_copy"]
    
    console.print(Panel.fit(
        f"[bold]Headline:[/bold] {final_copy['headlines'][0]}\n\n"
        f"{final_copy['body_copy'][:300]}...",
        title="📝 Final Copy (English)"
    ))
    
    console.print("\n[bold]Localized Versions:[/bold]")
    for lang, copy_data in result["localized_versions"].items():
        console.print(f"  [{lang.upper()}] {copy_data.get('headline', 'N/A')}")
    
    console.print(f"\n[dim]Refinement rounds: {len(result['refinement_history'])}[/dim]")
    
    return result


async def demo_customer_service(orchestrator):
    """Demo the Customer Service Agent."""
    console.rule("[bold yellow]🤖 Customer Service Agent Demo")
    
    test_queries = [
        ("Does this support fast charging?", "en"),
        ("ส่งไปไทยใช้เวลากี่วันครับ", "th"),
        ("Apakah bisa untuk olahraga lari?", "id"),
        ("Pin có dùng được cả ngày không?", "vi"),
    ]
    
    for query, lang in test_queries:
        console.print(f"\n[bold]Customer ({lang}):[/bold] {query}")
        
        result = await orchestrator.customer_service.handle_query(
            query=query,
            language=lang
        )
        
        console.print(f"[bold green]Agent ({lang}):[/bold green] {result['response'][:200]}...")
        console.print(f"[dim]Intent: {result['detected_intent']} | ERP: {result['erp_context_used']}[/dim]")


async def main():
    """Main CLI demo."""
    console.print(Panel.fit(
        "[bold]🌍 Cross-Border Ecommerce AI[/bold]\n"
        "Multi-Agent Marketing & Customer Service System\n"
        "[dim]Demo Mode — No API keys required[/dim]",
        border_style="blue"
    ))
    
    # Initialize
    console.print("\n[dim]Initializing system components...[/dim]")
    llm = LLMSimulator()
    rag = RAGEngine()
    erp = ERPConnector()
    
    # Load sample FAQ data
    from data import load_sample_data
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
    
    console.print("[green]✅ All agents initialized[/green]\n")
    
    # Run demos
    market_result = await demo_market_insight(orchestrator)
    
    console.print("\n")
    pain_points = market_result.get("pain_points", [])
    await demo_copywriter(orchestrator, pain_points)
    
    console.print("\n")
    await demo_customer_service(orchestrator)
    
    # Final stats
    console.rule("[bold]📊 Session Statistics")
    token_summary = token_counter.get_daily_summary()
    cost_est = token_counter.estimate_cost()
    
    console.print(f"Total Tokens Used: {token_summary['total_tokens']:,}")
    console.print(f"Estimated Cost: ${cost_est['estimated_cost_usd']:.4f}")
    console.print(f"LLM Calls: {llm.call_count}")
    
    by_agent = token_summary.get("by_agent", {})
    if by_agent:
        table = Table(title="Token Usage by Agent")
        table.add_column("Agent")
        table.add_column("Tokens", justify="right")
        for agent, tokens in by_agent.items():
            table.add_row(agent, f"{tokens:,}")
        console.print(table)
    
    console.print("\n[bold green]✨ Demo complete![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
