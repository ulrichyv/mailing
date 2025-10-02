import streamlit as st
from .base_service import BaseAIService

class AnthropicService(BaseAIService):
    """Service pour Claude (Anthropic)"""
    
    def generate_template(self, prompt: str, style_preference: str, **kwargs) -> str:
        try:
            if not self.api_key:
                st.warning("🔑 Clé API Anthropic requise")
                return ""
            
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            system_prompt = self.get_system_prompt(style_preference)
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            template_html = response.content[0].text.strip()
            template_html = self._clean_response(template_html)
            
            if self._is_valid_template(template_html):
                st.success("✅ Template généré avec Claude (Anthropic)")
                return template_html
            else:
                st.warning("Claude a retourné une réponse invalide.")
                return ""
                
        except ImportError:
            st.error("📦 pip install anthropic")
            return ""
        except Exception as e:
            st.error(f"❌ Erreur Anthropic: {e}")
            return ""
    
    def get_system_prompt(self, style_preference: str) -> str:
        return f"""Tu es un expert en création de templates email HTML/CSS. 

Crée un template email professionnel avec:
- Tables HTML pour la compatibilité Outlook/Gmail
- CSS inline uniquement
- Largeur maximum de 600px
- Design responsive
- Variables de personnalisation: [Nom], [Prénom], [Entreprise], [Poste], etc.
- Style: {style_preference}

Retourne uniquement le code HTML complet, sans commentaires ni explications."""