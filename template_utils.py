import streamlit as st
from datetime import datetime
from data_manager import save_email_templates, save_sms_templates

# Import des nouveaux services modulaires
from IA_integrations.template.template_generator import AITemplateGenerator
from IA_integrations.models.ai_config import AIConfigManager
from IA_integrations.utils.helpers import get_smart_default_value, organize_variables_by_category

# NOUVEAU - Import du gestionnaire de templates
from template_manager import TemplateManager

def template_section():
    st.header("📝 Gestion des Templates Multi-Canal")
    
    # Initialisation du gestionnaire (NOUVEAU)
    template_manager = TemplateManager()
    
    # === Nouvel onglet pour l'IA ===
    tab1, tab2, tab3 = st.tabs(["📝 Création Manuelle", "🤖 Génération IA", "🔄 Conversion SMS"])  # NOUVEAU onglet
    
    with tab1:
        manual_template_creation(template_manager)  # MODIFIÉ avec template_manager
    
    with tab2:
        ai_template_section()  # GARDÉ identique
    
    with tab3:  # NOUVEAU onglet
        template_conversion_section(template_manager)
    
    # Afficher les templates existants
    display_existing_templates(template_manager)  # MODIFIÉ avec template_manager

def manual_template_creation(template_manager):
    """Version améliorée avec option SMS intégrée"""
    with st.expander("📧 Créer un nouveau template EMAIL", expanded=True):
        with st.form("email_template_form"):
            template_name = st.text_input("Nom du template*")
            email_subject = st.text_input("Sujet de l'email*")

            # NOUVEAU : Option de création simultanée SMS
            create_sms_version = st.checkbox(
                "📱 Créer aussi une version SMS", 
                help="Génère automatiquement une version SMS optimisée"
            )
            
            if create_sms_version:
                sms_template_name = st.text_input(
                    "Nom du template SMS", 
                    value=f"SMS - {template_name}" if template_name else "",
                    help="Laissez vide pour nom automatique"
                )

            # Choix du type de contenu
            option = st.radio(
                "Type de contenu du mail *",
                ["Texte uniquement", "HTML uniquement", "Texte + HTML"],
                key="create_template_type"
            )

            html_content, text_content = "", ""

            if option in ["HTML uniquement", "Texte + HTML"]:
                html_content = st.text_area("Contenu HTML", height=300, placeholder="<h1>Bonjour [Nom]</h1>")

            if option in ["Texte uniquement", "Texte + HTML"]:
                text_content = st.text_area("Contenu Texte", height=300, placeholder="Bonjour [Nom], ...")

            submitted = st.form_submit_button("Sauvegarder le template")
            if submitted:
                # Validation
                if not template_name.strip() or not email_subject.strip():
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
                elif option == "Texte uniquement" and not text_content.strip():
                    st.error("❌ Le contenu texte est obligatoire pour ce choix")
                elif option == "HTML uniquement" and not html_content.strip():
                    st.error("❌ Le contenu HTML est obligatoire pour ce choix")
                elif option == "Texte + HTML" and (not text_content.strip() or not html_content.strip()):
                    st.error("❌ Les deux contenus doivent être remplis")
                else:
                    # Sauvegarde du template email
                    template_manager.email_templates[template_name] = {
                        "subject": email_subject,
                        "html": html_content if option in ["HTML uniquement", "Texte + HTML"] else None,
                        "text": text_content if option in ["Texte uniquement", "Texte + HTML"] else None,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "manual",
                        "variables": template_manager.extract_variables(html_content + " " + text_content)
                    }
                    save_email_templates(template_manager.email_templates)
                    
                    # NOUVEAU : Création automatique du template SMS si demandé
                    if create_sms_version:
                        success, sms_name = template_manager.convert_email_to_sms(
                            template_name, 
                            sms_template_name if sms_template_name.strip() else None
                        )
                        if success:
                            st.success(f"✅ Template '{template_name}' et '{sms_name}' sauvegardés !")
                        else:
                            st.success(f"✅ Template '{template_name}' sauvegardé !")
                            st.warning("⚠️ Échec de la création du template SMS")
                    else:
                        st.success(f"✅ Template '{template_name}' sauvegardé avec succès !")
                    
                    st.rerun()

