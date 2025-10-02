from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import re

class BaseAIService(ABC):
    """Classe de base pour tous les services IA"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    def generate_template(self, prompt: str, style_preference: str, **kwargs) -> str:
        """Méthode abstraite pour générer un template"""
        pass
    
    @abstractmethod
    def get_system_prompt(self, style_preference: str) -> str:
        """Retourne le prompt système spécifique au service"""
        pass
    
    def _clean_response(self, response: str) -> str:
        """Nettoie la réponse IA"""
        if not response:
            return ""
            
        if '```html' in response:
            response = response.split('```html')[1].split('```')[0]
        elif '```' in response:
            response = response.split('```')[1].split('```')[0]
        
        lines = response.split('\n')
        html_lines = []
        in_html = False
        
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('<!DOCTYPE') or stripped_line.startswith('<html') or stripped_line.startswith('<table'):
                in_html = True
            if in_html:
                html_lines.append(line)
            if stripped_line.endswith('</html>') or stripped_line.endswith('</body>'):
                break
        
        cleaned_html = '\n'.join(html_lines)
        return cleaned_html.strip() if cleaned_html and len(cleaned_html) > 100 else response.strip()
    
    def _is_valid_template(self, html_content: str) -> bool:
        """Valide le template HTML généré"""
        if not html_content or len(html_content) < 200:
            return False
        
        required_tags = ['<html', '<body', '<table']
        for tag in required_tags:
            if tag not in html_content.lower():
                return False
        
        return html_content.count('<') >= 5