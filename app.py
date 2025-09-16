import streamlit as st
from data_manager import load_data
from smtp_utils import smtp_config_section
from template_utils import template_section
from email_sender import send_email_section

st.set_page_config(page_title="Email Marketing Manager", page_icon="📧", layout="wide")

# Initialisation
if 'smtp_configs' not in st.session_state or 'email_templates' not in st.session_state:
    st.session_state.smtp_configs, st.session_state.email_templates = load_data()

# Sidebar
menu_options = ["Configuration SMTP", "Gestion des Templates", "Envoi d'Emails", "Historique"]
choice = st.sidebar.selectbox("Navigation", menu_options)

if choice == "Configuration SMTP":
    smtp_config_section()
elif choice == "Gestion des Templates":
    template_section()
elif choice == "Envoi d'Emails":
    send_email_section()
elif choice == "Historique":
    st.info("📊 Historique des campagnes (à venir)")
