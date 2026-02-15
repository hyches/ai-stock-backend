# AI Stock Backend - Complete Implementation Plan

**Status**: Active Development  
**Created**: November 16, 2025  
**Priority**: High - Systematic execution required

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Assessment](#current-state-assessment)
3. [Policy Opportunity Auto-Tracking Implementation](#policy-opportunity-auto-tracking-implementation)
4. [12-Week Comprehensive Roadmap](#12-week-comprehensive-roadmap)
5. [Execution Order](#execution-order)
6. [Success Metrics](#success-metrics)

---

## Executive Summary

This document consolidates all implementation plans for transforming the AI Stock Backend from a prototype to a production-grade platform. The immediate priority is implementing automated policy tracking, while laying the foundation for Feature Store, job queue infrastructure, and ML explainability.

**Key Objectives:**
- Automate policy intelligence from PIB, LinkedIn, government sources
- Implement unified Feature Store for all data consumers
- Setup Redis + Celery for background processing
- Migrate frontend to React Query for real-time updates
- Add ML explainability (SHAP) and advanced screeners
- Build professional F&O terminal with options chain and Greeks
- Deploy alerts engine and observability stack

---

## Current State Assessment

### ✅ Working Features
- Research tab with TradingView charts and technical indicators
- ML-based price prediction (RandomForest/GradientBoosting)
- Pattern detection (H&S, triangles, double tops, breakouts)
- Feature extraction service (50+ technical indicators)
- Basic screener and portfolio optimizer (frontend mock)
- Transaction tracking (frontend mock)
- Settings page (frontend mock)

### ⚠️ Issues to Address
1. **Dashboard** uses TradingContext (mock data). Keep mock/no broker integration until production; defer any trading/broker APIs. Read-only backend data APIs can be introduced later without enabling order placement.
2. **Policy page** has manual upload, needs automated tracking
3. **No unified data layer** - each service reads raw data independently
4. **Synchronous ML training** blocks requests (needs background jobs)
5. **No caching layer** - repeated calculations waste resources
6. **Mixed currencies** in portfolio calculations
7. **No explainability** for ML predictions
8. **No alerts system** for price/pattern notifications

---

## Policy Opportunity Auto-Tracking Implementation

### Phase 1: Infrastructure Setup (Week 1)

#### 1.1 Redis & Celery Installation

**File: `docker-compose.yml` (create new)**
```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: ai-stock-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: ai-stock-postgres
    environment:
      POSTGRES_USER: stockuser
      POSTGRES_PASSWORD: stockpass
      POSTGRES_DB: stockdb
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  redis-data:
  postgres-data:
```

**File: `requirements.txt` (append)**
```txt
# Job Queue & Caching
celery==5.3.4
redis==5.0.1
flower==2.0.1

# Web Scraping
beautifulsoup4==4.12.2
requests==2.31.0
selenium==4.15.2
feedparser==6.0.10

# NLP & ML
spacy==3.7.2
transformers==4.35.2
torch==2.1.1
sentencepiece==0.1.99

# Additional utilities
python-dateutil==2.8.2
pytz==2023.3
```

**File: `app/core/celery_app.py` (create new)**
```python
from celery import Celery
from celery.schedules import crontab
from app.config.settings import settings

celery_app = Celery(
    "ai_stock_backend",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.policy_tracker",
        "app.tasks.ml_training",
        "app.tasks.report_generator"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "check-policy-updates-every-30-min": {
        "task": "app.tasks.policy_tracker.check_policy_updates",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "train-ml-models-daily": {
        "task": "app.tasks.ml_training.train_all_models",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
    "generate-daily-reports": {
        "task": "app.tasks.report_generator.generate_daily_reports",
        "schedule": crontab(hour=7, minute=0),  # 7 AM daily
    },
}

@celery_app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
```

**File: `app/config/settings.py` (update)**
```python
# Add to Settings class
REDIS_URL: str = "redis://localhost:6379/0"
CELERY_BROKER_URL: str = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
```

#### 1.2 Database Schema Migration

**File: `alembic/versions/004_add_policy_tracking.py` (create new)**
```python
"""Add policy tracking tables

Revision ID: 004
Revises: 003
Create Date: 2025-11-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # Policies table
    op.create_table(
        'policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),  # PIB, LinkedIn, News
        sa.Column('source_url', sa.String(1000), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('published_date', sa.DateTime(), nullable=False),
        sa.Column('scraped_date', sa.DateTime(), nullable=False),
        sa.Column('sectors', ARRAY(sa.String()), nullable=True),
        sa.Column('affected_stocks', ARRAY(sa.String()), nullable=True),
        sa.Column('opportunity_level', sa.String(20), nullable=True),  # High, Medium, Low
        sa.Column('budget_allocation', sa.Numeric(15, 2), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('entities', JSONB, nullable=True),  # NLP extracted entities
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_policies_source', 'policies', ['source'])
    op.create_index('idx_policies_published_date', 'policies', ['published_date'])
    op.create_index('idx_policies_sectors', 'policies', ['sectors'], postgresql_using='gin')
    
    # Monitored sources table
    op.create_table(
        'monitored_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),  # RSS, LinkedIn, News
        sa.Column('source_name', sa.String(200), nullable=False),
        sa.Column('url', sa.String(1000), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_checked', sa.DateTime(), nullable=True),
        sa.Column('check_interval_minutes', sa.Integer(), default=30),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Policy alerts/subscriptions table
    op.create_table(
        'policy_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('sectors', ARRAY(sa.String()), nullable=True),
        sa.Column('keywords', ARRAY(sa.String()), nullable=True),
        sa.Column('min_opportunity_level', sa.String(20), nullable=True),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_policy_alerts_user', 'policy_alerts', ['user_id'])

def downgrade():
    op.drop_table('policy_alerts')
    op.drop_table('monitored_sources')
    op.drop_table('policies')
```

### Phase 2: Policy Tracker Service (Week 1-2)

#### 2.1 Core Service Implementation

**File: `app/services/policy_tracker_service.py` (create new)**
```python
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import logging
from sqlalchemy.orm import Session
from app.models.policy import Policy, MonitoredSource
from app.services.policy_analyzer import PolicyAnalyzer

logger = logging.getLogger(__name__)

class PolicyTrackerService:
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = PolicyAnalyzer()
        
    def scrape_pib_india(self) -> List[Dict]:
        """Scrape Press Information Bureau (PIB) RSS feed"""
        try:
            # PIB RSS feeds by category
            feeds = [
                "https://pib.gov.in/RssMain.aspx?ModId=3&Lang=1",  # Economy
                "https://pib.gov.in/RssMain.aspx?ModId=7&Lang=1",  # Finance
                "https://pib.gov.in/RssMain.aspx?ModId=9&Lang=1",  # Infrastructure
            ]
            
            policies = []
            for feed_url in feeds:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:  # Latest 10 per feed
                    # Check if already exists
                    existing = self.db.query(Policy).filter(
                        Policy.source_url == entry.link
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Parse published date
                    published_date = datetime(*entry.published_parsed[:6])
                    
                    # Only process recent entries (last 24 hours)
                    if datetime.utcnow() - published_date > timedelta(days=1):
                        continue
                    
                    policies.append({
                        "title": entry.title,
                        "content": entry.description,
                        "source": "PIB",
                        "source_url": entry.link,
                        "published_date": published_date,
                        "scraped_date": datetime.utcnow(),
                    })
            
            logger.info(f"Scraped {len(policies)} policies from PIB")
            return policies
            
        except Exception as e:
            logger.error(f"Error scraping PIB: {str(e)}")
            return []
    
    def scrape_linkedin_posts(self, profiles: List[str] = None) -> List[Dict]:
        """Scrape LinkedIn posts from government/finance ministers
        Note: Requires LinkedIn API access or Selenium for authenticated scraping
        """
        if profiles is None:
            profiles = [
                "nirmala-sitharaman",  # Finance Minister
                "piyush-goyal",  # Commerce Minister
                # Add more profiles
            ]
        
        policies = []
        # TODO: Implement LinkedIn API or Selenium scraping
        # For now, return empty (requires LinkedIn Developer account)
        logger.warning("LinkedIn scraping not implemented - requires API access")
        return policies
    
    def scrape_news_sites(self) -> List[Dict]:
        """Scrape economic policy news from major publications"""
        try:
            sources = [
                {
                    "name": "Economic Times",
                    "url": "https://economictimes.indiatimes.com/news/economy/policy",
                    "selector": "article"
                },
                {
                    "name": "Reuters India",
                    "url": "https://www.reuters.com/world/india/",
                    "selector": "article"
                },
            ]
            
            policies = []
            for source in sources:
                try:
                    response = requests.get(source["url"], timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    articles = soup.find_all(source["selector"], limit=5)
                    for article in articles:
                        title_tag = article.find(['h1', 'h2', 'h3', 'a'])
                        if not title_tag:
                            continue
                        
                        title = title_tag.get_text(strip=True)
                        link = title_tag.get('href', '')
                        
                        # Filter for policy-related keywords
                        policy_keywords = ['policy', 'budget', 'reform', 'scheme', 
                                         'allocation', 'subsidy', 'regulation']
                        if not any(kw in title.lower() for kw in policy_keywords):
                            continue
                        
                        # Check if already exists
                        if link and self.db.query(Policy).filter(
                            Policy.source_url == link
                        ).first():
                            continue
                        
                        policies.append({
                            "title": title,
                            "content": article.get_text(strip=True)[:1000],
                            "source": source["name"],
                            "source_url": link,
                            "published_date": datetime.utcnow(),
                            "scraped_date": datetime.utcnow(),
                        })
                
                except Exception as e:
                    logger.error(f"Error scraping {source['name']}: {str(e)}")
                    continue
            
            logger.info(f"Scraped {len(policies)} policies from news sites")
            return policies
            
        except Exception as e:
            logger.error(f"Error in news scraping: {str(e)}")
            return []
    
    def process_and_store_policies(self, raw_policies: List[Dict]) -> int:
        """Analyze and store policies in database"""
        stored_count = 0
        
        for policy_data in raw_policies:
            try:
                # Analyze policy content
                analysis = self.analyzer.analyze(
                    title=policy_data["title"],
                    content=policy_data["content"]
                )
                
                # Create policy record
                policy = Policy(
                    title=policy_data["title"],
                    content=policy_data["content"],
                    source=policy_data["source"],
                    source_url=policy_data.get("source_url"),
                    published_date=policy_data["published_date"],
                    scraped_date=policy_data["scraped_date"],
                    sectors=analysis["sectors"],
                    affected_stocks=analysis["affected_stocks"],
                    opportunity_level=analysis["opportunity_level"],
                    budget_allocation=analysis.get("budget_allocation"),
                    sentiment_score=analysis["sentiment_score"],
                    entities=analysis["entities"],
                    summary=analysis["summary"],
                )
                
                self.db.add(policy)
                stored_count += 1
                
            except Exception as e:
                logger.error(f"Error processing policy '{policy_data['title']}': {str(e)}")
                continue
        
        try:
            self.db.commit()
            logger.info(f"Stored {stored_count} policies in database")
        except Exception as e:
            logger.error(f"Error committing policies: {str(e)}")
            self.db.rollback()
            return 0
        
        return stored_count
    
    def run_full_check(self) -> Dict[str, int]:
        """Run complete policy check across all sources"""
        logger.info("Starting full policy check...")
        
        all_policies = []
        
        # Scrape all sources
        all_policies.extend(self.scrape_pib_india())
        all_policies.extend(self.scrape_linkedin_posts())
        all_policies.extend(self.scrape_news_sites())
        
        # Process and store
        stored_count = self.process_and_store_policies(all_policies)
        
        return {
            "total_scraped": len(all_policies),
            "total_stored": stored_count,
            "timestamp": datetime.utcnow().isoformat()
        }
```

#### 2.2 NLP Policy Analyzer

**File: `app/services/policy_analyzer.py` (create new)**
```python
import spacy
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)

class PolicyAnalyzer:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found, downloading...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Load FinBERT for sentiment analysis
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        except Exception as e:
            logger.error(f"Error loading FinBERT: {str(e)}")
            self.tokenizer = None
            self.sentiment_model = None
        
        # Sector keyword mapping
        self.sector_keywords = {
            "Banking": ["bank", "banking", "financial services", "nbfc"],
            "Infrastructure": ["infrastructure", "roads", "highways", "construction"],
            "Energy": ["energy", "power", "renewable", "solar", "wind"],
            "Telecom": ["telecom", "telecommunications", "5g", "spectrum"],
            "Pharma": ["pharma", "healthcare", "medicine", "drug"],
            "Auto": ["automobile", "auto", "vehicle", "electric vehicle", "ev"],
            "IT": ["technology", "software", "digital", "it services"],
            "Manufacturing": ["manufacturing", "industry", "production", "make in india"],
            "Agriculture": ["agriculture", "farming", "crop", "rural"],
            "Real Estate": ["real estate", "housing", "property", "construction"],
        }
        
        # Stock mapping (simplified - should use proper database)
        self.sector_stocks = {
            "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK"],
            "Infrastructure": ["LT", "ADANIENT", "ULTRACEMCO"],
            "Energy": ["RELIANCE", "NTPC", "POWERGRID", "ADANIPOWER"],
            "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB"],
            "Auto": ["TATAMOTORS", "M&M", "MARUTI", "BAJAJ-AUTO"],
            "IT": ["TCS", "INFY", "WIPRO", "HCLTECH"],
        }
    
    def extract_entities(self, text: str) -> Dict:
        """Extract named entities using spaCy"""
        doc = self.nlp(text)
        
        entities = {
            "organizations": [],
            "locations": [],
            "dates": [],
            "money": [],
            "persons": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "GPE":
                entities["locations"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
            elif ent.label_ == "MONEY":
                entities["money"].append(ent.text)
            elif ent.label_ == "PERSON":
                entities["persons"].append(ent.text)
        
        return entities
    
    def detect_sectors(self, text: str) -> List[str]:
        """Detect relevant sectors from policy text"""
        text_lower = text.lower()
        detected_sectors = []
        
        for sector, keywords in self.sector_keywords.items():
            if any(kw in text_lower for kw in keywords):
                detected_sectors.append(sector)
        
        return detected_sectors
    
    def map_stocks(self, sectors: List[str]) -> List[str]:
        """Map sectors to affected stocks"""
        stocks = set()
        for sector in sectors:
            if sector in self.sector_stocks:
                stocks.update(self.sector_stocks[sector])
        return list(stocks)
    
    def extract_budget_allocation(self, text: str) -> Optional[float]:
        """Extract budget allocation amount from text"""
        # Match patterns like "Rs 10000 crore", "₹5000 crore", "$1 billion"
        patterns = [
            r'₹\s*([\d,]+\.?\d*)\s*(crore|lakh|billion|million)',
            r'Rs\.?\s*([\d,]+\.?\d*)\s*(crore|lakh|billion|million)',
            r'\$\s*([\d,]+\.?\d*)\s*(billion|million)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                unit = match.group(2).lower()
                
                # Convert to crores
                if unit == 'crore':
                    return amount
                elif unit == 'lakh':
                    return amount / 100
                elif unit == 'billion':
                    return amount * 100  # Assuming USD, 1B ~ 100 crore
                elif unit == 'million':
                    return amount  # Assuming USD, 1M ~ 1 crore
        
        return None
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment using FinBERT"""
        if not self.tokenizer or not self.sentiment_model:
            return 0.0
        
        try:
            # Truncate text to model max length
            inputs = self.tokenizer(text[:512], return_tensors="pt", truncation=True)
            
            with torch.no_grad():
                outputs = self.sentiment_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # FinBERT outputs: [positive, negative, neutral]
            sentiment_score = predictions[0][0].item() - predictions[0][1].item()
            return round(sentiment_score, 3)
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return 0.0
    
    def calculate_opportunity_level(self, sectors: List[str], budget: Optional[float], 
                                   sentiment: float) -> str:
        """Calculate opportunity level based on multiple factors"""
        score = 0
        
        # Factor 1: Number of sectors (more sectors = broader impact)
        score += len(sectors) * 10
        
        # Factor 2: Budget allocation
        if budget:
            if budget > 10000:
                score += 30
            elif budget > 1000:
                score += 20
            else:
                score += 10
        
        # Factor 3: Sentiment
        if sentiment > 0.5:
            score += 30
        elif sentiment > 0:
            score += 15
        
        # Determine level
        if score >= 60:
            return "High"
        elif score >= 30:
            return "Medium"
        else:
            return "Low"
    
    def generate_summary(self, title: str, content: str, max_length: int = 200) -> str:
        """Generate brief summary of policy"""
        # Simple extractive summary - first sentence or truncate
        sentences = content.split('.')
        summary = sentences[0] if sentences else content
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def analyze(self, title: str, content: str) -> Dict:
        """Complete analysis of policy document"""
        full_text = f"{title}. {content}"
        
        # Extract entities
        entities = self.extract_entities(full_text)
        
        # Detect sectors
        sectors = self.detect_sectors(full_text)
        
        # Map affected stocks
        affected_stocks = self.map_stocks(sectors)
        
        # Extract budget
        budget_allocation = self.extract_budget_allocation(full_text)
        
        # Sentiment analysis
        sentiment_score = self.analyze_sentiment(full_text)
        
        # Calculate opportunity level
        opportunity_level = self.calculate_opportunity_level(
            sectors, budget_allocation, sentiment_score
        )
        
        # Generate summary
        summary = self.generate_summary(title, content)
        
        return {
            "sectors": sectors,
            "affected_stocks": affected_stocks,
            "budget_allocation": budget_allocation,
            "sentiment_score": sentiment_score,
            "opportunity_level": opportunity_level,
            "entities": entities,
            "summary": summary
        }
```

### Phase 3: Celery Tasks (Week 2)

**File: `app/tasks/policy_tracker.py` (create new)**
```python
from celery import Task
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.policy_tracker_service import PolicyTrackerService
import logging

logger = logging.getLogger(__name__)

class DatabaseTask(Task):
    """Base task with database session"""
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()

@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.policy_tracker.check_policy_updates")
def check_policy_updates(self):
    """Periodic task to check for new policy updates"""
    logger.info("Starting scheduled policy update check")
    
    try:
        service = PolicyTrackerService(self.db)
        result = service.run_full_check()
        
        logger.info(f"Policy check completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in policy check: {str(e)}")
        raise

@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.policy_tracker.analyze_single_policy")
def analyze_single_policy(self, policy_id: int):
    """Analyze a single policy (can be triggered manually)"""
    from app.models.policy import Policy
    from app.services.policy_analyzer import PolicyAnalyzer
    
    try:
        policy = self.db.query(Policy).filter(Policy.id == policy_id).first()
        if not policy:
            return {"error": "Policy not found"}
        
        analyzer = PolicyAnalyzer()
        analysis = analyzer.analyze(policy.title, policy.content)
        
        # Update policy with analysis
        policy.sectors = analysis["sectors"]
        policy.affected_stocks = analysis["affected_stocks"]
        policy.opportunity_level = analysis["opportunity_level"]
        policy.sentiment_score = analysis["sentiment_score"]
        policy.entities = analysis["entities"]
        policy.summary = analysis["summary"]
        
        self.db.commit()
        
        return {"status": "success", "policy_id": policy_id}
        
    except Exception as e:
        logger.error(f"Error analyzing policy {policy_id}: {str(e)}")
        self.db.rollback()
        raise
```

### Phase 4: API Endpoints (Week 2)

**File: `app/models/policy.py` (create new)**
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.base_class import Base

class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    source = Column(String(100), nullable=False, index=True)
    source_url = Column(String(1000), nullable=True)
    content = Column(Text, nullable=False)
    published_date = Column(DateTime, nullable=False, index=True)
    scraped_date = Column(DateTime, nullable=False)
    sectors = Column(ARRAY(String), nullable=True, index=True)
    affected_stocks = Column(ARRAY(String), nullable=True)
    opportunity_level = Column(String(20), nullable=True)
    budget_allocation = Column(Numeric(15, 2), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    entities = Column(JSONB, nullable=True)
    summary = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class MonitoredSource(Base):
    __tablename__ = "monitored_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(50), nullable=False)
    source_name = Column(String(200), nullable=False)
    url = Column(String(1000), nullable=False)
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    check_interval_minutes = Column(Integer, default=30)
    created_at = Column(DateTime, server_default=func.now())

class PolicyAlert(Base):
    __tablename__ = "policy_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    policy_id = Column(Integer, nullable=False)
    sectors = Column(ARRAY(String), nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    min_opportunity_level = Column(String(20), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
```

**File: `app/schemas/policy.py` (create new)**
```python
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict

class PolicyBase(BaseModel):
    title: str
    source: str
    content: str
    
class PolicyCreate(PolicyBase):
    source_url: Optional[str] = None
    published_date: datetime

class PolicyResponse(PolicyBase):
    id: int
    source_url: Optional[str]
    published_date: datetime
    scraped_date: datetime
    sectors: Optional[List[str]]
    affected_stocks: Optional[List[str]]
    opportunity_level: Optional[str]
    budget_allocation: Optional[float]
    sentiment_score: Optional[float]
    entities: Optional[Dict]
    summary: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PolicyListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    policies: List[PolicyResponse]

class PolicySubscribeRequest(BaseModel):
    sectors: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    min_opportunity_level: Optional[str] = None
```

**File: `app/api/endpoints/policy.py` (create new)**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.policy import Policy, PolicyAlert
from app.schemas.policy import PolicyResponse, PolicyListResponse, PolicySubscribeRequest
from app.services.policy_tracker_service import PolicyTrackerService
from app.tasks.policy_tracker import check_policy_updates

router = APIRouter()

@router.get("/latest", response_model=PolicyListResponse)
def get_latest_policies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sector: Optional[str] = None,
    opportunity_level: Optional[str] = None,
    source: Optional[str] = None,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get latest policy updates with filters"""
    
    # Base query
    query = db.query(Policy).filter(Policy.is_active == True)
    
    # Date filter
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(Policy.published_date >= cutoff_date)
    
    # Apply filters
    if sector:
        query = query.filter(Policy.sectors.contains([sector]))
    
    if opportunity_level:
        query = query.filter(Policy.opportunity_level == opportunity_level)
    
    if source:
        query = query.filter(Policy.source == source)
    
    # Order by published date
    query = query.order_by(Policy.published_date.desc())
    
    # Get total count
    total = query.count()
    
    # Pagination
    offset = (page - 1) * page_size
    policies = query.offset(offset).limit(page_size).all()
    
    return PolicyListResponse(
        total=total,
        page=page,
        page_size=page_size,
        policies=policies
    )

@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy_detail(
    policy_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific policy"""
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return policy

@router.post("/subscribe")
def subscribe_to_policies(
    subscription: PolicySubscribeRequest,
    user_id: int = Query(...),  # In production, get from JWT token
    db: Session = Depends(get_db)
):
    """Subscribe to policy alerts based on criteria"""
    
    # In a real app, you'd create a user subscription record
    # For now, return success
    return {
        "status": "success",
        "message": "Subscribed to policy alerts",
        "criteria": subscription.dict()
    }

@router.post("/trigger-check")
def trigger_policy_check(
    db: Session = Depends(get_db)
):
    """Manually trigger policy update check (admin endpoint)"""
    
    # Trigger Celery task
    task = check_policy_updates.delay()
    
    return {
        "status": "triggered",
        "task_id": task.id,
        "message": "Policy update check started in background"
    }

@router.get("/sources/list")
def get_monitored_sources(
    db: Session = Depends(get_db)
):
    """Get list of monitored policy sources"""
    from app.models.policy import MonitoredSource
    
    sources = db.query(MonitoredSource).filter(
        MonitoredSource.is_active == True
    ).all()
    
    return {"sources": sources}

@router.get("/stats")
def get_policy_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get policy statistics"""
    from sqlalchemy import func
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Total policies
    total = db.query(Policy).filter(
        Policy.published_date >= cutoff_date
    ).count()
    
    # By source
    by_source = db.query(
        Policy.source,
        func.count(Policy.id).label('count')
    ).filter(
        Policy.published_date >= cutoff_date
    ).group_by(Policy.source).all()
    
    # By opportunity level
    by_opportunity = db.query(
        Policy.opportunity_level,
        func.count(Policy.id).label('count')
    ).filter(
        Policy.published_date >= cutoff_date
    ).group_by(Policy.opportunity_level).all()
    
    return {
        "total_policies": total,
        "by_source": {source: count for source, count in by_source},
        "by_opportunity_level": {level: count for level, count in by_opportunity},
        "date_range_days": days
    }
```

**File: `app/api/api.py` (update to include policy router)**
```python
# Add import
from app.api.endpoints import policy

# Add to API router
api_router.include_router(policy.router, prefix="/policy", tags=["policy"])
```

### Phase 5: Frontend Integration (Week 3)

**File: `frontend/src/pages/Policy.tsx` (complete redesign)**
```typescript
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Bell, Filter, TrendingUp, Calendar, ExternalLink, RefreshCw } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Policy {
  id: number;
  title: string;
  source: string;
  source_url: string;
  content: string;
  published_date: string;
  sectors: string[];
  affected_stocks: string[];
  opportunity_level: 'High' | 'Medium' | 'Low';
  budget_allocation: number | null;
  sentiment_score: number;
  summary: string;
  created_at: string;
}

interface PolicyStats {
  total_policies: number;
  by_source: Record<string, number>;
  by_opportunity_level: Record<string, number>;
  date_range_days: number;
}

export default function PolicyOpportunity() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [stats, setStats] = useState<PolicyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterSector, setFilterSector] = useState<string>('all');
  const [filterOpportunity, setFilterOpportunity] = useState<string>('all');
  const [filterSource, setFilterSource] = useState<string>('all');
  const [refreshing, setRefreshing] = useState(false);

  const fetchPolicies = async () => {
    try {
      setLoading(true);
      
      // Build query params
      const params = new URLSearchParams({
        page: '1',
        page_size: '50',
        days: '30'
      });
      
      if (filterSector !== 'all') params.append('sector', filterSector);
      if (filterOpportunity !== 'all') params.append('opportunity_level', filterOpportunity);
      if (filterSource !== 'all') params.append('source', filterSource);
      
      const response = await fetch(`http://localhost:8000/api/policy/latest?${params}`);
      const data = await response.json();
      
      setPolicies(data.policies);
    } catch (error) {
      console.error('Error fetching policies:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/policy/stats?days=30');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const triggerManualCheck = async () => {
    try {
      setRefreshing(true);
      await fetch('http://localhost:8000/api/policy/trigger-check', { method: 'POST' });
      
      // Wait a few seconds then refresh
      setTimeout(() => {
        fetchPolicies();
        fetchStats();
        setRefreshing(false);
      }, 3000);
    } catch (error) {
      console.error('Error triggering check:', error);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
    fetchStats();
  }, [filterSector, filterOpportunity, filterSource]);

  const getOpportunityColor = (level: string) => {
    switch (level) {
      case 'High': return 'bg-green-500';
      case 'Medium': return 'bg-yellow-500';
      case 'Low': return 'bg-gray-400';
      default: return 'bg-gray-400';
    }
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return 'text-green-600';
    if (score < -0.3) return 'text-red-600';
    return 'text-gray-600';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffHours < 48) return 'Yesterday';
    return date.toLocaleDateString();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Policy Opportunity Detector</h1>
          <p className="text-muted-foreground mt-1">
            Automated tracking of government policies, budgets, and announcements
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={triggerManualCheck} disabled={refreshing}>
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Checking...' : 'Check Now'}
          </Button>
          <Button>
            <Bell className="w-4 h-4 mr-2" />
            Setup Alerts
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Policies (30d)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_policies}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">High Opportunity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {stats.by_opportunity_level['High'] || 0}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">PIB Updates</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.by_source['PIB'] || 0}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">News Articles</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(stats.by_source['Economic Times'] || 0) + (stats.by_source['Reuters India'] || 0)}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 items-center">
            <Filter className="w-5 h-5 text-muted-foreground" />
            
            <Select value={filterSector} onValueChange={setFilterSector}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Sector" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sectors</SelectItem>
                <SelectItem value="Banking">Banking</SelectItem>
                <SelectItem value="Infrastructure">Infrastructure</SelectItem>
                <SelectItem value="Energy">Energy</SelectItem>
                <SelectItem value="Pharma">Pharma</SelectItem>
                <SelectItem value="Auto">Auto</SelectItem>
                <SelectItem value="IT">IT</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterOpportunity} onValueChange={setFilterOpportunity}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Opportunity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                <SelectItem value="High">High</SelectItem>
                <SelectItem value="Medium">Medium</SelectItem>
                <SelectItem value="Low">Low</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterSource} onValueChange={setFilterSource}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Source" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sources</SelectItem>
                <SelectItem value="PIB">PIB</SelectItem>
                <SelectItem value="Economic Times">Economic Times</SelectItem>
                <SelectItem value="Reuters India">Reuters India</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Policy Feed */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-8">Loading policies...</div>
        ) : policies.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              No policies found. Try adjusting filters or trigger a manual check.
            </CardContent>
          </Card>
        ) : (
          policies.map((policy) => (
            <Card key={policy.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className={getOpportunityColor(policy.opportunity_level)}>
                        {policy.opportunity_level}
                      </Badge>
                      <Badge variant="outline">{policy.source}</Badge>
                      <span className="text-sm text-muted-foreground flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(policy.published_date)}
                      </span>
                    </div>
                    <CardTitle className="text-xl">{policy.title}</CardTitle>
                  </div>
                  {policy.source_url && (
                    <Button variant="ghost" size="sm" asChild>
                      <a href={policy.source_url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </Button>
                  )}
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">{policy.summary}</p>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-medium mb-1">Affected Sectors</div>
                    <div className="flex flex-wrap gap-1">
                      {policy.sectors && policy.sectors.length > 0 ? (
                        policy.sectors.map((sector) => (
                          <Badge key={sector} variant="secondary">{sector}</Badge>
                        ))
                      ) : (
                        <span className="text-sm text-muted-foreground">Not identified</span>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium mb-1">Impacted Stocks</div>
                    <div className="flex flex-wrap gap-1">
                      {policy.affected_stocks && policy.affected_stocks.length > 0 ? (
                        policy.affected_stocks.slice(0, 5).map((stock) => (
                          <Badge key={stock} variant="outline">{stock}</Badge>
                        ))
                      ) : (
                        <span className="text-sm text-muted-foreground">Not identified</span>
                      )}
                      {policy.affected_stocks && policy.affected_stocks.length > 5 && (
                        <Badge variant="outline">+{policy.affected_stocks.length - 5} more</Badge>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-between items-center text-sm pt-2 border-t">
                  {policy.budget_allocation && (
                    <div className="flex items-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      <span className="font-medium">Budget:</span>
                      <span>₹{policy.budget_allocation.toLocaleString()} Cr</span>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-1">
                    <span className="font-medium">Sentiment:</span>
                    <span className={getSentimentColor(policy.sentiment_score)}>
                      {policy.sentiment_score > 0 ? 'Positive' : policy.sentiment_score < 0 ? 'Negative' : 'Neutral'}
                      ({policy.sentiment_score.toFixed(2)})
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
```

---

## 12-Week Comprehensive Roadmap

### Phase 1: Foundation Infrastructure (Weeks 1-3)

**Week 1: Job Queue & Caching**
- ✅ Redis installation via docker-compose
- ✅ Celery app configuration with beat scheduler
- ✅ Policy tracking tasks setup (DONE last week)
- ✅ Database migrations for policies table (DONE last week)
- Feature Store schema design

**Week 2: Feature Store Implementation**
- Create `feature_store` table (PostgreSQL JSONB)
- Implement `FeatureStoreService` with read/write methods
- Migrate Research endpoint to write features
- Add Redis caching layer for features
- API endpoints: `/features/{symbol}`, `/predictions/{symbol}`

**Week 3: React Query Migration**
- Install `@tanstack/react-query`
- Create custom hooks: `useDashboard`, `usePortfolio`, `useWatchlist`
- Migrate Dashboard page from TradingContext
- Add loading skeletons and error boundaries
- Archive cleanup (move old markdown docs)

### Phase 2: Advanced Features (Weeks 4-6)

**Week 4: Enhanced Screener**
- Advanced filters: ML score, pattern type, momentum rank
- Multi-condition builder UI (AND/OR logic)
- Preset strategies (Breakout Momentum, Value + Growth)
- Export to CSV functionality
- Real-time data updates via WebSocket

**Week 5: ML Explainability**
- Install SHAP library (`pip install shap`)
- Implement SHAP value computation in training service
- Create `/research/{symbol}/explainability` endpoint
- Frontend: SHAP waterfall chart component
- Store explanations in Feature Store

**Week 6: Complete Indicator Library**
- Add missing indicators: ADX, ATR, Stochastic, VWAP
- Volume profile analysis
- Multi-timeframe indicator support (1D, 1W, 1M)
- Indicator comparison tool
- Custom indicator builder (future enhancement)

### Phase 3: Portfolio & F&O (Weeks 7-9)

**Week 7: Advanced Portfolio Optimizers**
- Black-Litterman model implementation
- Risk Parity optimizer
- CVaR (Conditional Value at Risk) optimizer
- Constraint builder: sector limits, concentration caps
- Backtesting framework for strategies

**Week 8: F&O Terminal - Phase 1**
- Options chain data integration (NSE API)
- Greeks calculation (Delta, Gamma, Theta, Vega)
- IV surface visualization
- Max pain calculator
- PCR (Put-Call Ratio) analysis

**Week 9: F&O Terminal - Phase 2**
- Strategy builder: Straddle, Strangle, Iron Condor, Butterfly
- P&L calculator with breakeven analysis
- Margin calculator
- Strategy scanner (find profitable setups)
- Risk/reward visualizations

### Phase 4: Production Features (Weeks 10-12)

**Week 10: Alerts Engine**
- Alerts database schema (user_id, symbol, condition, threshold)
- Alert evaluation worker (Celery task every 5 min)
- Notification channels: Email, SMS, Push
- Alert management UI
- Alert history and performance tracking

**Week 11: Reports & Analytics**
- Async report generation (Celery tasks)
- PDF export using ReportLab
- Scheduled reports (daily/weekly/monthly)
- Portfolio performance attribution
- Tax harvesting recommendations

**Week 12: Observability & Polish**
- OpenTelemetry instrumentation
- Grafana dashboards (API latency, cache hit rate, ML accuracy)
- Error tracking with Sentry
- User settings persistence (theme, watchlist, preferences)
- Performance optimization and load testing

---

## Execution Order

### Last Week (Completed)

- Redis & Celery setup (docker-compose, app config)
- Policy tracking tasks setup (Celery beat)
- Database migrations for policies table

### Immediate Priority (This Week)

1. ✅ **Create this consolidated plan** (DONE)
2. **Push current code to GitHub** (create feature branch, PR)
3. **Implement Policy Tracker Service** (scrapers + NLP)
4. **Build Policy API endpoints**
5. **Redesign Policy.tsx** frontend
6. **Install NLP dependencies** (spaCy, FinBERT)
7. **Test end-to-end** policy tracking

### Next Priorities (Weeks 2-3)

1. Feature Store database schema
2. FeatureStoreService implementation
3. React Query setup and Dashboard migration
4. Archive cleanup

### Medium-Term (Weeks 4-9)

1. Enhanced screener with ML filters
2. SHAP explainability
3. Complete indicator library
4. Portfolio optimizers (Black-Litterman, Risk Parity)
5. F&O Terminal with options chain

### Long-Term (Weeks 10-12)

1. Alerts engine
2. Async report generation
3. Observability stack (OpenTelemetry, Grafana)
4. User settings persistence

---

## Success Metrics

### Policy Opportunity Detector
- ✅ Automated scraping from 3+ sources (PIB, News sites)
- ✅ 30-minute check interval via Celery beat
- ✅ NLP analysis with sector/stock mapping
- ✅ Frontend displaying policy feed (not upload form)
- Target: 50+ policies tracked per month

### Feature Store
- All pages reading from unified data layer
- Sub-100ms cache hit latency (Redis)
- 90%+ cache hit rate
- Feature versioning for ML experiments

### ML Explainability
- SHAP values computed for all predictions
- Interactive waterfall charts on frontend
- User trust increase (qualitative feedback)

### F&O Terminal
- Real-time options chain data
- Greeks accuracy within 1% of exchange
- 10+ strategy templates available
- P&L calculator with commission modeling

### Alerts Engine
- Alert latency < 5 minutes from trigger
- Multi-channel delivery (Email, SMS, Push)
- 99% delivery success rate
- User engagement: 50%+ alerts actioned

### Overall Platform
- API response time: p95 < 500ms, p99 < 2s
- Cache hit rate > 85%
- ML model accuracy > 65% (directional prediction)
- Frontend load time < 2s (LCP)
- Zero critical bugs in production

---

## Notes & Considerations

### Technical Debt to Address
1. **Currency mixing** in portfolio calculations (₹ vs $)
2. **TradingContext** - keep mock for now; later migrate to read-only backend data APIs (no trading).
3. **Error handling** - silent failures in Dashboard/Research
4. **Ambiguous P&L formulas** - standardize calculations
5. **Chart safety guards** - proper null checks

### Broker Integrations Policy
- No real broker integrations until production. Keep TradingContext using mock data; disable any broker API calls for trading/order placement. This applies across backend services and frontend UI (only paper/demo modes enabled).
- Read-only market/data fetching may be added for research and dashboards, but absolutely no trading/order endpoints until production sign-off.

### Repository Hygiene Note
- All legacy Markdown documentation has been moved under `archive/` and excluded by `.gitignore`, with two explicit exceptions that remain tracked in-place: `IMPLEMENTATION_PLAN.md` and `frontend/README.md`. If additional files should stay out of the archive, call them out and we’ll keep them in place.

### Future Enhancements (Post 12-Week Plan)
1. Real-time WebSocket data feeds
2. Social sentiment analysis (Twitter, Reddit)
3. Earnings calendar integration
4. Backtesting engine for strategies
5. Mobile app (React Native)
6. Multi-user support with authentication
7. Subscription/pricing tiers

### Infrastructure Requirements
- **Redis**: 2GB RAM minimum
- **PostgreSQL**: 10GB storage for Feature Store
- **Celery Workers**: 2 workers for policy tracking + ML training
- **NLP Models**: ~1GB disk space (spaCy + FinBERT)

### Risk Mitigation
- **Web scraping failures**: Implement retry logic with exponential backoff
- **Rate limiting**: Respect robots.txt, add delays between requests
- **LinkedIn access**: May require API key or Selenium with authentication
- **Data quality**: Validate scraped content before NLP analysis
- **Model drift**: Monitor ML performance, retrain monthly

---

## Conclusion

This implementation plan transforms the AI Stock Backend from prototype to production-grade platform. The immediate focus is **Policy Opportunity Auto-Tracking**, followed by systematic execution of the 12-week roadmap covering Feature Store, ML explainability, advanced screeners, portfolio optimizers, F&O terminal, alerts engine, and observability.

**Next Action**: Push current code to GitHub, then execute Week 1 tasks (Redis, Celery, Policy Tracker).

**Status**: Ready for execution. No blockers identified.
