import streamlit as st
import re
import requests
import json
from datetime import datetime

class AITemplateGenerator:
    def __init__(self):
        self.available_models = {
            "Ollama (Local)": self._generate_with_ollama,
            "OpenAI GPT-4": self._generate_with_openai,
            "Claude (Anthropic)": self._generate_with_anthropic,
            "Gemini (Google)": self._generate_with_gemini,
        }
    
    def generate_template(self, prompt, model_type, style_preference="professional", api_key=None, ollama_model="llama2"):
        """Génère un template HTML/CSS à partir d'un prompt"""
        if model_type in self.available_models:
            return self.available_models[model_type](prompt, style_preference, api_key, ollama_model)
        else:
            return self._fallback_generation(prompt, style_preference)
    
    def _generate_with_ollama(self, prompt, style_preference, api_key=None, ollama_model="llama2"):
        """Génération avec Ollama (modèles locaux)"""
        try:
            # URL par défaut d'Ollama
            OLLAMA_URL = "http://localhost:11434/api/generate"
            
            # Prompt système pour la génération de templates email
            system_prompt = self._get_system_prompt(style_preference)
            
            full_prompt = f"""
            {system_prompt}
            
            Description du template demandé : {prompt}
            Style : {style_preference}
            
            Génère UNIQUEMENT le code HTML/CSS sans aucun commentaire supplémentaire.
            Le code doit être compatible email (tables, CSS inline, etc.).
            """
            
            payload = {
                "model": ollama_model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                template_html = result["response"].strip()
                
                # Nettoyer la réponse pour ne garder que le HTML
                template_html = self._clean_ollama_response(template_html)
                return template_html
            else:
                st.warning(f"Ollama non disponible (erreur {response.status_code}). Utilisation du mode fallback.")
                return self._fallback_generation(prompt, style_preference)
                
        except requests.exceptions.ConnectionError:
            st.warning("🔌 Ollama n'est pas démarré. Démarrez Ollama avec 'ollama serve' et assurez-vous qu'un modèle est téléchargé.")
            return self._fallback_generation(prompt, style_preference)
        except Exception as e:
            st.error(f"Erreur Ollama: {e}")
            return self._fallback_generation(prompt, style_preference)
    
    def _clean_ollama_response(self, response):
        """Nettoie la réponse d'Ollama pour extraire le HTML pur"""
        # Supprime les marqueurs de code ```html ... ```
        if '```html' in response:
            response = response.split('```html')[1].split('```')[0]
        elif '```' in response:
            response = response.split('```')[1].split('```')[0]
        
        # Supprime les explications textuelles avant/après le HTML
        lines = response.split('\n')
        html_lines = []
        in_html = False
        
        for line in lines:
            if '<!DOCTYPE' in line or '<html' in line or '<table' in line:
                in_html = True
            if in_html:
                html_lines.append(line)
            if '</html>' in line or '</body>' in line:
                break
        
        cleaned_html = '\n'.join(html_lines)
        return cleaned_html if cleaned_html.strip() else response
    
    def _generate_with_openai(self, prompt, style_preference, api_key=None, ollama_model=None):
        """Génération avec OpenAI"""
        try:
            if api_key:
                # Implémentation OpenAI réelle
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": self._get_system_prompt(style_preference)},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                except ImportError:
                    st.warning("Bibliothèque OpenAI non installée. Utilisez 'pip install openai'")
            
            return self._fallback_generation(prompt, style_preference)
        except Exception as e:
            st.error(f"Erreur OpenAI: {e}")
            return self._fallback_generation(prompt, style_preference)
    
    def _generate_with_anthropic(self, prompt, style_preference, api_key=None, ollama_model=None):
        """Génération avec Anthropic Claude"""
        try:
            if api_key:
                # Implémentation Anthropic réelle
                try:
                    import anthropic
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    response = client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=2000,
                        temperature=0.7,
                        system=self._get_system_prompt(style_preference),
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.content[0].text
                except ImportError:
                    st.warning("Bibliothèque Anthropic non installée. Utilisez 'pip install anthropic'")
            
            return self._fallback_generation(prompt, style_preference)
        except Exception as e:
            st.error(f"Erreur Anthropic: {e}")
            return self._fallback_generation(prompt, style_preference)
    
    def _generate_with_gemini(self, prompt, style_preference, api_key=None, ollama_model=None):
        """Génération avec Google Gemini"""
        try:
            if api_key:
                # Implémentation Gemini réelle
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(
                        f"{self._get_system_prompt(style_preference)}\n\n{prompt}"
                    )
                    return response.text
                except ImportError:
                    st.warning("Bibliothèque Google Generative AI non installée. Utilisez 'pip install google-generativeai'")
            
            return self._fallback_generation(prompt, style_preference)
        except Exception as e:
            st.error(f"Erreur Gemini: {e}")
            return self._fallback_generation(prompt, style_preference)
    
    def _get_system_prompt(self, style_preference):
        """Retourne le prompt système détaillé pour la génération"""
        styles = {
            "professional": "style professionnel et corporate, couleurs sobres (bleu, gris, blanc)",
            "modern": "style moderne avec design épuré, gradients subtils, typographie clean",
            "creative": "style créatif et original, couleurs vives, design unique",
            "minimalist": "style minimaliste, maximum d'espace blanc, typographie simple",
            "warm": "style chaleureux, couleurs douces (orange, beige, marron), ambiance accueillante"
        }
        
        style_desc = styles.get(style_preference, styles["professional"])
        
        return f"""
        Tu es un expert en création de templates email HTML/CSS. Crée un template email responsive et compatible avec tous les clients email.

        CONTRAINTES TECHNIQUES IMPORTANTES :
        - Utilise des tables pour la mise en page (compatibilité Outlook)
        - CSS inline uniquement (pas de balise <style>)
        - Largeur maximale : 600px
        - Pas de JavaScript
        - Design responsive (mobile-friendly)
        - Compatible Gmail, Outlook, Apple Mail, Yahoo Mail

        STYLE : {style_desc}
        COMPATIBILITÉ : Doit fonctionner sur tous les clients email

        STRUCTURE REQUISE :
        - Entête avec titre principal
        - Section contenu principale
        - Pied de page avec informations légales

        Retourne UNIQUEMENT le code HTML complet sans commentaires, sans explications, sans texte autour.
        Le code doit être prêt à être utilisé immédiatement.
        """
    
    def _fallback_generation(self, prompt, style_preference):
        """Génération de fallback sans API"""
        return self._create_advanced_template(prompt, style_preference)
    
    def _create_advanced_template(self, prompt, style_preference):
        """Crée un template avancé avec variations selon le style"""
        styles_config = {
            "professional": {
                "primary": "#2563eb",
                "secondary": "#64748b", 
                "bg_color": "#f8fafc",
                "text_color": "#334155"
            },
            "modern": {
                "primary": "#7c3aed",
                "secondary": "#475569",
                "bg_color": "#ffffff",
                "text_color": "#1e293b"
            },
            "creative": {
                "primary": "#dc2626",
                "secondary": "#ea580c",
                "bg_color": "#fef7ed",
                "text_color": "#7c2d12"
            },
            "minimalist": {
                "primary": "#000000",
                "secondary": "#666666",
                "bg_color": "#ffffff",
                "text_color": "#333333"
            },
            "warm": {
                "primary": "#ea580c",
                "secondary": "#d97706",
                "bg_color": "#fef7ed",
                "text_color": "#7c2d12"
            }
        }
        
        style = styles_config.get(style_preference, styles_config["professional"])
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Arial', sans-serif; background-color: {style['bg_color']};">
            <!-- Container principal -->
            <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <!-- En-tête -->
                <tr>
                    <td style="padding: 30px 20px; background: linear-gradient(135deg, {style['primary']}, {style['secondary']}); text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">Votre Titre Principal</h1>
                        <p style="color: rgba(255, 255, 255, 0.9); margin: 10px 0 0 0; font-size: 16px;">Description ou sous-titre</p>
                    </td>
                </tr>
                
                <!-- Contenu principal -->
                <tr>
                    <td style="padding: 40px 30px;">
                        <h2 style="color: {style['text_color']}; margin-top: 0;">Section Principale</h2>
                        <p style="color: {style['text_color']}; line-height: 1.6; font-size: 16px;">
                            Ceci est un template email généré automatiquement basé sur votre description : "{prompt}".
                        </p>
                        
                        <!-- Bouton d'action -->
                        <table border="0" cellpadding="0" cellspacing="0" style="margin: 30px 0; text-align: center;">
                            <tr>
                                <td>
                                    <a href="#" style="background-color: {style['primary']}; color: #ffffff; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Action Principale</a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                
                <!-- Pied de page -->
                <tr>
                    <td style="padding: 20px; background-color: #f8f9fa; text-align: center;">
                        <p style="color: #666666; font-size: 14px; margin: 0;">
                            &copy; 2024 Votre Entreprise. Tous droits réservés.<br>
                            <a href="#" style="color: {style['primary']}; text-decoration: none;">Se désabonner</a>
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return template
    
    def _extract_text_from_html(self, html_content):
        """Extrait le texte brut du HTML pour la version texte"""
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

def ai_template_interface():
    """Interface pour la génération IA de templates"""
    
    st.subheader("🤖 Générer un Template avec IA")
    
    with st.expander("Configuration IA", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            model_choice = st.selectbox(
                "Modèle IA",
                list(AITemplateGenerator().available_models.keys())
            )
            
            style_choice = st.selectbox(
                "Style du template",
                ["professional", "modern", "creative", "minimalist", "warm"]
            )
        
        with col2:
            if model_choice == "Ollama (Local)":
                ollama_model = st.selectbox(
                    "Modèle Ollama",
                    ["llama2", "mistral", "codellama", "phi", "custom"],
                    help="Assurez-vous que le modèle est téléchargé via 'ollama pull <model>'"
                )
                api_key = None
            else:
                ollama_model = None
                api_key = st.text_input(
                    "Clé API (optionnel)",
                    type="password",
                    help=f"Clé API pour {model_choice}"
                )
    
    # Configuration avancée Ollama
    if model_choice == "Ollama (Local)":
        with st.expander("⚙️ Configuration Ollama avancée"):
            col1, col2 = st.columns(2)
            with col1:
                ollama_url = st.text_input(
                    "URL Ollama",
                    value="http://localhost:11434",
                    help="URL où tourne Ollama"
                )
            with col2:
                st.info("💡 Assurez-vous qu'Ollama est démarré avec 'ollama serve'")
    
    # Zone de prompt
    prompt = st.text_area(
        "Décrivez votre template idéal :",
        placeholder="Ex: 'Un template newsletter moderne avec une header bleue, des sections bien espacées, bouton d'action, adapté mobile...'",
        height=100
    )
    
    if st.button("🎨 Générer des Templates", type="primary"):
        if not prompt.strip():
            st.warning("Veuillez entrer une description pour votre template")
            return
        
        with st.spinner("Génération des templates en cours..."):
            ai_generator = AITemplateGenerator()
            generated_templates = []
            
            # Générer 3 variantes
            for i in range(3):
                template_html = ai_generator.generate_template(
                    prompt, 
                    model_choice, 
                    style_choice, 
                    api_key,
                    ollama_model
                )
                
                if template_html:
                    generated_templates.append({
                        "name": f"Template {i+1} - {style_choice}",
                        "html": template_html,
                        "text": ai_generator._extract_text_from_html(template_html),
                        "preview": template_html,
                        "model": model_choice
                    })
            
            if generated_templates:
                st.session_state.generated_templates = generated_templates
                st.success(f"✅ {len(generated_templates)} templates générés avec succès !")
                
                # Afficher des informations de débogage pour Ollama
                if model_choice == "Ollama (Local)":
                    st.info("🔍 Conseil : Si les templates ne sont pas optimaux, essayez un modèle plus récent comme 'llama2:13b'")
            else:
                st.error("❌ Erreur lors de la génération des templates")
    
    # Affichage des templates générés
    if hasattr(st.session_state, 'generated_templates') and st.session_state.generated_templates:
        st.subheader("📋 Templates Générés")
        
        for i, template in enumerate(st.session_state.generated_templates):
            with st.expander(f"Template {i+1}: {template['name']} ({template['model']})", expanded=i==0):
                
                # Aperçu
                st.markdown("**Aperçu :**")
                st.components.v1.html(template['preview'], height=400, scrolling=True)
                
                # Code source
                with st.expander("📄 Voir le code source"):
                    st.code(template['html'], language='html')
                
                # Actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📝 Utiliser ce template", key=f"use_{i}"):
                        st.session_state.selected_ai_template = template
                        st.rerun()
                
                with col2:
                    st.download_button(
                        "💾 Télécharger HTML",
                        template['html'],
                        file_name=f"template_ia_{i+1}.html",
                        key=f"download_{i}"
                    )
                
                with col3:
                    if st.button("🔄 Régénérer", key=f"regenerate_{i}"):
                        # Logique de régénération
                        pass