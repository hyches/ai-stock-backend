import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to sys.path
sys.path.append(os.getcwd())

async def test_multi_agent_flow():
    print("🚀 Starting Multi-Agent Flow Verification...")
    
    # Mock the data services to avoid hitting real APIs
    mock_tech_data = {
        "trend_analysis": {"trend_direction": "uptrend"},
        "momentum_indicators": {"rsi": 65, "macd": 5.2},
        "volatility_indicators": {"bb_width": 0.1},
        "volume_analysis": {"volume_trend": "high"}
    }
    
    mock_fund_data = {
        "financial_ratios": {"profitability_ratios": {"roe": 0.25}},
        "valuation_metrics": {"price_metrics": {"pe_ratio": 25}},
        "growth_metrics": {"revenue_growth": 0.15}
    }
    
    mock_sent_data = {
        "overall_sentiment": {"composite_score": 0.75},
        "news_sentiment": {"news_articles": {"sentiment": {"vader": {"compound": 0.6}}}}
    }
    
    # Patches for the services
    with patch('app.services.technical_analysis.technical_analysis.get_comprehensive_analysis', return_value=mock_tech_data), \
         patch('app.services.fundamental_analysis.fundamental_analysis.get_comprehensive_analysis', return_value=mock_fund_data), \
         patch('app.services.sentiment_analysis.sentiment_analysis.get_comprehensive_sentiment', return_value=mock_sent_data):
        
        from app.agents.trader import agent_service
        
        print("🔍 Running full analysis for RELIANCE (Mock Data)...")
        import time
        start_time = time.time()
        
        try:
            # We'll try a timeout here just in case
            result = await asyncio.wait_for(agent_service.run_full_analysis("RELIANCE"), timeout=300)
            
            duration = time.time() - start_time
            print(f"\n✅ Analysis Complete in {duration:.2f}s!")
            print(f"Symbol: {result['symbol']}")
            print("\n--- FINAL DECISION ---")
            print(result['final_decision'])
            
            print("\n--- ANALYST REPORTS ---")
            for role, report in result['analyst_reports'].items():
                print(f"\n[{role.upper()}]:\n{report[:200]}...")
                
            print("\n--- RESEARCH CASES ---")
            for side, report in result['research_cases'].items():
                print(f"\n[{side.upper()}]:\n{report[:200]}...")
                
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            if "Ollama" in str(e) or "client" in str(e).lower():
                print("💡 Suggestion: Ensure Ollama is running locally and you have run 'ollama pull llama3.1'")

if __name__ == "__main__":
    asyncio.run(test_multi_agent_flow())
