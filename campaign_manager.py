import streamlit as st
import pandas as pd
import re
from datetime import datetime
from email_sender import send_email_campaign
from sms_sender import send_sms_campaign
from data_manager import load_data
from sms_manager import load_sms_configs, load_sms_templates

def detect_contact_channels(df):
    """Détecte automatiquement les canaux disponibles dans le CSV"""
    channels = {"email": False, "sms": False}
    
    if "email" in df.columns and not df["email"].isna().all():
        channels["email"] = True
    
    if "telephone" in df.columns and not df["telephone"].isna().all():
        # Vérifier qu'il y a des numéros valides
        from sms_utils import validate_cameroon_phone
        valid_phones = df["telephone"].dropna().apply(lambda x: validate_cameroon_phone(str(x)))
        if valid_phones.any():
            channels["sms"] = True
    
    return channels

def check_spam_risks(email_content, sms_content):
    """Vérifie les risques de spam dans le contenu"""
    spam_indicators = {
        "email": {
            "🚨 Mots-clés spam": [
                "gratuit", "gratuite", "free", "prix incroyable", "offre limitée",
                "urgence", "action immédiate", "gagnez", "million", "cash",
                "credit", "prêt", "argent facile", "richesse", "profit"
            ],
            "⚠️ Caractéristiques suspectes": [
                "TROP DE MAJUSCULES", "!!! multiples", "💰 emojis financiers"
            ]
        },
        "sms": {
            "🚨 Mots-clés spam": [
                "STOP", "ARRET", "UNSUBSCRIBE", "gratuit", "gagnez", "cash",
                "credit", "prêt", "urgent", "immédiat"
            ],
            "⚠️ Risques": [
                "Pas de nom d'entreprise", "Lien court suspect", "Numéro masqué"
            ]
        }
    }
    
    warnings = {"email": [], "sms": []}
    
    # Vérification Email
    if email_content:
        content_lower = email_content.lower()
        for keyword in spam_indicators["email"]["🚨 Mots-clés spam"]:
            if keyword.lower() in content_lower:
                warnings["email"].append(f"Mot-clé spam détecté: '{keyword}'")
        
        # Vérifier les majuscules excessives
        if len(re.findall(r'[A-Z]{5,}', email_content)) > 3:
            warnings["email"].append("Trop de majuscules (risque de spam)")
        
        # Vérifier les points d'exclamation multiples
        if email_content.count('!!!') > 0 or email_content.count('!!') > 2:
            warnings["email"].append("Trop de points d'exclamation")
    
    # Vérification SMS
    if sms_content:
        content_lower = sms_content.lower()
        for keyword in spam_indicators["sms"]["🚨 Mots-clés spam"]:
            if keyword.lower() in content_lower:
                warnings["sms"].append(f"Mot-clé spam détecté: '{keyword}'")
        
        # Vérifier les liens courts suspects
        if re.search(r'(bit\.ly|tinyurl|goo\.gl|t\.co)', sms_content):
            warnings["sms"].append("Lien court détecté (peut être suspect)")
        
        # Vérifier la présence d'identifiant d'entreprise
        if not re.search(r'\[Entreprise\]|\{Entreprise\}|Neurafrik|votre entreprise', sms_content, re.IGNORECASE):
            warnings["sms"].append("Nom d'entreprise manquant")
    
    return warnings

def get_variable_value(var, row, var_mapping, default_values):
    """Récupère la valeur d'une variable pour une ligne donnée - VERSION CORRIGÉE"""
    try:
        if var in var_mapping and var_mapping[var] in row:
            value = row[var_mapping[var]]
            # Gérer les valeurs NaN, None ou vides
            if pd.isna(value) or value is None or str(value).strip() == "":
                return default_values.get(var, "") or ""  # S'assurer de ne pas retourner None
            return str(value).strip()
        else:
            return default_values.get(var, "") or ""  # S'assurer de ne pas retourner None
    except Exception as e:
        # En cas d'erreur, retourner une chaîne vide
        return default_values.get(var, "") or ""

