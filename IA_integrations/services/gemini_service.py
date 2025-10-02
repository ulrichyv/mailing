import streamlit as st
from typing import Optional
from .base_service import BaseAIService

class GeminiService(BaseAIService):
    """Service pour Google Gemini"""
    
    def generate_template(self, prompt: str, style_preference: str, **kwargs) -> str:
        try:
            if not self.api_key:
                st.warning("🔑 Clé API Google Gemini requise")
                return ""
            
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=self.api_key)
            system_prompt = self.get_system_prompt(style_preference)
            full_prompt = f"{system_prompt}\n\nDescription: {prompt}"
            
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            
            template_html = response.text.strip()
            template_html = self._clean_response(template_html)
            
            if self._is_valid_template(template_html):
                st.success("✅ Template généré avec Google Gemini 2.5 Flash")
                return template_html
            else:
                st.warning("Gemini a retourné un format invalide.")
                return ""
                
        except ImportError:
            st.error("📦 pip install -U google-genai")
            return ""
        except Exception as e:
            st.error(f"❌ Erreur Gemini: {e}")
            return ""
    
    def get_system_prompt(self, style_preference: str) -> str:
        return f"""Tu es un expert en création de templates email HTML professionnels.

CRÉE UN TEMPLATE EMAIL HTML avec ces CONTRAINTES STRICTES :

📧 COMPATIBILITÉ EMAIL :
- Tables HTML UNIQUEMENT (pas de div pour le layout)
- CSS INLINE SEULEMENT (style="")
- Largeur MAXIMUM : 600px
- Mobile-responsive

🎨 STYLE : {style_preference}

🔧 VARIABLES OBLIGATOIRES :
[Nom], [Prénom], [Entreprise], [Poste], [Ville], [Date]
[Produit], [Service], [Promotion], [Lien], [Site web]
[Téléphone], [Email], [Montant]

🚫 INTERDICTIONS :
- PAS d'explications avant/après
- PAS de commentaires HTML
- PAS de ```html ou backticks
- PAS de balises <head> avec <style>
- SEULEMENT le code HTML valide

✅ COMMENCE DIRECTEMENT PAR : <!DOCTYPE html>"""