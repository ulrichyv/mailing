import streamlit as st
import re
import requests
import json
import subprocess
from datetime import datetime

class AITemplateGenerator:
    def __init__(self):
        # Nouvelle organisation BYOK
        self.available_models = {
            "🆓 GRATUITS (BYOK)": {
                "Google Gemini": self._generate_with_gemini,
                "Groq (Llama 3)": self._generate_with_groq,
            },
            "💰 PREMIUM (BYOK)": {
                "OpenAI GPT-4": self._generate_with_openai,
                "Claude (Anthropic)": self._generate_with_anthropic,
            },
            "🖥️ LOCAUX": {
                "Ollama": self._generate_with_ollama,
            },
            "📝 TEMPLATES": {
                "Template Basique": self._generate_basic_template,
                "Template Professionnel": self._generate_professional_template,
                "Template Moderne": self._generate_modern_template,
                "Template Newsletter": self._generate_newsletter_template,
            }
        }
        
        self.standard_variables = [
            "Nom", "Prénom", "Entreprise", "Poste", "Ville", 
            "Date", "Produit", "Service", "Offre", "Promotion",
            "Lien", "Site web", "Téléphone", "Email", "Montant"
        ]

    def get_variable_categories(self):
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
    
    def generate_template(self, prompt, model_category, model_choice, style_preference="professional", 
                         api_key=None, ollama_model="mistral:7b", ollama_url="http://localhost:11434"):
        """Génère un template HTML/CSS à partir d'un prompt"""
        try:
            if model_category in self.available_models:
                if model_choice in self.available_models[model_category]:
                    generator = self.available_models[model_category][model_choice]
                    
                    if model_choice == "Ollama":
                        template_html, debug_info = generator(prompt, style_preference, api_key, ollama_model, ollama_url)
                        return template_html
                    else:
                        return generator(prompt, style_preference, api_key, ollama_model, ollama_url)
            
            # Fallback au template basique
            return self._generate_basic_template(prompt, style_preference)
            
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération: {e}")
            return self._generate_basic_template(prompt, style_preference)

    # === MÉTHODES DE GÉNÉRATION ===
    def _generate_with_gemini(self, prompt, style_preference, api_key=None, ollama_model=None, ollama_url=None):
        """Génération avec le NOUVEAU SDK Google GenAI"""
        try:
            if not api_key:
                st.warning("🔑 Clé API Google Gemini requise")
                return self._generate_basic_template(prompt, style_preference)
            
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=api_key)
                
                system_prompt = self._get_gemini_system_prompt(style_preference)
                full_prompt = f"{system_prompt}\n\nDescription: {prompt}"
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=0)
                    )
                )
                
                template_html = response.text.strip()
                template_html = self._clean_ai_response(template_html)
                
                if self._is_valid_template(template_html):
                    st.success("✅ Template généré avec Google Gemini 2.5 Flash")
                    return template_html
                else:
                    st.warning("Gemini a retourné un format invalide.")
                    return self._generate_basic_template(prompt, style_preference)
                    
            except ImportError:
                st.error("📦 pip install -U google-genai")
                return self._generate_basic_template(prompt, style_preference)
            except Exception as e:
                st.error(f"❌ Erreur Gemini: {e}")
                return self._generate_basic_template(prompt, style_preference)
                
        except Exception as e:
            st.error(f"❌ Erreur inattendue avec Gemini: {e}")
            return self._generate_basic_template(prompt, style_preference)

    def _generate_with_groq(self, prompt, style_preference, api_key=None, ollama_model=None, ollama_url=None):
        """Génération avec Groq API"""
        try:
            if not api_key:
                st.warning("🔑 Clé API Groq requise")
                return self._generate_basic_template(prompt, style_preference)
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            system_prompt = self._get_groq_system_prompt(style_preference)
            
            data = {
                "model": "llama3-8b-8192",
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
                template_html = self._clean_ai_response(template_html)
                
                if self._is_valid_template(template_html):
                    st.success("✅ Template généré avec Groq (Llama 3)")
                    return template_html
                else:
                    st.warning("Groq a retourné un format invalide.")
                    return self._generate_basic_template(prompt, style_preference)
            else:
                error_msg = f"Erreur Groq: {response.status_code}"
                st.error(f"❌ {error_msg}")
                return self._generate_basic_template(prompt, style_preference)
                
        except Exception as e:
            st.error(f"❌ Erreur avec Groq: {e}")
            return self._generate_basic_template(prompt, style_preference)

    def _generate_with_ollama(self, prompt, style_preference, api_key=None, ollama_model="mistral:7b", ollama_url="http://localhost:11434"):
        debug_info = []
        try:
            if not self._check_ollama_connection(ollama_url):
                st.warning("🚫 Ollama n'est pas accessible.")
                return self._generate_basic_template(prompt, style_preference), debug_info
            
            OLLAMA_URL = f"{ollama_url}/api/generate"
            system_prompt = self._get_optimized_prompt(style_preference, prompt)
            
            payload = {
                "model": ollama_model,
                "prompt": system_prompt,
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.8, "num_predict": 800, "top_k": 20}
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                raw_response = result["response"].strip()
                template_html = self._clean_ollama_response(raw_response)
                
                if self._is_valid_template(template_html):
                    debug_info.append("✅ Template valide")
                    return template_html, debug_info
                else:
                    debug_info.append("⚠️ Template invalide")
                    return self._generate_enhanced_basic_template(prompt, style_preference), debug_info
            else:
                debug_info.append(f"❌ Erreur HTTP: {response.status_code}")
                return self._generate_enhanced_basic_template(prompt, style_preference), debug_info
                        
        except Exception as e:
            debug_info.append(f"❌ Erreur: {str(e)}")
            return self._generate_enhanced_basic_template(prompt, style_preference), debug_info

    def _generate_with_openai(self, prompt, style_preference, api_key=None, ollama_model=None, ollama_url=None):
        try:
            if not api_key:
                st.warning("🔑 Clé API OpenAI requise")
                return self._generate_basic_template(prompt, style_preference)
            
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                
                system_prompt = self._get_openai_system_prompt(style_preference)
                
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
                template_html = self._clean_ai_response(template_html)
                
                if self._is_valid_template(template_html):
                    st.success("✅ Template généré avec OpenAI GPT-4")
                    return template_html
                else:
                    st.warning("OpenAI a retourné une réponse invalide.")
                    return self._generate_basic_template(prompt, style_preference)
                    
            except Exception as e:
                st.error(f"❌ Erreur OpenAI: {e}")
                return self._generate_basic_template(prompt, style_preference)
                
        except Exception as e:
            st.error(f"❌ Erreur inattendue avec OpenAI: {e}")
            return self._generate_basic_template(prompt, style_preference)

    def _generate_with_anthropic(self, prompt, style_preference, api_key=None, ollama_model=None, ollama_url=None):
        try:
            if not api_key:
                st.warning("🔑 Clé API Anthropic requise")
                return self._generate_basic_template(prompt, style_preference)
            
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                
                system_prompt = self._get_anthropic_system_prompt(style_preference)
                
                response = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                template_html = response.content[0].text.strip()
                template_html = self._clean_ai_response(template_html)
                
                if self._is_valid_template(template_html):
                    st.success("✅ Template généré avec Claude (Anthropic)")
                    return template_html
                else:
                    st.warning("Claude a retourné une réponse invalide.")
                    return self._generate_basic_template(prompt, style_preference)
                    
            except Exception as e:
                st.error(f"❌ Erreur Anthropic: {e}")
                return self._generate_basic_template(prompt, style_preference)
                
        except Exception as e:
            st.error(f"❌ Erreur inattendue avec Anthropic: {e}")
            return self._generate_basic_template(prompt, style_preference)

    # === TEMPLATES PRÉDÉFINIS ===
    def _generate_basic_template(self, prompt, style_preference, api_key=None, ollama_model=None, ollama_url=None):
        styles_config = {
            "professional": {"primary": "#2563eb", "secondary": "#1e40af", "bg_color": "#f8fafc"},
            "modern": {"primary": "#7c3aed", "secondary": "#6d28d9", "bg_color": "#fafafa"},
            "creative": {"primary": "#dc2626", "secondary": "#b91c1c", "bg_color": "#fef7ed"},
            "minimalist": {"primary": "#000000", "secondary": "#374151", "bg_color": "#ffffff"},
            "warm": {"primary": "#ea580c", "secondary": "#c2410c", "bg_color": "#fef7ed"}
        }
        
        style = styles_config.get(style_preference, styles_config["professional"])
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: {style['bg_color']};">
    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <tr>
            <td style="padding: 30px 25px; background: linear-gradient(135deg, {style['primary']}, {style['secondary']}); text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">[Entreprise]</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Votre partenaire de confiance</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 40px 30px;">
                <h2 style="color: #1f2937; margin: 0 0 20px 0; font-size: 22px;">Bonjour [Prénom] [Nom],</h2>
                <p style="color: #4b5563; line-height: 1.6; font-size: 16px; margin: 0 0 20px 0;">
                    Nous sommes ravis de vous contacter de la part de <strong>[Entreprise]</strong>. 
                    Votre profil en tant que <strong>[Poste]</strong> à <strong>[Entreprise]</strong> 
                    a retenu toute notre attention.
                </p>
                <p style="color: #4b5563; line-height: 1.6; font-size: 16px; margin: 0 0 30px 0;">
                    Nous pensons que notre solution <strong>[Produit]</strong> pourrait vous aider 
                    à atteindre vos objectifs plus efficacement.
                </p>
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; border-left: 4px solid {style['primary']}; margin: 25px 0;">
                    <h3 style="color: {style['primary']}; margin: 0 0 10px 0; font-size: 18px;">🎯 Offre Spéciale</h3>
                    <p style="color: #6b7280; margin: 0; font-size: 15px;">
                        Bénéficiez de <strong>[Promotion]</strong> sur [Produit] jusqu'au [Date] !
                    </p>
                </div>
                <table border="0" cellpadding="0" cellspacing="0" style="margin: 30px 0; text-align: center;">
                    <tr>
                        <td>
                            <a href="[Lien]" style="background: {style['primary']}; color: #ffffff; padding: 14px 35px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; font-size: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                Découvrir l'offre ›
                            </a>
                        </td>
                    </tr>
                </table>
                <p style="color: #6b7280; font-size: 14px; line-height: 1.5; margin: 30px 0 0 0;">
                    Cordialement,<br>
                    <strong>L'équipe [Entreprise]</strong><br>
                    📞 [Téléphone] | 🌐 [Site web]<br>
                    📧 [Email]
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding: 25px 30px; background: #f9fafb; text-align: center;">
                <p style="color: #9ca3af; font-size: 12px; line-height: 1.4; margin: 0;">
                    &copy; 2024 [Entreprise]. Tous droits réservés.<br>
                    <a href="#" style="color: {style['primary']}; text-decoration: none;">Se désabonner</a> • 
                    <a href="#" style="color: {style['primary']}; text-decoration: none;">Gérer mes préférences</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>'''

    def _generate_professional_template(self, prompt, style_preference, api_key=None, ollama_model=None, ollama_url=None):
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: #ffffff;">
        <tr>
            <td style="padding: 30px 20px; background: #2563eb; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px;">[Entreprise]</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Communication Professionnelle</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 40px 30px;">
                <h2 style="color: #1e293b; margin-top: 0;">Bonjour [Prénom] [Nom],</h2>
                <p style="color: #475569; line-height: 1.6; font-size: 16px;">
                    Nous sommes ravis de vous contacter concernant [Produit]. 
                    Votre entreprise <strong>[Entreprise]</strong> située à [Ville] représente 
                    un partenaire idéal pour nous.
                </p>
                <div style="background: #f1f5f9; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="color: #334155; margin-top: 0;">Offre Spéciale pour vous</h3>
                    <p style="color: #475569; margin: 10px 0;">
                        Bénéficiez de <strong>[Promotion]</strong> sur [Produit] jusqu'au [Date].
                    </p>
                </div>
                <table border="0" cellpadding="0" cellspacing="0" style="margin: 30px 0; text-align: center;">
                    <tr>
                        <td>
                            <a href="[Lien]" style="background: #2563eb; color: #ffffff; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Découvrir l'offre</a>
                        </td>
                    </tr>
                </table>
                <p style="color: #64748b; font-size: 14px;">
                    Cordialement,<br>
                    L'équipe [Entreprise]<br>
                    [Site web] | [Téléphone]
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px; background: #f8fafc; text-align: center;">
                <p style="color: #64748b; font-size: 14px; margin: 0;">
                    &copy; 2024 [Entreprise]. Tous droits réservés.<br>
                    <a href="#" style="color: #2563eb; text-decoration: none;">Se désabonner</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    def _generate_modern_template(self, prompt, style_preference, api_key=None, ollama_model=None, ollama_url=None):
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <tr>
            <td style="padding: 40px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: 300;">[Entreprise]</h1>
                <p style="color: rgba(255,255,255,0.8); margin: 15px 0 0 0; font-size: 16px;">Innovation & Excellence</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 50px 40px;">
                <h2 style="color: #2d3748; margin-top: 0; font-weight: 400;">Bonjour [Prénom],</h2>
                <p style="color: #4a5568; line-height: 1.7; font-size: 16px;">
                    Votre profil au sein de <strong>[Entreprise]</strong> en tant que <strong>[Poste]</strong> 
                    a retenu notre attention. Nous pensons que notre solution <strong>[Produit]</strong> 
                    pourrait considérablement optimiser vos processus.
                </p>
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 25px; border-radius: 10px; margin: 30px 0; text-align: center;">
                    <h3 style="color: #ffffff; margin: 0 0 10px 0;">Offre Exclusive</h3>
                    <p style="color: #ffffff; margin: 0; font-size: 18px; font-weight: 500;">
                        Économisez [Montant] jusqu'au [Date] !
                    </p>
                </div>
                <table border="0" cellpadding="0" cellspacing="0" style="margin: 40px 0; text-align: center;">
                    <tr>
                        <td>
                            <a href="[Lien]" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 15px 35px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: 500; letter-spacing: 0.5px;">Profiter de l'offre</a>
                        </td>
                    </tr>
                </table>
                <p style="color: #718096; font-size: 14px; text-align: center;">
                    Besoin d'informations ? Contactez-nous au [Téléphone] ou à [Email]
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding: 30px; background: #f7fafc; text-align: center;">
                <p style="color: #718096; font-size: 14px; margin: 0;">
                    &copy; 2024 [Entreprise]. [Site web]<br>
                    <a href="#" style="color: #667eea; text-decoration: none;">Gérer mes préférences</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    def _generate_newsletter_template(self, prompt, style_preference, api_key=None, ollama_model=None, ollama_url=None):
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', sans-serif;">
    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: #ffffff;">
        <tr>
            <td style="padding: 25px 20px; background: #dc2626; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Newsletter [Entreprise]</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">[Date]</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 30px 25px;">
                <h2 style="color: #1f2937; margin: 0 0 15px 0;">Bonjour [Prénom] !</h2>
                <p style="color: #4b5563; line-height: 1.6; margin: 0 0 20px 0;">
                    Voici les dernières actualités de [Entreprise] spécialement pour vous.
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding: 0 25px 20px 25px;">
                <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background: #fef2f2; border-radius: 8px; overflow: hidden;">
                    <tr>
                        <td style="padding: 20px;">
                            <h3 style="color: #dc2626; margin: 0 0 10px 0;">Nouveau [Produit]</h3>
                            <p style="color: #7f1d1d; line-height: 1.5; margin: 0 0 15px 0;">
                                Découvrez notre nouvelle gamme [Produit] avec une promotion exclusive de [Promotion].
                            </p>
                            <a href="[Lien]" style="color: #dc2626; text-decoration: none; font-weight: bold;">En savoir plus →</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td style="padding: 0 25px 20px 25px;">
                <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background: #f0f9ff; border-radius: 8px; overflow: hidden;">
                    <tr>
                        <td style="padding: 20px;">
                            <h3 style="color: #0369a1; margin: 0 0 10px 0;">Événement à [Ville]</h3>
                            <p style="color: #0c4a6e; line-height: 1.5; margin: 0 0 15px 0;">
                                Rencontrez-nous à notre prochain événement le [Date] dans votre ville.
                            </p>
                            <a href="[Lien]" style="color: #0369a1; text-decoration: none; font-weight: bold;">S'inscrire →</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td style="padding: 0 25px 30px 25px; text-align: center;">
                <a href="[Lien]" style="background: #dc2626; color: #ffffff; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Voir toutes les actualités
                </a>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px; background: #f8fafc; text-align: center;">
                <p style="color: #6b7280; font-size: 12px; margin: 0 0 10px 0;">
                    [Entreprise] - [Site web] - [Téléphone]<br>
                    [Adresse], [Ville]
                </p>
                <p style="color: #9ca3af; font-size: 11px; margin: 0;">
                    <a href="#" style="color: #6b7280; text-decoration: none;">Se désabonner</a> | 
                    <a href="#" style="color: #6b7280; text-decoration: none;">Gérer les préférences</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>"""

    def _generate_enhanced_basic_template(self, prompt, style_preference):
        prompt_lower = prompt.lower()
        if "newsletter" in prompt_lower:
            return self._generate_newsletter_template(prompt, style_preference)
        elif "promotion" in prompt_lower or "vente" in prompt_lower:
            return self._generate_promotion_template(prompt, style_preference)
        elif "commercial" in prompt_lower or "prospection" in prompt_lower:
            return self._generate_professional_template(prompt, style_preference)
        else:
            return self._generate_basic_template(prompt, style_preference)

    def _generate_promotion_template(self, prompt, style_preference):
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: #ffffff;">
        <tr>
            <td style="padding: 40px 30px; background: linear-gradient(135deg, #dc2626, #b91c1c); text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: bold;">🚀 PROMOTION EXCEPTIONNELLE !</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 15px 0 0 0; font-size: 18px;">[Promotion] sur [Produit]</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 50px 40px; text-align: center;">
                <h2 style="color: #1f2937; margin: 0 0 20px 0;">Bonjour [Prénom],</h2>
                <p style="color: #4b5563; line-height: 1.6; font-size: 18px; margin: 0 0 30px 0;">
                    Ne manquez pas cette opportunité unique ! Profitez de <strong>[Promotion]</strong> sur notre [Produit].
                </p>
                <div style="background: #fef2f2; padding: 25px; border-radius: 10px; border: 2px dashed #dc2626; margin: 30px 0;">
                    <h3 style="color: #dc2626; margin: 0 0 15px 0; font-size: 24px;">⏰ Offre limitée dans le temps !</h3>
                    <p style="color: #7f1d1d; margin: 0; font-size: 16px;">Valable jusqu'au [Date] seulement</p>
                </div>
                <table border="0" cellpadding="0" cellspacing="0" style="margin: 40px 0; text-align: center;">
                    <tr>
                        <td>
                            <a href="[Lien]" style="background: #dc2626; color: #ffffff; padding: 18px 45px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 18px; box-shadow: 0 4px 8px rgba(220, 38, 38, 0.3);">
                                J'en profite maintenant !
                            </a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    # === PROMPTS SYSTÈMES ===
    def _get_optimized_prompt(self, style_preference, user_prompt):
        return f"""CRÉE UN EMAIL HTML SIMPLE ET RAPIDE.

RÈGLES STRICTES :
- Tables HTML uniquement, CSS inline
- Largeur max 600px
- Style: {style_preference}
- Variables: [Nom], [Prénom], [Entreprise]

BASÉ SUR: {user_prompt[:80]}

HTML SEULEMENT. DÉBUT: <!DOCTYPE html>"""

    def _get_groq_system_prompt(self, style_preference):
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

    def _get_gemini_system_prompt(self, style_preference):
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

    def _get_openai_system_prompt(self, style_preference):
        return f"""Tu es un expert en création de templates email HTML/CSS. Crée un template email responsive et compatible.

CONTRAINTES :
- Tables HTML pour la compatibilité
- CSS inline uniquement
- Largeur max: 600px
- Mobile-friendly
- Variables: [Nom], [Prénom], [Entreprise], etc.
- Style: {style_preference}

Retourne UNIQUEMENT le code HTML sans commentaires."""
    
    def _get_anthropic_system_prompt(self, style_preference):
        return f"""Tu es un expert en création de templates email HTML/CSS. 

Crée un template email professionnel avec:
- Tables HTML pour la compatibilité Outlook/Gmail
- CSS inline uniquement
- Largeur maximum de 600px
- Design responsive
- Variables de personnalisation: [Nom], [Prénom], [Entreprise], [Poste], etc.
- Style: {style_preference}

Retourne uniquement le code HTML complet, sans commentaires ni explications."""

    def _is_valid_template(self, html_content):
        if not html_content or len(html_content) < 200:
            return False
        required_tags = ['<html', '<body', '<table']
        for tag in required_tags:
            if tag not in html_content.lower():
                return False
        if html_content.count('<') < 5:
            return False
        return True

    def _clean_ollama_response(self, response):
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
        if not cleaned_html or len(cleaned_html) < 100:
            return response.strip()
        return cleaned_html.strip()
    
    def _clean_ai_response(self, response):
        return self._clean_ollama_response(response)

    def get_template_variables(self, html_content):
        variables = re.findall(r'\[(.*?)\]', html_content)
        return list(set(variables))

    def _extract_text_from_html(self, html_content):
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _test_ollama_direct(self, ollama_model, test_prompt):
        try:
            model_name = ollama_model.split(':')[0]
            result = subprocess.run(
                ["ollama", "run", model_name, test_prompt],
                capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Timeout - Trop long"
        except Exception as e:
            return False, f"Erreur: {e}"

    def _check_ollama_connection(self, ollama_url):
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

# === FONCTIONS D'INTERFACE POUR LES VARIABLES ===
def get_smart_default_value(variable_name):
    """Retourne une valeur par défaut intelligente selon le nom de variable"""
    defaults = {
        # Informations personnelles
        "Nom": "Dupont",
        "Prénom": "Jean",
        "Email": "jean.dupont@email.com",
        "Téléphone": "+33 1 23 45 67 89",
        "Poste": "Directeur Marketing",
        
        # Entreprise
        "Entreprise": "Neurafrik",
        "Ville": "Paris",
        "Site web": "https://neurafrik.com",
        "Adresse": "123 Avenue des Champs-Élysées",
        "Secteur": "Technologie",
        
        # Offres
        "Produit": "Solution IA",
        "Service": "Service Premium",
        "Offre": "Offre Exclusive",
        "Promotion": "20% de réduction",
        "Montant": "199€",
        "Prix": "199€",
        
        # Dates
        "Date": "15 décembre 2024",
        "DateLimite": "31 décembre 2024",
        "DateDébut": "1 janvier 2024",
        "DateFin": "31 décembre 2024",
        
        # Liens
        "Lien": "https://neurafrik.com/offre",
        "LienProduit": "https://neurafrik.com/produit",
        "LienSite": "https://neurafrik.com",
        "LienDésabonnement": "https://neurafrik.com/desabonnement",
        
        # CTAs
        "CTA": "Découvrir l'offre",
        "Bouton": "Je profite de l'offre",
        "Action": "Télécharger maintenant",
        "Urgence": "Offre limitée !"
    }
    
    return defaults.get(variable_name, f"Valeur {variable_name}")

def organize_variables_by_category(detected_variables, categories):
    """Organise les variables détectées par catégorie"""
    organized = {}
    
    for var in detected_variables:
        found_category = None
        for category, info in categories.items():
            if var in info['variables']:
                found_category = category
                break
        
        if found_category:
            organized.setdefault(found_category, []).append(var)
        else:
            organized.setdefault("🔤 Autres Variables", []).append(var)
    
    return organized

def display_template_with_variables(template, style_choice):
    """Affiche un template avec interface de gestion des variables"""
    
    with st.expander(f"🎨 {template['name']} ({template['model']})", expanded=True):
        
        # Section variables
        st.markdown("### 🔧 Personnalisation des Variables")
        
        # Variables détectées
        detected_variables = template.get('variables', [])
        
        if detected_variables:
            st.success(f"🎯 {len(detected_variables)} variables détectées automatiquement")
            
            # Interface de gestion des variables
            final_html, variable_values = manage_template_variables_advanced(
                template['html'], 
                detected_variables
            )
            
            # Aperçu avec valeurs
            st.markdown("### 👀 Aperçu personnalisé")
            st.components.v1.html(final_html, height=500, scrolling=True)
            
        else:
            st.warning("ℹ️ Aucune variable détectée dans ce template")
            final_html = template['html']
            variable_values = {}
            st.components.v1.html(final_html, height=500, scrolling=True)
        
        # Actions
        st.markdown("### 💾 Téléchargement")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 Utiliser ce template", key=f"use_{id(template)}", use_container_width=True):
                st.session_state.selected_ai_template = template
                st.rerun()
        
        with col2:
            st.download_button(
                "📄 HTML original",
                template['html'],
                file_name=f"template_{style_choice}_original.html",
                use_container_width=True,
                help="Télécharger le template avec les variables [Nom]"
            )
        
        with col3:
            if variable_values:
                st.download_button(
                    "🚀 HTML personnalisé",
                    final_html,
                    file_name=f"template_{style_choice}_personnalise.html",
                    use_container_width=True,
                    help="Télécharger avec vos valeurs personnalisées"
                )

def manage_template_variables_advanced(template_html, detected_variables):
    """Interface avancée de gestion des variables"""
    
    ai_generator = AITemplateGenerator()
    categories = ai_generator.get_variable_categories()
    
    # Organiser les variables par catégorie
    organized_vars = organize_variables_by_category(detected_variables, categories)
    
    # Interface d'édition
    variable_values = {}
    
    st.markdown("#### 💾 Renseignez vos valeurs")
    
    # Afficher les catégories organisées
    for category, vars_list in organized_vars.items():
        category_info = categories.get(category, {"icon": "🔤", "description": "Variables personnalisées"})
        
        with st.expander(f"{category_info.get('icon', '🔤')} {category} ({len(vars_list)})", expanded=True):
            if category_info.get('description'):
                st.caption(f"📝 {category_info['description']}")
            
            cols = st.columns(2)
            for idx, var in enumerate(vars_list):
                with cols[idx % 2]:
                    # Valeur par défaut intelligente
                    default_value = get_smart_default_value(var)
                    
                    variable_values[var] = st.text_input(
                        f"**{var}**",
                        value=default_value,
                        placeholder=f"Entrez {var}...",
                        key=f"var_input_{var}",
                        help=f"Remplace [{var}] dans le template"
                    )
    
    # Variables personnalisées supplémentaires
    st.markdown("#### 🎨 Ajouter des variables personnalisées")
    custom_vars = st.text_area(
        "Variables supplémentaires (une par ligne)",
        placeholder="Exemple:\nOffreSpéciale\nCodePromo\nDélaiLivraison\n...",
        height=80,
        help="Ces variables seront ajoutées au template"
    )
    
    custom_variables = {}
    if custom_vars:
        for custom_var in custom_vars.strip().split('\n'):
            var_name = custom_var.strip()
            if var_name:
                custom_variables[var_name] = st.text_input(
                    f"Valeur {var_name}",
                    value=f"Valeur {var_name}",
                    key=f"custom_{var_name}"
                )
    
    # Fusionner les variables
    all_variables = {**variable_values, **custom_variables}
    
    # Appliquer le remplacement
    preview_html = template_html
    for var, value in all_variables.items():
        preview_html = preview_html.replace(f"[{var}]", value)
    
    return preview_html, all_variables

# === DOCUMENTATION POUR OBTENIR LES TOKENS ===
def show_api_key_help(model_choice, model_category):
    """Affiche l'aide pour obtenir les clés API"""
    
    help_info = {
        "Google Gemini": {
            "link": "https://aistudio.google.com/",
            "steps": [
                "🌐 Allez sur Google AI Studio",
                "🔑 Connectez-vous avec votre compte Google",
                "📝 Cliquez sur 'Get API Key'", 
                "🚀 Copiez votre clé et collez-la ci-dessous",
                "🆓 60 requêtes/minute gratuitement"
            ],
            "free": True
        },
        "Groq (Llama 3)": {
            "link": "https://console.groq.com/",
            "steps": [
                "🌐 Allez sur Groq Console",
                "🔑 Créez un compte gratuit",
                "📝 Générez une clé API dans l'onglet API Keys",
                "🚀 Copiez votre clé et collez-la ci-dessous",
                "🆓 Crédits gratuits inclus"
            ],
            "free": True
        },
        "OpenAI GPT-4": {
            "link": "https://platform.openai.com/api-keys",
            "steps": [
                "🌐 Allez sur OpenAI Platform",
                "🔑 Connectez-vous à votre compte",
                "💳 Ajoutez une méthode de paiement",
                "📝 Créez une nouvelle clé API",
                "🚀 Copiez votre clé sécurisée"
            ],
            "free": False
        },
        "Claude (Anthropic)": {
            "link": "https://console.anthropic.com/",
            "steps": [
                "🌐 Allez sur Anthropic Console", 
                "🔑 Créez votre compte",
                "💳 Ajoutez une méthode de paiement",
                "📝 Générez une clé API",
                "🚀 Copiez votre clé sécurisée"
            ],
            "free": False
        }
    }
    
    info = help_info.get(model_choice, {})
    if info:
        with st.expander(f"ℹ️ Comment obtenir ma clé {model_choice} ?", expanded=False):
            st.markdown(f"**Lien :** [{info['link']}]({info['link']})")
            
            st.markdown("**Étapes :**")
            for step in info['steps']:
                st.write(f"• {step}")
            
            if info['free'] and "GRATUITS" in model_category:
                st.success("🆓 **Gratuit** - Pas de carte de crédit requise")
            elif not info['free']:
                st.info("💳 **Payant** - Carte de crédit requise")

# === INTERFACE STREAMLIT PRINCIPALE ===
def ai_template_interface():
    """Interface pour la génération IA de templates - Version BYOK avec variables"""
    
    st.subheader("🤖 Générer un Template avec IA")
    
    # Debug mode
    debug_mode = st.sidebar.checkbox("🐛 Mode Debug", help="Afficher les informations de débogage")
    
    with st.expander("⚙️ Configuration IA", expanded=True):
        # Sélection de la catégorie
        model_category = st.selectbox(
            "Catégorie de modèle",
            ["🆓 GRATUITS (BYOK)", "💰 PREMIUM (BYOK)", "🖥️ LOCAUX", "📝 TEMPLATES"],
            help="BYOK = Bring Your Own Key (vous fournissez la clé API)"
        )
        
        # Modèles selon la catégorie
        ai_generator = AITemplateGenerator()
        available_choices = list(ai_generator.available_models[model_category].keys())
        
        model_choice = st.selectbox(
            "Modèle",
            available_choices,
            help=f"Modèles disponibles dans {model_category}"
        )
        
        style_choice = st.selectbox(
            "Style du template",
            ["professional", "modern", "creative", "minimalist", "warm"]
        )
        
        # Configuration API Key si BYOK
        api_key = None
        if "BYOK" in model_category:
            st.markdown("---")
            st.markdown("### 🔑 Configuration API")
            
            # Afficher l'aide pour obtenir la clé
            show_api_key_help(model_choice, model_category)
            
            help_links = {
                "Google Gemini": "https://aistudio.google.com/",
                "Groq (Llama 3)": "https://console.groq.com/",
                "OpenAI GPT-4": "https://platform.openai.com/api-keys",
                "Claude (Anthropic)": "https://console.anthropic.com/"
            }
            
            help_link = help_links.get(model_choice, "#")
            
            api_key = st.text_input(
                f"Clé API {model_choice}",
                type="password",
                placeholder=f"Collez votre clé {model_choice} ici...",
                help=f"🆓 Obtenez une clé gratuite sur {help_link}" if "GRATUITS" in model_category else f"💳 Clé payante requise - {help_link}"
            )
        
        # Configuration Ollama si local
        ollama_model = "mistral:7b"
        ollama_url = "http://localhost:11434"
        
        if model_category == "🖥️ LOCAUX":
            st.markdown("---")
            st.markdown("### 🔧 Configuration Ollama")
            
            ollama_model = st.selectbox(
                "Modèle Ollama",
                ["mistral:7b", "llama3.2:3b", "llama3.2:1b", "phi", "llama2"],
                help="mistral:7b recommandé pour meilleures performances"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                ollama_url = st.text_input(
                    "URL Ollama",
                    value="http://localhost:11434",
                    help="URL où tourne Ollama"
                )
            with col2:
                if st.button("🔍 Tester Ollama", use_container_width=True):
                    if ai_generator._check_ollama_connection(ollama_url):
                        st.success("✅ Ollama accessible!")
                    else:
                        st.error("❌ Ollama inaccessible")
    
    # Conseils selon la catégorie
    with st.expander("💡 Conseils pour de meilleurs résultats", expanded=True):
        if model_category == "🆓 GRATUITS (BYOK)":
            st.info("""
            **🎯 Modèles Gratuits (BYOK) :**
            - **Google Gemini** : 60 req/min gratuites, excellente qualité
            - **Groq** : Très rapide, modèle Llama 3 gratuit
            - **Clés perso** : Vos clés restent sur votre machine
            - **Sécurisé** : Aucune donnée envoyée à nos serveurs
            """)
        elif model_category == "💰 PREMIUM (BYOK)":
            st.info("""
            **🎯 Modèles Premium (BYOK) :**
            - **Meilleure qualité** : GPT-4 et Claude excellents
            - **Plus rapide** : Réponses en quelques secondes
            - **Coûts** : Vous payez seulement votre usage
            - **Flexible** : Utilisez vos crédits existants
            """)
        elif model_category == "🖥️ LOCAUX":
            st.info("""
            **🎯 Ollama (Local) :**
            - **100% gratuit** : Aucune clé API nécessaire
            - **Vie privée** : Tout reste sur votre machine
            - **Plus lent** : 1-2 minutes de génération
            - **Hors ligne** : Fonctionne sans internet
            """)
        else:
            st.info("""
            **🎯 Templates Prédéfinis :**
            - **Instantané** : Génération immédiate
            - **Fiable** : Qualité constante
            - **Personnalisable** : Variables modifiables
            - **Professionnel** : Designs éprouvés
            """)
    
    # Zone de prompt
    st.markdown("### 📝 Description du Template")
    
    prompt = st.text_area(
        "Décrivez votre template idéal :",
        placeholder="Ex: 'Template newsletter avec header bleu, bouton CTA, section articles'",
        height=80,
        help="💡 Soyez concis pour de meilleures performances"
    )
    
    # Options de génération
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_btn = st.button("🎨 Générer le Template", type="primary", use_container_width=True)
    with col2:
        if model_category == "🖥️ LOCAUX":
            st.info("⏱️ 1-2 min")
        elif model_category == "📝 TEMPLATES":
            st.info("⚡ Instantané")
        else:
            st.info("⏱️ 10-30s")
    
    if generate_btn:
        if not prompt.strip():
            st.warning("Veuillez entrer une description pour votre template")
            return
        
        if "BYOK" in model_category and not api_key:
            st.error(f"🔑 Clé API {model_choice} requise")
            return
        
        # Message d'attente adapté
        if model_category == "🖥️ LOCAUX":
            waiting_msg = f"🔄 Génération avec {ollama_model} (local, peut prendre 1-2 minutes)..."
        elif model_category == "📝 TEMPLATES":
            waiting_msg = "⚡ Génération instantanée..."
        else:
            waiting_msg = f"🔄 Génération avec {model_choice}..."
        
        with st.spinner(waiting_msg):
            if model_choice == "Ollama":
                template_html, debug_info = ai_generator._generate_with_ollama(
                    prompt, style_choice, api_key, ollama_model, ollama_url
                )
            else:
                template_html = ai_generator.generate_template(
                    prompt, model_category, model_choice, style_choice, api_key, ollama_model, ollama_url
                )
                debug_info = [f"Template généré avec {model_choice}"]
            
            if template_html:
                # Extraire les variables
                variables = ai_generator.get_template_variables(template_html)
                
                st.session_state.generated_templates = [{
                    "name": f"Template - {style_choice}",
                    "html": template_html,
                    "text": ai_generator._extract_text_from_html(template_html),
                    "preview": template_html,
                    "model": f"{model_category} - {model_choice}",
                    "variables": variables,
                    "debug_info": debug_info if debug_mode else None
                }]
                
                st.success(f"✅ Template généré avec {model_choice} !")
                if model_category != "📝 TEMPLATES":
                    st.balloons()
                
                if debug_mode and debug_info:
                    with st.expander("📊 Debug Info"):
                        for info in debug_info:
                            st.write(f"• {info}")
            else:
                st.error("❌ Erreur lors de la génération du template")
    
    # Affichage des templates générés AVEC INTERFACE VARIABLES
    if hasattr(st.session_state, 'generated_templates') and st.session_state.generated_templates:
        st.markdown("---")
        st.subheader("📋 Templates Générés")
        
        for i, template in enumerate(st.session_state.generated_templates):
            display_template_with_variables(template, style_choice)

# === POINT D'ENTRÉE PRINCIPAL ===
def main():
    """Fonction principale de l'application"""
    st.set_page_config(
        page_title="Mailing Neurafrik - Générateur de Templates",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Style CSS personnalisé
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # En-tête de l'application
    st.markdown('<h1 class="main-header">📧 Mailing Neurafrik</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Générateur Intelligent de Templates Email</h2>', unsafe_allow_html=True)
    
    # Initialisation de l'état de session
    if 'generated_templates' not in st.session_state:
        st.session_state.generated_templates = []
    if 'selected_ai_template' not in st.session_state:
        st.session_state.selected_ai_template = None
    
    # Interface principale
    ai_template_interface()
    
    # Pied de page
    st.markdown("---")
    st.markdown(
        "**Mailing Neurafrik** • Génération IA de templates email • "
        "BYOK (Bring Your Own Key) • "
        "© 2024 Tous droits réservés"
    )

# Lancement de l'application
if __name__ == "__main__":
    main()