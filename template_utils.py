import streamlit as st
from datetime import datetime
from data_manager import save_email_templates

def template_section():
    st.header("📝 Gestion des Templates d'Emails")

    with st.expander("Créer un nouveau template"):
        with st.form("template_form"):
            template_name = st.text_input("Nom du template*")
            email_subject = st.text_input("Sujet de l'email*")

            col1, col2 = st.tabs(["HTML", "Texte"])

            with col1:
                html_content = st.text_area("Contenu HTML*", height=300)

            with col2:
                text_content = st.text_area("Contenu Texte*", height=300)

            submitted = st.form_submit_button("Sauvegarder le template")
            if submitted:
                if template_name and email_subject and html_content and text_content:
                    st.session_state.email_templates[template_name] = {
                        "subject": email_subject,
                        "html": html_content,
                        "text": text_content,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_email_templates(st.session_state.email_templates)
                    st.success("Template sauvegardé!")
                else:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")

    # Edition des templates existants
    st.subheader("Templates existants")
    if st.session_state.email_templates:
        template_names = list(st.session_state.email_templates.keys())
        selected_template = st.selectbox("Sélectionner un template à modifier", [""] + template_names)

        if selected_template:
            template = st.session_state.email_templates[selected_template]
            with st.form("edit_template_form"):
                new_name = st.text_input("Nom du template", value=selected_template)
                new_subject = st.text_input("Sujet", value=template["subject"])
                new_html = st.text_area("Contenu HTML", value=template["html"], height=300)
                new_text = st.text_area("Contenu Texte", value=template["text"], height=300)

                col1, col2 = st.columns(2)
                save_changes = col1.form_submit_button("Sauvegarder les modifications")
                delete_template = col2.form_submit_button("Supprimer")

                if save_changes:
                    if new_name != selected_template:
                        del st.session_state.email_templates[selected_template]
                    st.session_state.email_templates[new_name] = {
                        "subject": new_subject,
                        "html": new_html,
                        "text": new_text,
                        "created_at": template.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    }
                    save_email_templates(st.session_state.email_templates)
                    st.success("Template mis à jour!")
                    st.rerun()

                if delete_template:
                    del st.session_state.email_templates[selected_template]
                    save_email_templates(st.session_state.email_templates)
                    st.success("Template supprimé!")
                    st.rerun()
    else:
        st.info("Aucun template enregistré.")
