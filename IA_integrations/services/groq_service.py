import requests
import streamlit as st
from .base_service import BaseAIService

class GroqService(BaseAIService):
    """Service pour Groq API"""
    
    def generate_template(self, prompt: str, style_preference: str, **kwargs) -> str:
        try:
            if not self.api_key:
                st.warning("🔑 Clé API Groq requise")
                return ""
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            system_prompt = self.get_system_prompt(style_preference)
            
            # MODÈLES GROQ DISPONIBLES - VERSION CORRIGÉE
            selected_model = "llama-3.3-70b-versatile"  # Modèle actuel de Groq
            
            data = {
                "model": selected_model,  # CORRECTION ICI
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": False
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                template_html = result["choices"][0]["message"]["content"].strip()
                template_html = self._clean_response(template_html)
                
                if self._is_valid_template(template_html):
                    st.success(f"✅ Template généré avec Groq ({selected_model})")
                    return template_html
                else:
                    st.warning("Groq a retourné un format invalide.")
                    return ""
            else:
                # Message d'erreur détaillé
                try:
                    error_detail = response.json()
                    st.error(f"❌ Erreur Groq {response.status_code}: {error_detail.get('error', {}).get('message', 'Unknown error')}")
                except:
                    st.error(f"❌ Erreur Groq {response.status_code}")
                return ""
                
        except Exception as e:
            st.error(f"❌ Erreur avec Groq: {e}")
            return ""
    
    def get_system_prompt(self, style_preference: str) -> str:
        return f"""Tu es un expert en création de templates email HTML/CSS. Crée un template email responsive.

CONTRAINTES STRICTES :
- Tables HTML pour la compatibilité email
- CSS inline uniquement
- Largeur max: 600px
- Mobile-friendly
- Variables: [Nom], [Prénom], [Entreprise], [Poste], etc.
- Style: {style_preference}

Retourne UNIQUEMENT le code HTML sans commentaires, sans backticks, sans explications.
Commence directement par <!DOCTYPE html>"""