import streamlit as st
import re
import json
from datetime import datetime

from IA_integrations.template.template_generator import AITemplateGenerator
from IA_integrations.models.ai_config import AIConfigManager
from IA_integrations.utils.helpers import get_smart_default_value, organize_variables_by_category

# === FONCTIONS D'INTERFACE POUR LES VARIABLES ===
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
        # Initialisation des managers
        config_manager = AIConfigManager()
        ai_generator = AITemplateGenerator()
        
        # Sélection de la catégorie
        model_category = st.selectbox(
            "Catégorie de modèle",
            config_manager.get_categories(),
            help="BYOK = Bring Your Own Key (vous fournissez la clé API)"
        )
        
        # Modèles selon la catégorie
        available_choices = config_manager.get_models_in_category(model_category)
        
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
                    from IA_integrations.services.ollama_service import OllamaService
                    ollama_service = OllamaService()
                    if ollama_service._check_ollama_connection(ollama_url):
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
            template_html = ai_generator.generate_template(
                prompt, model_category, model_choice, style_choice, 
                api_key, ollama_model, ollama_url
            )
            
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
                    "debug_info": ["Template généré avec succès"] if debug_mode else None
                }]
                
                st.success(f"✅ Template généré avec {model_choice} !")
                if model_category != "📝 TEMPLATES":
                    st.balloons()
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