# app/agents/base.py

import ollama
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all LLM-powered trading agents.
    Provides a standardized interface for interacting with Ollama.
    """
    
    def __init__(self, name: str, role: str, model: Optional[str] = None):
        self.name = name
        self.role = role
        self.model = model or settings.OLLAMA_MODEL
        # Set a generous timeout for local inference
        self.client = ollama.AsyncClient(
            host=settings.OLLAMA_BASE_URL,
            timeout=settings.OLLAMA_TIMEOUT
        )
        
    async def chat(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send a chat request to the local Ollama instance (async).
        """
        try:
            # Quick health check for connection
            logger.info(f"Agent {self.name} checking Ollama connectivity at {settings.OLLAMA_BASE_URL}...")
            
            response = await self.client.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error communicating with Ollama for agent {self.name}: {e}")
            if "Connection" in str(e) or "Refused" in str(e):
                return f"Error: Cannot connect to Ollama at {settings.OLLAMA_BASE_URL}. Ensure Ollama is running."
            return f"Error: {str(e)}"

    def format_prompt(self, template: str, **kwargs) -> str:
        """
        Helper to format prompt templates.
        """
        return template.format(**kwargs)
