import streamlit as st
import requests
import json
import re
from datetime import datetime
from sms_manager import load_sms_configs, save_sms_configs, load_sms_templates, save_sms_templates

def sms_config_section():
    st.header("📱 Configuration SMS - Cameroun")
    
    # Opérateurs Cameroun disponibles
    operators = {
        "orange_cm": {
            "name": "Orange Cameroun", 
            "color": "#FF6600",
            "docs": "https://developer.orange.com/apis/sms-cm",
            "format": "6XXXXXXXX ou 2376XXXXXXXX"
        },
        "mtn_cm": {
            "name": "MTN Cameroun", 
            "color": "#FFCC00",
            "docs": "https://www.mtn.cm/business/apis",
            "format": "6XXXXXXXX ou 2376XXXXXXXX"
        }
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Nouvelle Configuration")
        
        config_name = st.text_input("Nom de la configuration", placeholder="Orange Pro, MTN Business...")
        operator = st.selectbox(
            "Opérateur", 
            list(operators.keys()), 
            format_func=lambda x: operators[x]["name"]
        )
        
        # Configuration spécifique selon l'opérateur
        if operator == "orange_cm":
            st.info("🟠 **Orange Cameroun** - API SMS Professionnel")
            client_id = st.text_input("Client ID Orange", help="Trouvé dans Orange Developer Portal")
            client_secret = st.text_input("Client Secret", type="password")
            sender_name = st.text_input("Nom expéditeur (11 caractères)", max_chars=11, value="NEURAFRIK")
            api_key = f"{client_id}:{client_secret}"
            
        elif operator == "mtn_cm":
            st.info("🟡 **MTN Cameroun** - Business SMS API")
            api_key = st.text_input("Clé API MTN", type="password", help="Clé API fournie par MTN Business")
            sender_name = st.text_input("Numéro expéditeur MTN", placeholder="6XXXXXXXX")
            subscription_id = st.text_input("ID Abonnement MTN", help="ID de votre abonnement SMS")
        
        if st.button("💾 Sauvegarder la configuration", type="primary"):
            if config_name and api_key:
                sms_configs = load_sms_configs()
                sms_configs[config_name] = {
                    "operator": operator,
                    "api_key": api_key,
                    "sender_name": sender_name,
                    "operator_info": operators[operator],
                    "created_at": datetime.now().isoformat()
                }
                
                # Stockage spécifique selon l'opérateur
                if operator == "orange_cm":
                    sms_configs[config_name]["client_id"] = client_id
                    sms_configs[config_name]["client_secret"] = client_secret
                elif operator == "mtn_cm":
                    sms_configs[config_name]["subscription_id"] = subscription_id
                
                save_sms_configs(sms_configs)
                st.success(f"✅ Configuration '{config_name}' sauvegardée!")
                
                # Test de connexion
                if test_sms_configuration(sms_configs[config_name]):
                    st.balloons()
            else:
                st.error("Veuillez remplir tous les champs obligatoires")
    
    with col2:
        st.subheader("⚙️ Configurations existantes")
        sms_configs = load_sms_configs()
        
        if not sms_configs:
            st.info("Aucune configuration SMS sauvegardée")
        else:
            for name, config in sms_configs.items():
                operator_color = operators[config["operator"]]["color"]
                with st.expander(f"📱 {name} - {config['operator_info']['name']}", expanded=True):
                    st.markdown(f"**Expéditeur:** `{config.get('sender_name', 'Non défini')}`")
                    st.markdown(f"**Format numéros:** {config['operator_info']['format']}")
                    
                    # Test de la configuration
                    if st.button(f"🧪 Tester la connexion", key=f"test_{name}"):
                        if test_sms_configuration(config):
                            st.success("✅ Connexion réussie!")
                        else:
                            st.error("❌ Échec de connexion")
                    
                    if st.button(f"🗑️ Supprimer", key=f"del_{name}"):
                        sms_configs.pop(name)
                        save_sms_configs(sms_configs)
                        st.rerun()

def test_sms_configuration(config):
    """Teste la configuration SMS"""
    try:
        if config["operator"] == "orange_cm":
            return test_orange_cm_connection(config)
        elif config["operator"] == "mtn_cm":
            return test_mtn_cm_connection(config)
        return False
    except Exception as e:
        st.error(f"Erreur de test: {str(e)}")
        return False

def test_orange_cm_connection(config):
    """Teste la connexion à l'API Orange Cameroun"""
    try:
        # Orange Cameroon utilise OAuth2
        client_id, client_secret = config["api_key"].split(":")
        
        # Simulation - En production, tu ferais un vrai appel OAuth
        st.info("🟠 Test Orange Cameroon: Vérification des identifiants...")
        
        # Pour le moment, on simule un test réussi si les champs sont remplis
        if client_id and client_secret:
            return True
        return False
        
    except Exception as e:
        st.error(f"Erreur Orange Cameroon: {str(e)}")
        return False

def test_mtn_cm_connection(config):
    """Teste la connexion à l'API MTN Cameroun"""
    try:
        # MTN Cameroon API
        api_key = config["api_key"]
        subscription_id = config.get("subscription_id", "")
        
        st.info("🟡 Test MTN Cameroon: Vérification de la clé API...")
        
        # Simulation - En production, vrai appel API
        if api_key and subscription_id:
            return True
        return False
        
    except Exception as e:
        st.error(f"Erreur MTN Cameroon: {str(e)}")
        return False

def validate_cameroon_phone(phone):
    """Valide un numéro de téléphone camerounais"""
    # Formats acceptés: 6XXXXXXXX, 2376XXXXXXXX, +2376XXXXXXXX
    pattern = r'^(\+237|237)?[6-7][0-9]{8}$'
    return re.match(pattern, phone.replace(' ', '')) is not None

def format_cameroon_phone(phone):
    """Formate un numéro camerounais au format international"""
    cleaned = phone.replace(' ', '').replace('+', '')
    if cleaned.startswith('237'):
        return '+' + cleaned
    elif len(cleaned) == 9 and cleaned.startswith(('6', '7')):
        return '+237' + cleaned
    else:
        return phone

def sms_template_section():
    st.header("📝 Gestion des Templates SMS - Cameroun")
    
    st.info("💡 **Conseil:** Les SMS au Cameroun ont une limite de 160 caractères. Utilisez des messages concis!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Créer un template")
        template_name = st.text_input("Nom du template", placeholder="Promo Noël, Rappel Paiement...")
        
        # Variables communes pour le Cameroun
        st.caption("**Variables disponibles:** {prenom}, {nom}, {ville}, {quartier}, {produit}, {prix}, {date}")
        
        sms_content = st.text_area(
            "Contenu du SMS", 
            height=120,
            placeholder="Bonjour {prenom}! Votre commande {produit} est prête. Prix: {prix} FCFA. Merci!",
            help="Utilisez les variables entre {} pour personnaliser"
        )
        
        # Compteur de caractères avec alertes
        if sms_content:
            char_count = len(sms_content)
            st.write(f"📊 **{char_count}/160** caractères")
            
            if char_count > 160:
                st.error("❌ Trop long! Les SMS sont facturés en multiples de 160 caractères.")
            elif char_count > 140:
                st.warning("⚠️ Approche de la limite. Essayez de raccourcir.")
            else:
                st.success("✅ Longueur optimale!")
        
        if st.button("💾 Sauvegarder le template", type="primary"):
            if template_name and sms_content:
                templates = load_sms_templates()
                templates[template_name] = {
                    "content": sms_content,
                    "char_count": len(sms_content),
                    "created_at": datetime.now().isoformat(),
                    "variables": extract_variables_from_template(sms_content)
                }
                save_sms_templates(templates)
                st.success(f"✅ Template '{template_name}' sauvegardé!")
            else:
                st.error("Veuillez remplir tous les champs")
    
    with col2:
        st.subheader("Templates existants")
        templates = load_sms_templates()
        
        if not templates:
            st.info("Aucun template SMS sauvegardé")
        else:
            for name, template in templates.items():
                with st.expander(f"📝 {name} ({template['char_count']} caractères)"):
                    st.write("**Message:**", template['content'])
                    if template.get('variables'):
                        st.write("**Variables:**", ", ".join(template['variables']))
                    st.write("**Créé le:**", template.get('created_at', 'Inconnu'))
                    
                    col_edit, col_del = st.columns(2)
                    with col_del:
                        if st.button(f"🗑️ Supprimer", key=f"del_tpl_{name}"):
                            templates.pop(name)
                            save_sms_templates(templates)
                            st.rerun()

def extract_variables_from_template(template):
    """Extrait les variables {nom} d'un template"""
    import re
    return re.findall(r'\{(\w+)\}', template)

def send_sms_section():
    st.header("📤 Envoi de SMS - Cameroun")
    
    sms_configs = load_sms_configs()
    sms_templates = load_sms_templates()
    
    if not sms_configs:
        st.error("❌ Aucune configuration SMS trouvée. Configurez d'abord Orange ou MTN.")
        st.info("💡 **Conseil:** Allez dans '📱 Configuration SMS' pour configurer votre opérateur")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Configuration du message")
        
        selected_config = st.selectbox(
            "Configuration SMS à utiliser", 
            list(sms_configs.keys()),
            help="Choisissez la configuration Orange ou MTN"
        )
        
        config = sms_configs[selected_config]
        operator_name = config["operator_info"]["name"]
        
        st.info(f"**Opérateur sélectionné:** {operator_name}")
        
        # Sélection du template ou message personnalisé
        use_template = st.checkbox("Utiliser un template existant")
        
        message_content = ""
        
        if use_template and sms_templates:
            selected_template = st.selectbox("Choisir un template", list(sms_templates.keys()))
            if selected_template:
                template_data = sms_templates[selected_template]
                message_content = template_data["content"]
                st.text_area("Message pré-rempli", value=message_content, height=100, key="template_message", disabled=True)
                
                # Aperçu des variables
                if template_data.get('variables'):
                    st.caption(f"**Variables à remplir:** {', '.join(template_data['variables'])}")
        else:
            message_content = st.text_area(
                "Message personnalisé", 
                height=100, 
                placeholder="Bonjour! Votre colis est arrivé. Passez le récupérer avant {date}. Merci!",
                help="Maximum 160 caractères. Utilisez {variables} pour personnaliser"
            )
        
        # Validation en temps réel
        if message_content:
            char_count = len(message_content)
            st.write(f"📊 {char_count}/160 caractères")
            if char_count > 160:
                st.error("❌ Message trop long!")
    
    with col2:
        st.subheader("👥 Destinataires")
        
        st.info(f"**Format accepté:** {config['operator_info']['format']}")
        
        import_option = st.radio("Source des numéros", ["Saisie manuelle", "Fichier CSV", "Liste de contacts"])
        
        phone_numbers = []
        
        if import_option == "Saisie manuelle":
            numbers_input = st.text_area(
                "Numéros camerounais (un par ligne)",
                placeholder="677123456\n697987654\n237677123456",
                height=150,
                help="Format: 6XXXXXXXX ou 2376XXXXXXXX"
            )
            if numbers_input:
                raw_numbers = [num.strip() for num in numbers_input.split('\n') if num.strip()]
                valid_numbers = []
                invalid_numbers = []
                
                for num in raw_numbers:
                    if validate_cameroon_phone(num):
                        valid_numbers.append(format_cameroon_phone(num))
                    else:
                        invalid_numbers.append(num)
                
                phone_numbers = valid_numbers
                
                if invalid_numbers:
                    st.error(f"❌ {len(invalid_numbers)} numéro(s) invalide(s):")
                    for invalid in invalid_numbers[:5]:
                        st.write(f"`{invalid}`")
        
        elif import_option == "Fichier CSV":
            uploaded_file = st.file_uploader("Importer un CSV avec colonne 'telephone'", type=['csv'])
            if uploaded_file:
                # Implémentation basique du parsing CSV
                import pandas as pd
                try:
                    df = pd.read_csv(uploaded_file)
                    if 'telephone' in df.columns:
                        phone_numbers = [format_cameroon_phone(str(num)) for num in df['telephone'] if validate_cameroon_phone(str(num))]
                        st.success(f"✅ {len(phone_numbers)} numéro(s) valide(s) importé(s)")
                    else:
                        st.error("❌ Colonne 'telephone' non trouvée dans le CSV")
                except Exception as e:
                    st.error(f"Erreur lecture CSV: {str(e)}")
        
        # Aperçu et statistiques
        if phone_numbers:
            st.success(f"📱 **{len(phone_numbers)}** numéro(s) camerounais valide(s)")
            
            with st.expander("👀 Voir les numéros", expanded=False):
                for i, num in enumerate(phone_numbers[:10]):
                    st.write(f"{i+1}. {num}")
                if len(phone_numbers) > 10:
                    st.write(f"... et {len(phone_numbers) - 10} autres")
            
            # Estimation des coûts
            if message_content:
                message_count = (len(message_content) + 159) // 160  # Nombre de SMS nécessaires
                total_cost = len(phone_numbers) * message_count
                st.info(f"💰 Estimation: {total_cost} SMS à envoyer")
    
    # Section d'envoi
    if phone_numbers and message_content:
        st.markdown("---")
        st.subheader("🚀 Envoi des SMS")
        
        if st.button(f"📤 Envoyer {len(phone_numbers)} SMS via {operator_name}", type="primary", use_container_width=True):
            if len(message_content) > 160:
                st.error("❌ Message trop long! Maximum 160 caractères.")
                return
            
            # Simulation d'envoi
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            failed_numbers = []
            
            for i, phone in enumerate(phone_numbers):
                status_text.text(f"Envoi à {phone}... ({i+1}/{len(phone_numbers)})")
                
                # Envoi réel selon l'opérateur
                if config["operator"] == "orange_cm":
                    success = send_sms_orange_cm(phone, message_content, config)
                elif config["operator"] == "mtn_cm":
                    success = send_sms_mtn_cm(phone, message_content, config)
                else:
                    success = False
                
                if success:
                    success_count += 1
                else:
                    failed_numbers.append(phone)
                
                progress_bar.progress((i + 1) / len(phone_numbers))
            
            # Résultats
            st.success(f"✅ **{success_count}/{len(phone_numbers)}** SMS envoyés avec succès!")
            
            if failed_numbers:
                st.error(f"❌ **{len(failed_numbers)}** échec(s):")
                with st.expander("Voir les numéros en échec"):
                    for failed in failed_numbers:
                        st.write(f"`{failed}`")

def send_sms_orange_cm(phone_number: str, message: str, config: dict) -> bool:
    """Envoi SMS via Orange Cameroon API"""
    try:
        # IMPLÉMENTATION RÉELLE POUR ORANGE CAMEROON
        client_id = config.get("client_id", "")
        client_secret = config.get("client_secret", "")
        sender_name = config.get("sender_name", "NEURAFRIK")
        
        # ÉTAPE 1: Obtenir le token OAuth2
        auth_url = "https://api.orange.com/oauth/v3/token"
        auth_data = {
            "grant_type": "client_credentials"
        }
        auth_headers = {
            "Authorization": f"Basic {client_id}:{client_secret}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # ÉTAPE 2: Envoyer le SMS
        sms_url = "https://api.orange.com/smsmessaging/v1/outbound/tel:+237/requests"
        sms_headers = {
            "Authorization": f"Bearer VOTRE_TOKEN_ICI",
            "Content-Type": "application/json"
        }
        sms_data = {
            "outboundSMSMessageRequest": {
                "address": f"tel:+{phone_number}",
                "senderAddress": f"tel:+237{sender_name}",
                "outboundSMSTextMessage": {
                    "message": message
                }
            }
        }
        
        # Pour l'instant, simulation
        st.write(f"🟠 [SIMULATION] SMS Orange à {phone_number}: {message[:50]}...")
        return True
        
    except Exception as e:
        st.error(f"Erreur Orange Cameroon: {str(e)}")
        return False

def send_sms_mtn_cm(phone_number: str, message: str, config: dict) -> bool:
    """Envoi SMS via MTN Cameroon API"""
    try:
        # IMPLÉMENTATION RÉELLE POUR MTN CAMEROON
        api_key = config["api_key"]
        subscription_id = config.get("subscription_id", "")
        sender_name = config.get("sender_name", "")
        
        # URL de l'API MTN Cameroon
        mtn_url = f"https://api.mtn.cm/sms/v1/subscriptions/{subscription_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "to": phone_number,
            "from": sender_name,
            "message": message
        }
        
        # Pour l'instant, simulation
        st.write(f"🟡 [SIMULATION] SMS MTN à {phone_number}: {message[:50]}...")
        return True
        
    except Exception as e:
        st.error(f"Erreur MTN Cameroon: {str(e)}")
        return False