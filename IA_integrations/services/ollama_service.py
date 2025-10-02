import requests
import streamlit as st
from typing import Tuple
from .base_service import BaseAIService

class OllamaService(BaseAIService):
    """Service pour Ollama (local)"""
    
    def generate_template(self, prompt: str, style_preference: str, **kwargs) -> Tuple[str, list]:
        debug_info = []
        ollama_model = kwargs.get('ollama_model', 'mistral:7b')
        ollama_url = kwargs.get('ollama_url', 'http://localhost:11434')
        
        try:
            if not self._check_ollama_connection(ollama_url):
                st.warning("🚫 Ollama n'est pas accessible.")
                return "", debug_info
            
            url = f"{ollama_url}/api/generate"
            system_prompt = self._get_optimized_prompt(style_preference, prompt)
            
            payload = {
                "model": ollama_model,
                "prompt": system_prompt,
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.8, "num_predict": 800, "top_k": 20}
            }
            
            response = requests.post(url, json=payload, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                raw_response = result["response"].strip()
                template_html = self._clean_response(raw_response)
                
                if self._is_valid_template(template_html):
                    debug_info.append("✅ Template valide")
                    return template_html, debug_info
                else:
                    debug_info.append("⚠️ Template invalide")
                    return "", debug_info
            else:
                debug_info.append(f"❌ Erreur HTTP: {response.status_code}")
                return "", debug_info
                        
        except Exception as e:
            debug_info.append(f"❌ Erreur: {str(e)}")
            return "", debug_info
    
    def get_system_prompt(self, style_preference: str) -> str:
        return f"""Tu es un expert en création de templates email HTML. Crée un template email professionnel.

Style: {style_preference}
Contraintes: Tables HTML, CSS inline, largeur max 600px
Variables: [Nom], [Prénom], [Entreprise], [Poste], etc.

Retourne uniquement le code HTML."""

    def _get_optimized_prompt(self, style_preference: str, user_prompt: str) -> str:
        return f"""CRÉE UN EMAIL HTML SIMPLE ET RAPIDE.

RÈGLES STRICTES :
- Tables HTML uniquement, CSS inline
- Largeur max 600px
- Style: {style_preference}
- Variables: [Nom], [Prénom], [Entreprise]

BASÉ SUR: {user_prompt[:80]}

HTML SEULEMENT. DÉBUT: <!DOCTYPE html>"""

    def _check_ollama_connection(self, ollama_url: str) -> bool:
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model['name'] for model in models]
                status_text = f"✅ Ollama OK - {len(models)} modèle(s)"
                if models:
                    status_text += f" - {', '.join(model_names[:2])}"
                    if len(models) > 2:
                        status_text += "..."
                st.sidebar.success(status_text)
                return True
            else:
                st.sidebar.error(f"❌ Ollama erreur {response.status_code}")
                return False
        except Exception as e:
            st.sidebar.error(f"❌ Ollama inaccessible: {e}")
            return False