# NOUVELLE SECTION : Conversion Email vers SMS
def template_conversion_section(template_manager):
    """Section dédiée à la conversion entre canaux"""
    st.header("🔄 Conversion Email → SMS")
    
    if not template_manager.email_templates:
        st.info("📭 Aucun template email disponible pour conversion")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📧 → 📱 Convertir Email vers SMS")
        
        email_template = st.selectbox(
            "Template email à convertir",
            list(template_manager.email_templates.keys()),
            key="convert_email_select"
        )
        
        sms_template_name = st.text_input(
            "Nom du nouveau template SMS",
            value=f"SMS - {email_template}",
            key="converted_sms_name"
        )
        
        # Aperçu de la conversion
        if email_template:
            email_data = template_manager.email_templates[email_template]
            preview_sms = template_manager._generate_sms_from_email(email_data)
            
            st.text_area(
                "Aperçu du SMS généré",
                preview_sms,
                height=100,
                disabled=True
            )
            st.write(f"📊 {len(preview_sms)}/160 caractères")
            
            if st.button("🔄 Convertir en template SMS", key="convert_to_sms"):
                success, final_sms_name = template_manager.convert_email_to_sms(
                    email_template, 
                    sms_template_name
                )
                if success:
                    st.success(f"✅ Template SMS '{final_sms_name}' créé !")
                    st.balloons()
                else:
                    st.error("❌ Échec de la conversion")
    
    with col2:
        st.subheader("🎯 Templates Liés")
        
        # Afficher les paires email/sms existantes
        linked_templates = []
        for sms_name, sms_data in template_manager.sms_templates.items():
            if 'original_email_template' in sms_data:
                linked_templates.append({
                    'email': sms_data['original_email_template'],
                    'sms': sms_name
                })
        
        if linked_templates:
            st.write("**Paires email/SMS existantes :**")
            for pair in linked_templates:
                with st.expander(f"📧 {pair['email']} → 📱 {pair['sms']}"):
                    shared_vars = template_manager.get_shared_variables(
                        pair['email'], 
                        pair['sms']
                    )
                    if shared_vars:
                        st.write("**Variables communes :**", ", ".join(shared_vars))
                    
                    if st.button(f"🗑️ Supprimer le SMS", key=f"del_sms_{pair['sms']}"):
                        del template_manager.sms_templates[pair['sms']]
                        save_sms_templates(template_manager.sms_templates)
                        st.rerun()
        else:
            st.info("🔗 Aucun template lié pour le moment")

# MODIFICATION : display_existing_templates pour inclure SMS
def display_existing_templates(template_manager):
    """Affiche les templates existants avec onglets séparés"""
    st.subheader("📂 Templates Existants")
    
    if template_manager.email_templates:
        # Créer des onglets pour email et SMS
        tab_email, tab_sms = st.tabs(["📧 Templates Email", "📱 Templates SMS"])
        
        with tab_email:
            display_email_templates(template_manager)
        
        with tab_sms:
            display_sms_templates(template_manager)
    else:
        st.info("Aucun template enregistré.")

# NOUVELLE FONCTION : Affichage templates SMS
def display_sms_templates(template_manager):
    """Affiche les templates SMS"""
    if not template_manager.sms_templates:
        st.info("📭 Aucun template SMS enregistré")
        return
    
    sms_names = list(template_manager.sms_templates.keys())
    selected_sms = st.selectbox(
        "Sélectionner un template SMS à modifier",
        [""] + sms_names,
        key="select_sms_template"
    )
    
    if selected_sms:
        template = template_manager.sms_templates[selected_sms]
        
        # Indicateur de source
        source_info = template.get('source', 'manual')
        if source_info.startswith('converted_from_email:'):
            original_email = source_info.replace('converted_from_email:', '')
            st.info(f"🔄 Converti depuis : **{original_email}**")
        else:
            st.write("**Source :** ✍️ Manuel")
        
        with st.form("edit_sms_template_form"):
            new_name = st.text_input("Nom du template SMS", value=selected_sms, key="edit_sms_name")
            sms_content = st.text_area(
                "Contenu SMS", 
                value=template['content'],
                height=150,
                key="edit_sms_content"
            )
            
            st.write(f"📊 {len(sms_content)}/160 caractères")
            
            if st.form_submit_button("💾 Sauvegarder les modifications"):
                if new_name != selected_sms:
                    del template_manager.sms_templates[selected_sms]
                
                template_manager.sms_templates[new_name] = {
                    "content": sms_content,
                    "char_count": len(sms_content),
                    "created_at": template.get('created_at', datetime.now().isoformat()),
                    "variables": template_manager.extract_variables(sms_content),
                    "source": template.get('source', 'manual'),
                    "original_email_template": template.get('original_email_template')
                }
                
                save_sms_templates(template_manager.sms_templates)
                st.success("✅ Template SMS mis à jour !")
                st.rerun()

