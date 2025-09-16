import streamlit as st
from data_manager import save_smtp_configs

def smtp_config_section():
    st.header("🔧 Configuration des serveurs SMTP")

    with st.expander("Ajouter une nouvelle configuration SMTP"):
        with st.form("smtp_config_form"):
            config_name = st.text_input("Nom de la configuration*")
            smtp_server = st.text_input("Serveur SMTP*")
            smtp_port = st.number_input("Port SMTP*", min_value=1, max_value=65535, value=587)
            smtp_email = st.text_input("Email*")
            smtp_password = st.text_input("Mot de passe*", type="password")

            submitted = st.form_submit_button("Sauvegarder")
            if submitted:
                if config_name and smtp_server and smtp_port and smtp_email:
                    st.session_state.smtp_configs[config_name] = {
                        "server": smtp_server,
                        "port": smtp_port,
                        "email": smtp_email,
                        "password": smtp_password
                    }
                    save_smtp_configs(st.session_state.smtp_configs)
                    st.success("Configuration SMTP sauvegardée!")
                else:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")

    st.subheader("Configurations existantes")
    if st.session_state.smtp_configs:
        for config_name, config in st.session_state.smtp_configs.items():
            with st.expander(f"Configuration: {config_name}"):
                st.write(f"**Serveur:** {config['server']}")
                st.write(f"**Port:** {config['port']}")
                st.write(f"**Email:** {config['email']}")

                if st.button(f"Supprimer {config_name}", key=f"del_{config_name}"):
                    del st.session_state.smtp_configs[config_name]
                    save_smtp_configs(st.session_state.smtp_configs)
                    st.rerun()
    else:
        st.info("Aucune configuration SMTP enregistrée.")
