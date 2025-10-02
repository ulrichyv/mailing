import streamlit as st
from .base_service import BaseAIService

class OpenAIService(BaseAIService):
    """Service pour OpenAI GPT-4"""
    
    def generate_template(self, prompt: str, style_preference: str, **kwargs) -> str:
        try:
            if not self.api_key:
                st.warning("🔑 Clé API OpenAI requise")
                return ""
            
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            system_prompt = self.get_system_prompt(style_preference)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            template_html = response.choices[0].message.content.strip()
            template_html = self._clean_response(template_html)
            
            if self._is_valid_template(template_html):
                st.success("✅ Template généré avec OpenAI GPT-4")
                return template_html
            else:
                st.warning("OpenAI a retourné une réponse invalide.")
                return ""
                
        except ImportError:
            st.error("📦 pip install openai")
            return ""
        except Exception as e:
            st.error(f"❌ Erreur OpenAI: {e}")
            return ""
    
    def get_system_prompt(self, style_preference: str) -> str:
        return f"""Tu es un expert en création de templates email HTML/CSS. Crée un template email responsive et compatible.

CONTRAINTES :
- Tables HTML pour la compatibilité
- CSS inline uniquement
- Largeur max: 600px
- Mobile-friendly
- Variables: [Nom], [Prénom], [Entreprise], etc.
- Style: {style_preference}

Retourne UNIQUEMENT le code HTML sans commentaires."""