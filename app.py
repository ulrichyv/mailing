import streamlit as st
from data_manager import load_data
from smtp_utils import smtp_config_section
from template_utils import template_section
from sms_utils import sms_config_section, sms_template_section
from campaign_manager import campaign_section
from email_sender import send_email_section
from sms_sender import send_sms_section

st.set_page_config(page_title="Email & SMS Marketing Manager", page_icon="📧", layout="wide")

# Initialisation CORRIGÉE - Maintenant 3 valeurs
if 'smtp_configs' not in st.session_state or 'email_templates' not in st.session_state:
    # load_data() retourne maintenant 3 valeurs : smtp_configs, email_templates, sms_templates
    smtp_configs, email_templates, sms_templates = load_data()
    st.session_state.smtp_configs = smtp_configs
    st.session_state.email_templates = email_templates
    st.session_state.sms_templates = sms_templates  # NOUVEAU

# Sidebar - OPTIONS COMPLÈTES
menu_options = [
    "🎯 Campagne Multi-Canal",
    "📤 Envoi d'Emails",
    "📤 Envoi de SMS",
    "⚙️ Configuration SMTP", 
    "⚙️ Configuration SMS",
    "📝 Templates Email & SMS",  # MODIFIÉ - Un seul onglet pour tous les templates
    "📊 Historique"
]

choice = st.sidebar.selectbox("Navigation", menu_options)

if choice == "🎯 Campagne Multi-Canal":
    campaign_section()
elif choice == "📤 Envoi d'Emails":
    send_email_section()
elif choice == "📤 Envoi de SMS":
    send_sms_section()
elif choice == "⚙️ Configuration SMTP":
    smtp_config_section()
elif choice == "⚙️ Configuration SMS":
    sms_config_section()
elif choice == "📝 Templates Email & SMS":  # MODIFIÉ
    template_section()  # Maintenant gère email + SMS
elif choice == "📊 Historique":
    st.info("📊 Historique des campagnes (à venir)")