def campaign_section():
    st.header("🎯 Campagne Marketing Multi-Canal")
    
    # Section d'information anti-spam
    with st.expander("📋 Bonnes pratiques anti-spam", expanded=False):
        st.info("""
        **📧 Pour les Emails :**
        • ✅ Utilisez un objet clair et honnête
        • ✅ Incluez votre nom d'entreprise
        • ✅ Ajoutez un lien de désabonnement
        • ✅ Évitez les majuscules excessives
        • ✅ Limitez les mots comme 'gratuit', 'urgent', 'gain'
        
        **📱 Pour les SMS :**
        • ✅ Identifiez votre entreprise
        • ✅ Utilisez STOP pour désabonnement
        • ✅ Évitez les liens courts suspects
        • ✅ Pas de sollicitation financière
        • ✅ Respectez les horaires (9h-20h)
        """)
    
    # Charger toutes les configurations
    smtp_configs = st.session_state.smtp_configs
    email_templates = st.session_state.email_templates
    sms_configs = load_sms_configs()
    sms_templates = load_sms_templates()
    
    # Vérifier les prérequis
    email_ready = bool(smtp_configs and email_templates)
    sms_ready = bool(sms_configs and sms_templates)
    
    if not email_ready and not sms_ready:
        st.error("❌ Configurez d'abord au moins un canal (Email ou SMS)")
        st.info("💡 Allez dans 'Configuration SMTP' ou 'Configuration SMS'")
        return
    
    # Upload du fichier contacts
    st.subheader("📁 Fichier de contacts")
    uploaded_file = st.file_uploader(
        "Importer votre fichier CSV de contacts", 
        type="csv",
        help="Doit contenir au moins une colonne 'email' ou 'telephone'"
    )
    
    if not uploaded_file:
        st.info("📤 Veuillez importer un fichier CSV pour continuer")
        return
        
    df = pd.read_csv(uploaded_file)
    
    # Détection automatique des canaux
    available_channels = detect_contact_channels(df)
    
    if not any(available_channels.values()):
        st.error("❌ Aucun canal détecté. Le CSV doit contenir 'email' ou 'telephone'")
        return
    
    # Affichage des statistiques
    st.success("📊 **Contacts détectés:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_contacts = len(df)
        st.metric("Total contacts", total_contacts)
    
    with col2:
        if available_channels["email"]:
            email_count = df["email"].dropna().count()
            st.metric("📧 Emails", email_count)
        else:
            st.metric("📧 Emails", 0)
    
    with col3:
        if available_channels["sms"]:
            from sms_utils import validate_cameroon_phone
            phone_count = df["telephone"].dropna().apply(lambda x: validate_cameroon_phone(str(x))).sum()
            st.metric("📱 SMS", phone_count)
        else:
            st.metric("📱 SMS", 0)
    
    # Sélection des canaux
    st.subheader("🎯 Canaux à utiliser")
    
    selected_channels = {}
    
    if available_channels["email"] and email_ready:
        selected_channels["email"] = st.checkbox(
            "📧 Envoyer par Email", 
            value=True,
            help="Envoyer un email aux contacts avec adresse email"
        )
    
    if available_channels["sms"] and sms_ready:
        selected_channels["sms"] = st.checkbox(
            "📱 Envoyer par SMS",
            value=True, 
            help="Envoyer un SMS aux contacts avec numéro valide"
        )
    
    if not any(selected_channels.values()):
        st.warning("⚠️ Sélectionnez au moins un canal")
        return
    
    # Configuration Email (si sélectionné)
    email_config = None
    email_content_for_spam_check = ""
    if selected_channels.get("email"):
        st.markdown("---")
        st.subheader("📧 Configuration Email")
        
        col1, col2 = st.columns(2)
        with col1:
            selected_smtp = st.selectbox(
                "Serveur SMTP",
                list(smtp_configs.keys()),
                key="campaign_smtp"
            )
        with col2:
            selected_email_template = st.selectbox(
                "Template Email", 
                list(email_templates.keys()),
                key="campaign_email_template"
            )
        
        email_config = {
            "smtp": selected_smtp,
            "template": selected_email_template,
            "config_data": smtp_configs[selected_smtp],
            "template_data": email_templates[selected_email_template]
        }
        
        # Préparer le contenu pour vérification spam
        html_content = email_config["template_data"].get("html") or ""
        text_content = email_config["template_data"].get("text") or ""
        email_content_for_spam_check = html_content + " " + text_content
    
    # Configuration SMS (si sélectionné)
    sms_config = None
    sms_content_for_spam_check = ""
    if selected_channels.get("sms"):
        st.markdown("---")
        st.subheader("📱 Configuration SMS")
        
        col1, col2 = st.columns(2)
        with col1:
            selected_sms_config = st.selectbox(
                "Opérateur SMS",
                list(sms_configs.keys()),
                key="campaign_sms_config"
            )
        with col2:
            selected_sms_template = st.selectbox(
                "Template SMS",
                list(sms_templates.keys()),
                key="campaign_sms_template"
            )
        
        sms_config = {
            "config": selected_sms_config,
            "template": selected_sms_template,
            "config_data": sms_configs[selected_sms_config],
            "template_data": sms_templates[selected_sms_template]
        }
        
        # Préparer le contenu pour vérification spam
        sms_content_for_spam_check = sms_config["template_data"].get("content") or ""
    
    # VÉRIFICATION ANTI-SPAM
    spam_warnings = check_spam_risks(email_content_for_spam_check, sms_content_for_spam_check)
    
    # Afficher les avertissements spam
    has_spam_warnings = any(warnings for warnings in spam_warnings.values())
    if has_spam_warnings:
        st.markdown("---")
        st.subheader("🚨 Vérification Anti-Spam")
        
        if spam_warnings["email"]:
            with st.expander("📧 Alertes Email", expanded=True):
                for warning in spam_warnings["email"]:
                    if "🚨" in warning:
                        st.error(warning)
                    else:
                        st.warning(warning)
        
        if spam_warnings["sms"]:
            with st.expander("📱 Alertes SMS", expanded=True):
                for warning in spam_warnings["sms"]:
                    if "🚨" in warning:
                        st.error(warning)
                    else:
                        st.warning(warning)
        
        # Option pour continuer malgré les warnings
        if any("🚨" in warning for warnings in spam_warnings.values() for warning in warnings):
            st.error("**Risques élevés de spam détectés !**")
            continue_despite_spam = st.checkbox("⛔️ Je comprends les risques et souhaite continuer malgré tout")
            if not continue_despite_spam:
                st.stop()
        else:
            st.warning("**Risques modérés détectés** - Vérifiez votre contenu")
    
    # Gestion des variables communes
    st.markdown("---")
    st.subheader("🔧 Personnalisation des messages")
    
    # Détection des variables communes
    all_variables = set()
    
    if email_config:
        html_content = email_config["template_data"].get("html") or ""
        text_content = email_config["template_data"].get("text") or ""
        email_content = html_content + " " + text_content
        email_vars = set(re.findall(r'\[(.*?)\]', email_content))
        all_variables.update(email_vars)
    
    if sms_config:
        sms_content = sms_config["template_data"].get("content") or ""
        sms_vars = set(re.findall(r'\{(.*?)\}', sms_content))
        all_variables.update(sms_vars)
    
    # Mapping des variables
    var_mapping, default_values = {}, {}
    
    if all_variables:
        st.info("💡 Configurez le mapping des variables avec les colonnes de votre CSV")
        
        for var in all_variables:
            col1, col2 = st.columns([3, 1])
            with col1:
                if var in df.columns:
                    var_mapping[var] = var
                    st.write(f"✔️ `{var}` détecté dans CSV")
                else:
                    options = [col for col in df.columns if col not in ['email', 'telephone']]
                    selected_col = st.selectbox(
                        f"Colonne pour '{var}'", 
                        ["(Ignorer)"] + options, 
                        key=f"campaign_var_{var}"
                    )
                    if selected_col != "(Ignorer)":
                        var_mapping[var] = selected_col
            
            with col2:
                # S'assurer que la valeur par défaut n'est jamais None
                default_val = st.text_input(
                    f"Valeur par défaut", 
                    value=var,
                    key=f"campaign_default_{var}",
                    help=f"Si non trouvé dans CSV"
                )
                default_values[var] = default_val or ""  # S'assurer que ce n'est pas None
    
    # Aperçu multi-canal
    st.markdown("---")
    st.subheader("👀 Aperçu des messages")
    
    if not df.empty:
        preview_row = df.iloc[0]
        
        # Aperçu Email
        if selected_channels.get("email") and email_config:
            with st.expander("📧 Aperçu Email", expanded=True):
                preview_html = email_config["template_data"].get("html") or ""
                preview_text = email_config["template_data"].get("text") or ""
                
                for var in all_variables:
                    value = get_variable_value(var, preview_row, var_mapping, default_values)
                    # S'assurer que la valeur n'est pas None avant de remplacer
                    safe_value = str(value) if value is not None else ""
                    preview_html = preview_html.replace(f"[{var}]", safe_value)
                    preview_text = preview_text.replace(f"[{var}]", safe_value)
                
                if preview_html.strip():
                    st.components.v1.html(preview_html, height=300, scrolling=True)
                else:
                    st.text_area("Aperçu texte", preview_text, height=150)
        
        # Aperçu SMS
        if selected_channels.get("sms") and sms_config:
            with st.expander("📱 Aperçu SMS", expanded=True):
                preview_sms = sms_config["template_data"].get("content") or ""
                
                for var in all_variables:
                    value = get_variable_value(var, preview_row, var_mapping, default_values)
                    # S'assurer que la valeur n'est pas None avant de remplacer
                    safe_value = str(value) if value is not None else ""
                    preview_sms = preview_sms.replace(f"{{{var}}}", safe_value)
                
                st.text_area("Message SMS", preview_sms, height=100)
                char_count = len(preview_sms)
                st.write(f"📊 {char_count}/160 caractères")
                if char_count > 160:
                    st.error("❌ Message SMS trop long!")
    
    # LANCEMENT DE LA CAMPAGNE
    st.markdown("---")
    st.subheader("🚀 Lancement de la campagne")
    
    # Résumé de la campagne
    st.info("🎯 **Résumé de la campagne:**")
    summary_cols = st.columns(3)
    
    with summary_cols[0]:
        st.write("**Canaux:**")
        if selected_channels.get("email"):
            st.write("✅ Email")
        if selected_channels.get("sms"):
            st.write("✅ SMS")
    
    with summary_cols[1]:
        st.write("**Portée:**")
        if selected_channels.get("email"):
            email_count = df["email"].dropna().count()
            st.write(f"📧 {email_count} emails")
        if selected_channels.get("sms"):
            from sms_utils import validate_cameroon_phone
            sms_count = df["telephone"].dropna().apply(lambda x: validate_cameroon_phone(str(x))).sum()
            st.write(f"📱 {sms_count} SMS")
    
    with summary_cols[2]:
        st.write("**Configuration:**")
        if selected_channels.get("email"):
            st.write(f"📧 {email_config['smtp']}")
        if selected_channels.get("sms"):
            st.write(f"📱 {sms_config['config']}")
    
    # Avertissement final avant envoi
    if has_spam_warnings:
        st.warning("""
        **⚠️ Attention :** Votre campagne contient des indicateurs de spam.
        Assurez-vous d'avoir le consentement des destinataires et respectez les lois anti-spam.
        """)
    
    # Bouton de lancement
    if st.button("🎯 Démarrer la campagne multi-canal", type="primary", use_container_width=True):
        # Vérification de sécurité finale
        if has_spam_warnings and not any("🚨" in warning for warnings in spam_warnings.values() for warning in warnings):
            st.warning("⏳ Lancement de la campagne avec risques modérés...")
        elif has_spam_warnings:
            st.error("🚨 Lancement MALGRÉ les risques élevés de spam!")
        else:
            st.success("✅ Campagne prête à être envoyée!")
        
        campaign_results = {}
        
        # Filtrer les données pour chaque canal
        email_df = df[df["email"].notna()] if selected_channels.get("email") else pd.DataFrame()
        sms_df = df[df["telephone"].notna()] if selected_channels.get("sms") else pd.DataFrame()
        
        # Nettoyer les données SMS
        if selected_channels.get("sms"):
            from sms_utils import validate_cameroon_phone, format_cameroon_phone
            sms_df = sms_df[sms_df["telephone"].apply(lambda x: validate_cameroon_phone(str(x)))]
            sms_df["telephone"] = sms_df["telephone"].apply(lambda x: format_cameroon_phone(str(x)))
        
        # Lancement parallèle des campagnes
        progress_placeholder = st.empty()
        results_placeholder = st.empty()
        
        # Email Campaign
        if selected_channels.get("email") and not email_df.empty:
            with st.spinner("📧 Envoi des emails en cours..."):
                try:
                    email_results = send_email_campaign(
                        email_df, email_config, var_mapping, default_values
                    )
                    campaign_results["email"] = email_results
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'envoi des emails: {str(e)}")
                    campaign_results["email"] = {
                        "success_count": 0,
                        "error_count": len(email_df),
                        "logs": [f"Erreur globale: {str(e)}"]
                    }
        
        # SMS Campaign  
        if selected_channels.get("sms") and not sms_df.empty:
            with st.spinner("📱 Envoi des SMS en cours..."):
                try:
                    sms_results = send_sms_campaign(
                        sms_df, sms_config, var_mapping, default_values
                    )
                    campaign_results["sms"] = sms_results
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'envoi des SMS: {str(e)}")
                    campaign_results["sms"] = {
                        "success_count": 0,
                        "error_count": len(sms_df),
                        "logs": [f"Erreur globale: {str(e)}"]
                    }
        
        # Affichage des résultats finaux
        display_campaign_results(campaign_results)

def display_campaign_results(campaign_results):
    """Affiche les résultats de la campagne multi-canal"""
    st.markdown("---")
    st.header("📊 Résultats de la campagne")
    
    # Métriques globales
    total_sent = 0
    total_errors = 0
    
    for channel, results in campaign_results.items():
        total_sent += results.get('success_count', 0)
        total_errors += results.get('error_count', 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Total envoyés", total_sent)
    with col2:
        st.metric("❌ Total erreurs", total_errors)
    with col3:
        success_rate = (total_sent/(total_sent + total_errors))*100 if (total_sent + total_errors) > 0 else 0
        st.metric("📊 Taux de succès", f"{success_rate:.1f}%")
    
    # Détail par canal
    for channel, results in campaign_results.items():
        with st.expander(f"{'📧' if channel == 'email' else '📱'} Résultats {channel.upper()}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Envoyés", results.get('success_count', 0))
            with col2:
                st.metric("Erreurs", results.get('error_count', 0))
            
            if results.get('logs'):
                # Afficher les premiers logs
                st.text_area(
                    f"Derniers logs {channel}",
                    "\n".join(results['logs'][-10:]),  # Derniers 10 logs
                    height=150
                )
                
                st.download_button(
                    f"📥 Télécharger tous les logs {channel}",
                    "\n".join(results['logs']),
                    file_name=f"logs_{channel}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                )
    
    # Recommandations post-campagne
    st.markdown("---")
    st.subheader("💡 Recommandations")
    
    if total_errors > total_sent * 0.1:  # Plus de 10% d'erreurs
        st.warning("""
        **Taux d'erreur élevé détecté :**
        • Vérifiez la qualité de votre liste de contacts
        • Assurez-vous que les serveurs SMTP/SMS sont configurés correctement
        • Testez avec un petit groupe avant les prochaines campagnes
        """)
    elif total_sent > 0:
        st.success("""
        **Campagne réussie !**
        • Pensez à segmenter votre audience pour de meilleurs résultats
        • Analysez les taux d'ouverture et de conversion
        • Planifiez votre prochaine communication
        """)