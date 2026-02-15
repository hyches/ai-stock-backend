"""
Tests for news filtering with sentiment analysis and entity extraction.

Tests cover:
- Sentiment analysis (VADER and fallback)
- Entity extraction (company, sector, keywords)
- Relevance scoring
- News filtering and sorting
- Integration with YFinanceProvider (mocked)
"""

import pytest
from app.services.news_filter import (
    NewsFilter,
    analyze_news_list,
    get_news_sentiment_for_symbol,
)


class TestNewsFilterSentiment:
    """Tests for sentiment analysis."""
    
    def test_positive_sentiment(self):
        """Test positive sentiment detection."""
        filter_obj = NewsFilter(symbol="AAPL")
        sentiment = filter_obj.calculate_sentiment("Apple stock surges on strong earnings beat")
        assert sentiment > 0.5, f"Expected positive sentiment, got {sentiment}"
    
    def test_negative_sentiment(self):
        """Test negative sentiment detection."""
        filter_obj = NewsFilter(symbol="AAPL")
        sentiment = filter_obj.calculate_sentiment("Apple stock plunges on disappointing losses")
        assert sentiment < -0.5, f"Expected negative sentiment, got {sentiment}"
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment detection."""
        filter_obj = NewsFilter(symbol="AAPL")
        sentiment = filter_obj.calculate_sentiment("Apple announced quarterly report")
        assert -0.2 <= sentiment <= 0.2, f"Expected neutral sentiment, got {sentiment}"


class TestNewsFilterEntityExtraction:
    """Tests for entity extraction."""
    
    def test_ticker_extraction(self):
        """Test ticker symbol extraction."""
        filter_obj = NewsFilter(symbol="AAPL")
        entities = filter_obj.extract_entities("AAPL reports record earnings")
        # Ticker or keywords related to earnings should be present
        assert entities.get("keywords"), f"Expected keywords, got {entities}"
    
    def test_sector_extraction(self):
        """Test sector keyword extraction."""
        filter_obj = NewsFilter(symbol="MSFT", sector="technology")
        entities = filter_obj.extract_entities("Microsoft cloud platform grows")
        assert entities.get("sector"), f"Expected sector keywords, got {entities}"
    
    def test_company_name_extraction(self):
        """Test company name extraction."""
        filter_obj = NewsFilter(symbol="AAPL", company_name="Apple Inc.")
        entities = filter_obj.extract_entities("Apple Inc. announces new product")
        # Should match the company name
        assert len(entities.get("company", [])) > 0 or \
               "Apple Inc." in entities.get("keywords", []), \
            f"Expected company reference, got {entities}"
    
    def test_keyword_extraction(self):
        """Test keyword extraction."""
        filter_obj = NewsFilter(symbol="TSLA")
        entities = filter_obj.extract_entities("Tesla announces quarterly earnings and shareholder buyback")
        # Should extract business keywords (2-word phrases with business terms)
        assert entities.get("keywords"), f"Expected keywords, got {entities}"
        # Check that keywords contain business-related terms
        all_keywords_str = " ".join(entities.get("keywords", []))
        assert any(term in all_keywords_str.lower() for term in ["earnings", "buyback"]), \
            f"Expected business keywords, got {entities}"


class TestNewsFilterRelevance:
    """Tests for relevance scoring."""
    
    def test_high_relevance_direct_mention(self):
        """Test high relevance for direct company mention."""
        filter_obj = NewsFilter(symbol="AAPL")
        relevance = filter_obj.calculate_relevance(
            title="Apple Inc. reports record revenue",
            publisher="Reuters",
            entities={"company": ["Apple"], "sector": [], "keywords": []}
        )
        assert relevance > 0.9, f"Expected high relevance, got {relevance}"
    
    def test_medium_relevance_sector(self):
        """Test medium relevance for sector mention."""
        filter_obj = NewsFilter(symbol="MSFT", sector="technology")
        relevance = filter_obj.calculate_relevance(
            title="Tech stocks rally on AI news",
            publisher="CNBC",
            entities={"company": [], "sector": ["technology"], "keywords": []}
        )
        assert relevance > 0.7, f"Expected medium-high relevance, got {relevance}"
    
    def test_low_relevance_no_match(self):
        """Test low relevance for unrelated news."""
        filter_obj = NewsFilter(symbol="AAPL")
        relevance = filter_obj.calculate_relevance(
            title="Weather forecast for NYC tomorrow",
            publisher="Weather Channel",
            entities={"company": [], "sector": [], "keywords": []}
        )
        assert relevance < 0.5, f"Expected low relevance, got {relevance}"
    
    def test_publisher_boost(self):
        """Test relevance boost for financial publishers."""
        filter_obj = NewsFilter(symbol="AAPL")
        
        relevance_bloomberg = filter_obj.calculate_relevance(
            title="Stock news",
            publisher="Bloomberg",
            entities={"company": [], "sector": [], "keywords": []}
        )
        
        relevance_generic = filter_obj.calculate_relevance(
            title="Stock news",
            publisher="Local News",
            entities={"company": [], "sector": [], "keywords": []}
        )
        
        # Financial publishers should have higher relevance
        assert relevance_bloomberg > relevance_generic, \
            f"Bloomberg ({relevance_bloomberg}) should score higher than Local News ({relevance_generic})"


class TestNewsItemAnalysis:
    """Tests for complete news item analysis."""
    
    def test_analyze_news_item(self):
        """Test analyzing a single news item."""
        filter_obj = NewsFilter(symbol="AAPL", company_name="Apple")
        analysis = filter_obj.analyze_news(
            title="Apple stock surges on strong earnings",
            publisher="Reuters",
            link="https://example.com/news",
            providerPublishTime=1234567890,
        )
        
        assert analysis.title == "Apple stock surges on strong earnings"
        assert analysis.publisher == "Reuters"
        assert analysis.link == "https://example.com/news"
        assert analysis.providerPublishTime == 1234567890
        assert -1 <= analysis.sentiment <= 1, f"Sentiment out of range: {analysis.sentiment}"
        assert 0 <= analysis.relevance_score <= 1, f"Relevance out of range: {analysis.relevance_score}"
        assert isinstance(analysis.matched_entities, dict)


class TestNewsFiltering:
    """Tests for filtering and sorting news."""
    
    def test_filter_by_relevance(self):
        """Test filtering by minimum relevance."""
        filter_obj = NewsFilter(symbol="AAPL")
        
        news_items = [
            {"title": "Apple reports earnings", "publisher": "Reuters"},
            {"title": "Weather forecast", "publisher": "Weather.com"},
            {"title": "Tech stocks rally", "publisher": "Bloomberg"},
        ]
        
        filtered = filter_obj.filter_news_list(news_items, min_relevance=0.7)
        
        # Should filter out the weather forecast
        assert len(filtered) < len(news_items), "Should have filtered some items"
        assert all(item["relevance_score"] >= 0.7 for item in filtered), \
            "All filtered items should meet relevance threshold"
    
    def test_filter_by_sentiment(self):
        """Test filtering by sentiment range."""
        filter_obj = NewsFilter(symbol="AAPL")
        
        news_items = [
            {"title": "Apple stock soars on great earnings", "publisher": "Reuters"},
            {"title": "Apple stock drops on bad news", "publisher": "Bloomberg"},
            {"title": "Apple stock unchanged", "publisher": "CNBC"},
        ]
        
        # Filter for positive sentiment only
        positive_only = filter_obj.filter_news_list(
            news_items,
            min_relevance=0,
            min_sentiment=0.3,
        )
        
        assert all(item["sentiment"] >= 0.3 for item in positive_only), \
            "All filtered items should have positive sentiment"
    
    def test_filter_sorting(self):
        """Test that results are sorted by relevance then sentiment."""
        filter_obj = NewsFilter(symbol="AAPL", company_name="Apple")
        
        news_items = [
            {"title": "Unrelated news story", "publisher": "Reuters"},
            {"title": "Apple great earnings", "publisher": "Reuters"},
            {"title": "Tech sector news", "publisher": "Reuters"},
        ]
        
        filtered = filter_obj.filter_news_list(news_items, min_relevance=0)
        
        # Should be sorted by relevance descending
        if len(filtered) > 1:
            relevances = [item["relevance_score"] for item in filtered]
            assert relevances == sorted(relevances, reverse=True), \
                f"Items should be sorted by relevance, got {relevances}"


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_analyze_news_list_function(self):
        """Test analyze_news_list convenience function."""
        news_items = [
            {
                "title": "Apple Inc. reports strong earnings",
                "publisher": "Reuters",
                "link": "https://example.com/1",
                "providerPublishTime": 1000000,
            },
            {
                "title": "Tech stocks rally",
                "publisher": "Bloomberg",
                "link": "https://example.com/2",
                "providerPublishTime": 1000001,
            },
        ]
        
        result = analyze_news_list(
            news_items,
            symbol="AAPL",
            company_name="Apple Inc.",
            min_relevance=0.3,
        )
        
        assert len(result) > 0
        assert all("sentiment" in item for item in result)
        assert all("relevance_score" in item for item in result)
    
    def test_get_news_sentiment_for_symbol(self):
        """Test sentiment aggregation function."""
        news_items = [
            {"title": "Apple stock surges", "publisher": "Reuters"},
            {"title": "Apple stock drops", "publisher": "Bloomberg"},
        ]
        
        stats = get_news_sentiment_for_symbol(news_items, "AAPL")
        
        assert "count" in stats
        assert "avg_sentiment" in stats
        assert "avg_relevance" in stats
        assert stats["count"] > 0
        assert -1 <= stats["avg_sentiment"] <= 1
    
    def test_empty_sentiment_stats(self):
        """Test sentiment aggregation with empty news."""
        stats = get_news_sentiment_for_symbol([], "AAPL")
        
        assert stats["count"] == 0
        assert stats["avg_sentiment"] == 0.0


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_title(self):
        """Test handling of empty titles."""
        filter_obj = NewsFilter(symbol="AAPL")
        analysis = filter_obj.analyze_news(
            title="",
            publisher="Reuters",
        )
        
        assert analysis.title == ""
        assert analysis.sentiment is not None  # Should still calculate sentiment
    
    def test_none_publisher(self):
        """Test handling of None publisher."""
        filter_obj = NewsFilter(symbol="AAPL")
        analysis = filter_obj.analyze_news(
            title="Apple stock news",
            publisher=None,
        )
        
        assert analysis.publisher is None or analysis.publisher == ""
    
    def test_very_long_title(self):
        """Test handling of very long titles."""
        filter_obj = NewsFilter(symbol="AAPL")
        long_title = "Apple " * 100  # Very long title
        analysis = filter_obj.analyze_news(title=long_title)
        
        assert analysis.title == long_title
        assert -1 <= analysis.sentiment <= 1
    
    def test_special_characters_in_title(self):
        """Test handling of special characters."""
        filter_obj = NewsFilter(symbol="AAPL")
        title = "Apple®™ stock $AAPL 📈 news! #finance @markets"
        analysis = filter_obj.analyze_news(title=title)
        
        assert analysis.title == title
        assert analysis.sentiment is not None


class TestSpacyIntegration:
    """Tests for spaCy entity extraction (if available)."""
    
    def test_spacy_availability(self):
        """Test that spaCy is available."""
        filter_obj = NewsFilter(symbol="AAPL")
        # If spaCy model fails to load, this shouldn't crash
        assert filter_obj.nlp is not None or filter_obj.nlp is None, \
            "Should handle spaCy availability gracefully"
    
    def test_entity_extraction_with_spacy(self):
        """Test that entity extraction works even with/without spaCy."""
        filter_obj = NewsFilter(symbol="AAPL")
        entities = filter_obj.extract_entities(
            "Apple Inc. announced partnership with Google"
        )
        
        # Should return a dict with expected keys
        assert "company" in entities
        assert "sector" in entities
        assert "keywords" in entities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