# MODIFICATION LÉGÈRE : display_email_templates pour montrer les liens SMS
def display_email_templates(template_manager):
    """Affiche les templates email avec indicateurs SMS"""
    template_names = list(template_manager.email_templates.keys())
    selected_template = st.selectbox(
        "Sélectionner un template email à modifier", 
        [""] + template_names, 
        key="select_email_template"
    )

    if selected_template:
        template = template_manager.email_templates[selected_template]
        
        # Indicateur de source et liaison SMS
        source_badge = "🤖 IA" if template.get("source") == "ia_generated" else "✍️ Manuel"
        
        # Vérifier si un template SMS lié existe
        sms_linked = None
        for sms_name, sms_data in template_manager.sms_templates.items():
            if sms_data.get('original_email_template') == selected_template:
                sms_linked = sms_name
                break
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.write(f"**Source :** {source_badge}")
        with col_info2:
            if sms_linked:
                st.success(f"**📱 Lié à :** {sms_linked}")
            else:
                st.warning("**📱 Aucun SMS lié**")
        
        # Le reste de ta fonction display_existing_templates() original ici...
        # Afficher les variables si disponibles
        if template.get('variables'):
            st.markdown("**Variables de personnalisation :**")
            cols = st.columns(3)
            for idx, var in enumerate(template['variables']):
                cols[idx % 3].code(f"[{var}]")
        
        with st.form("edit_template_form"):
            new_name = st.text_input("Nom du template", value=selected_template, key="edit_template_name")
            new_subject = st.text_input("Sujet", value=template["subject"], key="edit_template_subject")

            # Déduire le type en fonction de ce qui existe
            if template.get("html") and template.get("text"):
                default_type = "Texte + HTML"
            elif template.get("html"):
                default_type = "HTML uniquement"
            else:
                default_type = "Texte uniquement"

            option_edit = st.radio(
                "Type de contenu du mail",
                ["Texte uniquement", "HTML uniquement", "Texte + HTML"],
                index=["Texte uniquement", "HTML uniquement", "Texte + HTML"].index(default_type),
                key="edit_template_type"
            )

            new_html, new_text = None, None
            if option_edit in ["HTML uniquement", "Texte + HTML"]:
                new_html = st.text_area("Contenu HTML", value=template.get("html") or "", height=300, key="edit_html_content")
            if option_edit in ["Texte uniquement", "Texte + HTML"]:
                new_text = st.text_area("Contenu Texte", value=template.get("text") or "", height=300, key="edit_text_content")

            # NOUVEAU : Option pour recréer le SMS lié
            if sms_linked:
                update_sms = st.checkbox("🔄 Mettre à jour le template SMS lié", value=True)

            col1, col2 = st.columns(2)
            save_changes = col1.form_submit_button("Sauvegarder les modifications")
            delete_template = col2.form_submit_button("Supprimer")

            if save_changes:
                if not new_name.strip() or not new_subject.strip():
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
                elif option_edit == "Texte uniquement" and not new_text.strip():
                    st.error("❌ Le contenu texte est obligatoire pour ce choix")
                elif option_edit == "HTML uniquement" and not new_html.strip():
                    st.error("❌ Le contenu HTML est obligatoire pour ce choix")
                elif option_edit == "Texte + HTML" and (not new_text.strip() or not new_html.strip()):
                    st.error("❌ Les deux contenus doivent être remplis")
                else:
                    if new_name != selected_template:
                        del template_manager.email_templates[selected_template]
                    template_manager.email_templates[new_name] = {
                        "subject": new_subject,
                        "html": new_html if option_edit in ["HTML uniquement", "Texte + HTML"] else None,
                        "text": new_text if option_edit in ["Texte uniquement", "Texte + HTML"] else None,
                        "created_at": template.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "source": template.get("source", "manual"),
                        "variables": template.get('variables', [])  # Conserver les variables
                    }
                    save_email_templates(template_manager.email_templates)
                    
                    # NOUVEAU : Mettre à jour le SMS lié si demandé
                    if sms_linked and update_sms:
                        template_manager.convert_email_to_sms(new_name, sms_linked)
                    
                    st.success("✅ Template mis à jour avec succès !")
                    st.rerun()

            if delete_template:
                del template_manager.email_templates[selected_template]
                save_email_templates(template_manager.email_templates)
                st.success("🗑️ Template supprimé !")
                st.rerun()

# ⚠️ TOUTES TES FONCTIONS IA RESTENT IDENTIQUES ⚠️
# Je ne les modifie pas du tout pour préserver ton code

