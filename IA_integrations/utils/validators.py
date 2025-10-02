import re
from typing import Tuple, Optional

def validate_html(html_content: str) -> Tuple[bool, Optional[str]]:
    """Valide le contenu HTML"""
    if not html_content:
        return False, "Le contenu HTML est vide"
    
    if len(html_content) < 100:
        return False, "Le contenu HTML est trop court"
    
    required_tags = ['<html', '<body', '<table']
    for tag in required_tags:
        if tag not in html_content.lower():
            return False, f"Balise {tag} manquante"
    
    if html_content.count('<') < 5:
        return False, "Structure HTML insuffisante"
    
    return True, None

def validate_api_key(api_key: str, service_name: str) -> Tuple[bool, Optional[str]]:
    """Valide le format d'une clé API"""
    if not api_key:
        return False, f"Clé API {service_name} requise"
    
    if len(api_key) < 10:
        return False, f"Clé API {service_name} trop courte"
    
    # Validation basique selon le service
    if service_name.lower() == "openai" and not api_key.startswith('sk-'):
        return False, "Format de clé OpenAI invalide (doit commencer par sk-)"
    
    return True, None