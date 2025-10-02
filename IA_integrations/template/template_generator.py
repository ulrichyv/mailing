import re
from typing import List, Dict, Any, Optional
from ..models.ai_config import AIConfigManager
from ..services.base_service import BaseAIService
from ..services.ollama_service import OllamaService
from .base_templates import BaseTemplates

class AITemplateGenerator:
    """Générateur principal de templates avec IA"""
    
    def __init__(self):
        self.config_manager = AIConfigManager()
        self.base_templates = BaseTemplates()
        self.standard_variables = [
            "Nom", "Prénom", "Entreprise", "Poste", "Ville", 
            "Date", "Produit", "Service", "Offre", "Promotion",
            "Lien", "Site web", "Téléphone", "Email", "Montant"
        ]

    def generate_template(self, prompt: str, model_category: str, model_choice: str, 
                         style_preference: str = "professional", api_key: str = None, 
                         ollama_model: str = "mistral:7b", ollama_url: str = "http://localhost:11434") -> str:
        """Génère un template HTML/CSS à partir d'un prompt"""
        try:
            service_config = self.config_manager.get_service_config(model_category, model_choice)
            
            if not service_config:
                return self.base_templates.generate_basic_template(prompt, style_preference)
            
            if service_config.is_template:
                # Utiliser les templates prédéfinis
                template_method_name = f"generate_{model_choice.lower().replace(' ', '_').replace('(', '').replace(')', '')}_template"
                template_method = getattr(self.base_templates, template_method_name, None)
                if template_method:
                    return template_method(prompt, style_preference)
                else:
                    return self.base_templates.generate_basic_template(prompt, style_preference)
            
            # Utiliser les services IA
            service_instance: BaseAIService = service_config.service_class(api_key=api_key)
            
            if model_choice == "Ollama":
                template_html, _ = service_instance.generate_template(
                    prompt, style_preference, 
                    ollama_model=ollama_model, 
                    ollama_url=ollama_url
                )
                return template_html
            else:
                return service_instance.generate_template(prompt, style_preference)
            
        except Exception as e:
            import streamlit as st
            st.error(f"❌ Erreur lors de la génération: {e}")
            return self.base_templates.generate_basic_template(prompt, style_preference)
    
    def get_template_variables(self, html_content: str) -> List[str]:
        """Extrait les variables du template HTML"""
        variables = re.findall(r'\[(.*?)\]', html_content)
        return list(set(variables))
    
    def get_variable_categories(self) -> Dict[str, Any]:
        """Retourne les catégories de variables organisées"""
        return {
            "👤 Informations Personnelles": {
                "variables": ["Nom", "Prénom", "Email", "Téléphone", "Poste"],
                "description": "Informations de contact du destinataire",
                "icon": "👤"
            },
            "🏢 Informations Entreprise": {
                "variables": ["Entreprise", "Ville", "Site web", "Adresse", "Secteur"],
                "description": "Informations sur l'entreprise",
                "icon": "🏢"
            },
            "🛍️ Offre & Produits": {
                "variables": ["Produit", "Service", "Offre", "Promotion", "Montant", "Prix"],
                "description": "Détails de l'offre commerciale",
                "icon": "🛍️"
            },
            "📅 Calendrier": {
                "variables": ["Date", "DateLimite", "DateDébut", "DateFin"],
                "description": "Dates importantes",
                "icon": "📅"
            },
            "🔗 Navigation": {
                "variables": ["Lien", "LienProduit", "LienSite", "LienDésabonnement"],
                "description": "Liens et URLs",
                "icon": "🔗"
            },
            "🎯 Appels à l'action": {
                "variables": ["CTA", "Bouton", "Action", "Urgence"],
                "description": "Textes pour les boutons et actions",
                "icon": "🎯"
            },
            "🔤 Autres Variables": {
                "variables": [],
                "description": "Variables personnalisées détectées",
                "icon": "🔤"
            }
        }
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extrait le texte brut du HTML"""
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text