def ai_template_section():
    """Interface pour la génération IA utilisant la nouvelle architecture"""
    # TON CODE EXACT ICI - je ne le modifie pas
    st.subheader("🤖 Générer un Template avec IA")
    
    # Debug mode
    debug_mode = st.sidebar.checkbox("🐛 Mode Debug", help="Afficher les informations de débogage", key="ai_debug")
    
    with st.expander("⚙️ Configuration IA", expanded=True):
        # Initialisation des managers
        config_manager = AIConfigManager()
        ai_generator = AITemplateGenerator()
        
        # Sélection de la catégorie
        model_category = st.selectbox(
            "Catégorie de modèle",
            config_manager.get_categories(),
            help="BYOK = Bring Your Own Key (vous fournissez la clé API)",
            key="ai_model_category"
        )
        
        # Modèles selon la catégorie
        available_choices = config_manager.get_models_in_category(model_category)
        
        model_choice = st.selectbox(
            "Modèle",
            available_choices,
            help=f"Modèles disponibles dans {model_category}",
            key="ai_model_choice"
        )
        
        style_choice = st.selectbox(
            "Style du template",
            ["professional", "modern", "creative", "minimalist", "warm"],
            key="ai_style_choice"
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
                help=f"🆓 Obtenez une clé gratuite sur {help_link}" if "GRATUITS" in model_category else f"💳 Clé payante requise - {help_link}",
                key="ai_api_key"
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
                help="mistral:7b recommandé pour meilleures performances",
                key="ollama_model"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                ollama_url = st.text_input(
                    "URL Ollama",
                    value="http://localhost:11434",
                    help="URL où tourne Ollama",
                    key="ollama_url"
                )
            with col2:
                if st.button("🔍 Tester Ollama", use_container_width=True, key="test_ollama"):
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
        help="💡 Soyez concis pour de meilleures performances",
        key="ai_prompt"
    )
    
    # Options de génération
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_btn = st.button("🎨 Générer le Template", type="primary", use_container_width=True, key="generate_ai_template")
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
            display_ai_template_with_variables(template, style_choice)
    
    # Afficher le formulaire de finalisation si un template est sélectionné
    display_ai_template_finalization()

# Toutes tes autres fonctions IA restent identiques...
def display_ai_template_with_variables(template, style_choice):
    """Affiche un template IA avec interface de gestion des variables"""
    # CORRECTION DU BOUTON ICI
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
        
        # Actions - CORRECTION DES BOUTONS ICI
        st.markdown("### 💾 Sauvegarde du Template")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CORRECTION : "Utiliser ce template" → "Sauvegarder ce template"
            if st.button("💾 Sauvegarder ce template", key=f"save_{id(template)}", use_container_width=True):
                st.session_state.selected_ai_template = template
                st.success("✅ Template sélectionné ! Remplissez le formulaire ci-dessous pour le sauvegarder.")
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
    # TON CODE EXACT ICI
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
        help="Ces variables seront ajoutées au template",
        key="custom_vars"
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

def show_api_key_help(model_choice, model_category):
    """Affiche l'aide pour obtenir les clés API"""
    # TON CODE EXACT ICI
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

def display_ai_template_finalization():
    """Affiche le formulaire de finalisation pour les templates IA"""
    # CORRECTION DU BOUTON ICI
    if hasattr(st.session_state, 'selected_ai_template') and st.session_state.selected_ai_template:
        template = st.session_state.selected_ai_template
        
        st.markdown("---")
        st.subheader("🎯 Finalisation du Template IA")
        
        st.info("""
        **Étapes de finalisation :**
        1. ✅ Donnez un nom à votre template
        2. 📝 Définissez un sujet d'email
        3. 💾 Sauvegardez le template dans votre bibliothèque
        """)
        
        # Afficher les variables détectées
        if template.get('variables'):
            st.markdown("**🔍 Variables de personnalisation incluses :**")
            cols = st.columns(4)
            for idx, var in enumerate(template['variables']):
                cols[idx % 4].code(f"[{var}]")
        
        with st.form("ai_template_finalize"):
            template_name = st.text_input(
                "Nom du template*", 
                value=f"Template IA - {datetime.now().strftime('%H:%M')}",
                key="finalize_template_name"
            )
            email_subject = st.text_input(
                "Sujet de l'email*", 
                value="Message personnalisé pour [Nom]",
                key="finalize_email_subject"
            )
            
            # Aperçu final
            st.markdown("**📋 Aperçu du template généré :**")
            st.components.v1.html(template['html'], height=300, scrolling=True)
            
            # CORRECTION : "Sauvegarder ce template" → "Sauvegarder dans la bibliothèque"
            if st.form_submit_button("💾 Sauvegarder dans la bibliothèque", use_container_width=True):
                if not template_name.strip() or not email_subject.strip():
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
                else:
                    # Utiliser le TemplateManager pour la sauvegarde
                    template_manager = TemplateManager()
                    
                    template_manager.email_templates[template_name] = {
                        "subject": email_subject,
                        "html": template['html'],
                        "text": template.get('text', ''),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "ia_generated",
                        "variables": template.get('variables', [])
                    }
                    
                    save_email_templates(template_manager.email_templates)
                    
                    # Mettre à jour la session state
                    st.session_state.email_templates = template_manager.email_templates
                    
                    del st.session_state.selected_ai_template
                    st.success("✅ Template IA sauvegardé dans votre bibliothèque !")
                    st.rerun()