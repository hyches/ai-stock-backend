"""
Enhanced news filtering with NLP entity extraction and sentiment analysis.

This module provides:
- Entity extraction: identify company names, sectors, ticker symbols in news
- Relevance scoring: determine how relevant a news item is to a given stock
- Sentiment analysis: score news sentiment (negative, neutral, positive)
- News filtering: intelligent filtering beyond regex patterns

Uses:
- spaCy for entity extraction (lightweight, no external API calls)
- VADER sentiment analysis (nltk, built-in, no training needed)
"""

from typing import List, Dict, Optional, Tuple
import re
from dataclasses import dataclass

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk import download as nltk_download
    # Ensure vader_lexicon is downloaded
    try:
        nltk_download('vader_lexicon', quiet=True)
    except Exception:
        pass
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False


@dataclass
class NewsAnalysis:
    """Analysis result for a single news item."""
    title: str
    publisher: Optional[str]
    link: Optional[str]
    providerPublishTime: Optional[int]
    
    # New fields (Phase 6)
    sentiment: float  # -1 (very negative) to +1 (very positive)
    relevance_score: float  # 0 (irrelevant) to 1 (highly relevant)
    matched_entities: Dict[str, List[str]]  # company, sector, keywords
    

class NewsFilter:
    """
    Enhanced news filtering with entity extraction and sentiment analysis.
    
    Workflow:
    1. Extract entities from title/publisher (company names, sectors)
    2. Calculate relevance score based on entity matches
    3. Analyze sentiment using VADER
    4. Return enriched news item with metadata
    """
    
    def __init__(self, symbol: str, company_name: str = "", sector: str = ""):
        self.symbol = symbol
        self.company_name = company_name.lower()
        self.sector = sector.lower()
        self.base_symbol = symbol.split('.')[0].upper()  # Remove exchange suffix
        
        # Initialize NLP tools if available
        self.nlp = None
        self.sia = None
        
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model not found. Run: python -m spacy download en_core_web_sm")
        
        if VADER_AVAILABLE:
            self.sia = SentimentIntensityAnalyzer()
        
        # Common sector keywords for fallback (if spaCy not available)
        self.sector_keywords = {
            "technology": ["tech", "software", "hardware", "ai", "cloud", "digital"],
            "finance": ["bank", "financial", "insurance", "fintech", "trading"],
            "healthcare": ["pharma", "biotech", "medical", "health", "hospital"],
            "energy": ["oil", "gas", "renewable", "solar", "wind", "power"],
            "industrials": ["manufacturing", "aerospace", "defense", "industrial"],
            "consumer": ["retail", "consumer", "grocery", "luxury", "fashion"],
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities and keywords from text."""
        entities = {
            "company": [],
            "sector": [],
            "keywords": [],
        }
        
        # Method 1: spaCy entity extraction (if available)
        if self.nlp:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    if ent.label_ in ["ORG", "PRODUCT"]:
                        entities["company"].append(ent.text)
                    # Note: spaCy GPE is location, not directly sector
            except Exception:
                pass
        
        # Method 2: Rule-based sector detection
        text_lower = text.lower()
        for sector, keywords in self.sector_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if sector not in entities["sector"]:
                        entities["sector"].append(sector)
        
        # Method 3: Symbol matching
        if self.base_symbol.lower() in text.upper():
            entities["keywords"].append(self.base_symbol)
        
        # Method 4: Company name matching
        if self.company_name and self.company_name in text_lower:
            entities["company"].append(self.company_name)
        
        # Extract word chunks (2-4 word phrases) as keywords
        words = text.split()
        for i in range(len(words) - 1):
            phrase = " ".join(words[i:i+2]).lower()
            if len(phrase) > 5 and phrase not in entities["keywords"]:
                # Only add meaningful business terms
                if any(term in phrase for term in ["earnings", "revenue", "profit", "growth", "stock", "share", "analyst", "rating", "target", "ipo", "buyback"]):
                    entities["keywords"].append(phrase)
        
        return entities
    
    def calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score for text (-1 to +1)."""
        if not self.sia:
            # Fallback: simple keyword-based sentiment
            return self._simple_sentiment(text)
        
        try:
            scores = self.sia.polarity_scores(text)
            # VADER returns compound score (-1 to +1)
            return scores['compound']
        except Exception:
            return self._simple_sentiment(text)
    
    def _simple_sentiment(self, text: str) -> float:
        """Simple keyword-based sentiment (fallback if VADER not available)."""
        text_lower = text.lower()
        
        positive_words = ["gain", "profit", "beat", "surge", "rally", "soar", "outperform", "upgrade", "bullish", "buy"]
        negative_words = ["loss", "miss", "drop", "plunge", "slump", "underperform", "downgrade", "bearish", "sell"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count + neg_count == 0:
            return 0.0
        
        # Normalize to -1 to +1 range
        return (pos_count - neg_count) / max(pos_count + neg_count, 1)
    
    def calculate_relevance(self, title: str, publisher: str, entities: Dict[str, List[str]]) -> float:
        """
        Calculate relevance score (0 to 1) for news to target stock.
        
        Scoring:
        - 0.9-1.0: Directly mentions company or ticker
        - 0.7-0.9: Company sector or related terms
        - 0.4-0.7: General market/industry news
        - 0.0-0.4: Likely irrelevant
        """
        score = 0.0
        
        # Direct symbol/company match: highest relevance
        if entities["company"]:
            score = max(score, 0.95)
        elif self.base_symbol in title.upper():
            score = max(score, 0.95)
        
        # Sector match
        elif entities["sector"]:
            score = max(score, 0.8)
        elif self.sector and self.sector in title.lower():
            score = max(score, 0.8)
        
        # Keyword match (earnings, analyst, rating, etc.)
        elif entities["keywords"]:
            score = max(score, 0.6)
        
        # Publisher check: financial news publishers more relevant
        financial_publishers = ["reuters", "bloomberg", "cnbc", "marketwatch", "barron's", "investor", "seeking alpha"]
        if any(pub in publisher.lower() for pub in financial_publishers):
            score = min(score + 0.1, 1.0)  # Boost relevance for financial outlets
        
        # General market publisher: lower boost
        general_publishers = ["cnbc", "bbc", "nyt", "wsj"]
        if any(pub in publisher.lower() for pub in general_publishers):
            score = min(score + 0.05, 1.0)
        
        return score
    
    def analyze_news(
        self,
        title: str,
        publisher: Optional[str] = None,
        link: Optional[str] = None,
        providerPublishTime: Optional[int] = None,
    ) -> NewsAnalysis:
        """
        Analyze a single news item and return enriched metadata.
        
        Returns NewsAnalysis with sentiment, relevance_score, and matched entities.
        """
        publisher = publisher or ""
        
        # Extract entities
        entities = self.extract_entities(title)
        
        # Calculate sentiment
        sentiment = self.calculate_sentiment(title)
        
        # Calculate relevance
        relevance = self.calculate_relevance(title, publisher, entities)
        
        return NewsAnalysis(
            title=title,
            publisher=publisher,
            link=link,
            providerPublishTime=providerPublishTime,
            sentiment=sentiment,
            relevance_score=relevance,
            matched_entities=entities,
        )
    
    def filter_news_list(
        self,
        news_items: List[Dict],
        min_relevance: float = 0.4,
        min_sentiment: Optional[float] = None,
        max_sentiment: Optional[float] = None,
    ) -> List[Dict]:
        """
        Filter and enrich a list of news items.
        
        Args:
            news_items: List of news dicts with 'title', 'publisher', 'link', 'providerPublishTime'
            min_relevance: Minimum relevance score to include (0-1)
            min_sentiment: Minimum sentiment to include (-1 to 1)
            max_sentiment: Maximum sentiment to include (-1 to 1)
        
        Returns:
            Filtered list of enriched news dicts (sorted by relevance, then sentiment)
        """
        analyzed = []
        
        for item in news_items:
            analysis = self.analyze_news(
                title=item.get('title', ''),
                publisher=item.get('publisher'),
                link=item.get('link'),
                providerPublishTime=item.get('providerPublishTime'),
            )
            
            # Apply filters
            if analysis.relevance_score < min_relevance:
                continue
            if min_sentiment is not None and analysis.sentiment < min_sentiment:
                continue
            if max_sentiment is not None and analysis.sentiment > max_sentiment:
                continue
            
            # Convert to dict for response
            analyzed.append({
                "title": analysis.title,
                "publisher": analysis.publisher,
                "link": analysis.link,
                "providerPublishTime": analysis.providerPublishTime,
                "sentiment": round(analysis.sentiment, 3),
                "relevance_score": round(analysis.relevance_score, 3),
                "matched_entities": analysis.matched_entities,
            })
        
        # Sort by relevance (descending), then by abs(sentiment) for interest
        analyzed.sort(
            key=lambda x: (x["relevance_score"], abs(x["sentiment"])),
            reverse=True
        )
        
        return analyzed


# Convenience functions for integration

def analyze_news_list(
    news_items: List[Dict],
    symbol: str,
    company_name: str = "",
    sector: str = "",
    min_relevance: float = 0.4,
) -> List[Dict]:
    """Convenience function to analyze and filter news items."""
    filter_obj = NewsFilter(symbol, company_name, sector)
    return filter_obj.filter_news_list(news_items, min_relevance=min_relevance)


def get_news_sentiment_for_symbol(
    news_items: List[Dict],
    symbol: str,
) -> Dict:
    """Get aggregate sentiment and stats for a symbol's news."""
    analyzed = analyze_news_list(news_items, symbol)
    
    if not analyzed:
        return {"count": 0, "avg_sentiment": 0.0, "avg_relevance": 0.0}
    
    sentiments = [item["sentiment"] for item in analyzed]
    relevances = [item["relevance_score"] for item in analyzed]
    
    return {
        "count": len(analyzed),
        "avg_sentiment": round(sum(sentiments) / len(sentiments), 3),
        "avg_relevance": round(sum(relevances) / len(relevances), 3),
        "positive_count": sum(1 for s in sentiments if s > 0.1),
        "negative_count": sum(1 for s in sentiments if s < -0.1),
        "neutral_count": sum(1 for s in sentiments if -0.1 <= s <= 0.1),
    }
