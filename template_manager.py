import streamlit as st
import re
from datetime import datetime
from data_manager import save_email_templates, save_sms_templates

class TemplateManager:
    """Gestionnaire centralisé des templates email et SMS"""
    
    def __init__(self):
        # S'assurer que sms_templates existe dans session_state
        if 'sms_templates' not in st.session_state:
            st.session_state.sms_templates = {}
            
        self.email_templates = st.session_state.email_templates
        self.sms_templates = st.session_state.sms_templates
    
    def extract_variables(self, content):
        """Extrait les variables d'un contenu (support [var] et {var})"""
        if not content:
            return []
        
        # Support pour les deux formats : [var] et {var}
        bracket_vars = set(re.findall(r'\[(.*?)\]', content))
        curly_vars = set(re.findall(r'\{(.*?)\}', content))
        
        return list(bracket_vars.union(curly_vars))
    
    def convert_email_to_sms(self, email_template_name, sms_template_name=None):
        """Convertit un template email en template SMS"""
        if email_template_name not in self.email_templates:
            return False, "Template email non trouvé"
        
        email_template = self.email_templates[email_template_name]
        
        # Générer le contenu SMS à partir du texte email
        sms_content = self._generate_sms_from_email(email_template)
        
        if not sms_template_name:
            sms_template_name = f"SMS - {email_template_name}"
        
        # Sauvegarder le template SMS
        self.sms_templates[sms_template_name] = {
            "content": sms_content,
            "char_count": len(sms_content),
            "created_at": datetime.now().isoformat(),
            "variables": self.extract_variables(sms_content),
            "source": f"converted_from_email:{email_template_name}",
            "original_email_template": email_template_name
        }
        
        save_sms_templates(self.sms_templates)
        st.session_state.sms_templates = self.sms_templates
        
        return True, sms_template_name
    
    def _generate_sms_from_email(self, email_template):
        """Génère un contenu SMS intelligent à partir d'un template email"""
        # Priorité : texte brut > HTML converti
        text_content = email_template.get("text", "")
        
        if not text_content and email_template.get("html"):
            # Convertir HTML en texte pour SMS
            text_content = self._html_to_sms_text(email_template.get("html", ""))
        
        # Optimiser pour SMS (160 caractères)
        optimized_sms = self._optimize_for_sms(text_content)
        
        return optimized_sms
    
    def _html_to_sms_text(self, html_content):
        """Convertit le HTML en texte pour SMS"""
        if not html_content:
            return ""
        # Supprimer les balises HTML
        text = re.sub(r'<[^>]+>', ' ', html_content)
        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        # Raccourcir si nécessaire
        if len(text) > 150:
            text = text[:147] + "..."
        return text
    
    def _optimize_for_sms(self, text):
        """Optimise le texte pour les limites SMS"""
        if not text:
            return ""
            
        # Remplacer les variables [var] par {var} pour SMS
        text = re.sub(r'\[(.*?)\]', r'{\1}', text)
        
        # Raccourcir intelligemment si nécessaire
        if len(text) > 160:
            # Conserver le début qui contient généralement l'essentiel
            sentences = text.split('.')
            optimized = ""
            for sentence in sentences:
                if len(optimized + sentence + '.') <= 155:  # Marge pour "..."
                    optimized += sentence + '.'
                else:
                    break
            if not optimized:
                optimized = text[:155]
            text = optimized + ".." if len(optimized) < len(text) else optimized
        
        return text.strip()
    
    def get_shared_variables(self, email_template_name, sms_template_name):
        """Retourne les variables communes entre deux templates"""
        if email_template_name not in self.email_templates or sms_template_name not in self.sms_templates:
            return []
            
        email_vars = set(self.email_templates[email_template_name].get('variables', []))
        sms_vars = set(self.sms_templates[sms_template_name].get('variables', []))
        
        return list(email_vars.intersection(sms_vars))