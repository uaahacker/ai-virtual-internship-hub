"""
LLM Provider abstraction layer for chatbot.
Supports multiple AI providers (OpenRouter, OpenAI, etc.)
"""

import requests
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from the LLM."""
        pass


class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider implementation."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_base = 'https://openrouter.ai/api/v1'
        self.model = os.getenv('OPENROUTER_MODEL', 'mistralai/mistral-7b-instruct')
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment variables")
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using OpenRouter API."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'model': self.model,
                'messages': messages,
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 500),
                'top_p': kwargs.get('top_p', 0.9),
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using OpenAI API."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'model': self.model,
                'messages': messages,
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 500),
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")


class MockProvider(LLMProvider):
    """Mock provider for testing and development."""
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a mock response."""
        last_user_message = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                last_user_message = msg.get('content', '').lower()
                break
        
        # Simple mock responses based on keywords
        if 'skill' in last_user_message:
            return "Based on your career goals, I recommend focusing on: Python, Web Development, Data Analysis, and Cloud Technologies. These are highly in-demand skills for freelancers."
        elif 'domain' in last_user_message or 'field' in last_user_message:
            return "Popular domains for freelancers include: Web Development, Data Science, Mobile Apps, UI/UX Design, AI/ML, and DevOps. Choose based on your interests and background."
        elif 'portfolio' in last_user_message:
            return "To improve your portfolio: 1) Showcase diverse projects, 2) Include real-world applications, 3) Write clear documentation, 4) Demonstrate problem-solving skills, 5) Keep it updated regularly."
        elif 'roadmap' in last_user_message or 'plan' in last_user_message:
            return "Here's a recommended roadmap: Week 1-2: Foundation building, Week 3-4: Intermediate projects, Week 5-6: Advanced skills, Week 7-8: Portfolio project, Week 9+: Freelancing preparation."
        else:
            return "That's a great question! I'm here to help with career guidance. Feel free to ask about skills to develop, domains to explore, portfolio improvements, or your learning roadmap."


class ProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _providers = {
        'openrouter': OpenRouterProvider,
        'openai': OpenAIProvider,
        'mock': MockProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_name: Optional[str] = None) -> LLMProvider:
        """Create a provider instance."""
        if provider_name is None:
            provider_name = os.getenv('LLM_PROVIDER', 'mock')
        
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            logger.warning(f"Unknown provider: {provider_name}, falling back to mock")
            provider_name = 'mock'
        
        try:
            return cls._providers[provider_name]()
        except Exception as e:
            logger.warning(f"Failed to initialize {provider_name} provider: {str(e)}, falling back to mock")
            return MockProvider()
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Register a custom provider."""
        cls._providers[name] = provider_class
