from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..services.gemini_service import GeminiService
from ..services.groq_service import GroqService
from ..services.openai_service import OpenAIService
from ..services.anthropic_service import AnthropicService
from ..services.ollama_service import OllamaService

@dataclass
class AIServiceConfig:
    name: str
    service_class: Any
    requires_api_key: bool = True
    is_local: bool = False
    is_template: bool = False

class AIConfigManager:
    """Gestionnaire de configuration des services IA"""
    
    def __init__(self):
        self.available_models = {
            "🆓 GRATUITS (BYOK)": {
                "Google Gemini": AIServiceConfig("Google Gemini", GeminiService, requires_api_key=True),
                "Groq (Llama 3)": AIServiceConfig("Groq (Llama 3)", GroqService, requires_api_key=True),
            },
            "💰 PREMIUM (BYOK)": {
                "OpenAI GPT-4": AIServiceConfig("OpenAI GPT-4", OpenAIService, requires_api_key=True),
                "Claude (Anthropic)": AIServiceConfig("Claude (Anthropic)", AnthropicService, requires_api_key=True),
            },
            "🖥️ LOCAUX": {
                "Ollama": AIServiceConfig("Ollama", OllamaService, requires_api_key=False, is_local=True),
            },
            "📝 TEMPLATES": {
                "Template Basique": AIServiceConfig("Template Basique", None, requires_api_key=False, is_template=True),
                "Template Professionnel": AIServiceConfig("Template Professionnel", None, requires_api_key=False, is_template=True),
                "Template Moderne": AIServiceConfig("Template Moderne", None, requires_api_key=False, is_template=True),
                "Template Newsletter": AIServiceConfig("Template Newsletter", None, requires_api_key=False, is_template=True),
            }
        }
    
    def get_service_config(self, model_category: str, model_choice: str) -> Optional[AIServiceConfig]:
        """Récupère la configuration d'un service"""
        category = self.available_models.get(model_category, {})
        return category.get(model_choice)
    
    def get_categories(self):
        return list(self.available_models.keys())
    
    def get_models_in_category(self, category: str):
        return list(self.available_models.get(category, {}).keys())