import streamlit as st
from datetime import datetime
from data_manager import save_email_templates
from ai_template_generator import ai_template_interface

def template_section():
    st.header("📝 Gestion des Templates d'Emails")
    
    # === Nouvel onglet pour l'IA ===
    tab1, tab2 = st.tabs(["📝 Création Manuelle", "🤖 Génération IA"])
    
    with tab1:
        manual_template_creation()
    
    with tab2:
        ai_template_section()
    
    # Afficher les templates existants
    display_existing_templates()

def manual_template_creation():
    """Version originale de la création manuelle"""
    with st.expander("Créer un nouveau template", expanded=True):
        with st.form("template_form"):
            template_name = st.text_input("Nom du template*")
            email_subject = st.text_input("Sujet de l'email*")

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
                    # Sauvegarde
                    st.session_state.email_templates[template_name] = {
                        "subject": email_subject,
                        "html": html_content if option in ["HTML uniquement", "Texte + HTML"] else None,
                        "text": text_content if option in ["Texte uniquement", "Texte + HTML"] else None,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "manual"
                    }
                    save_email_templates(st.session_state.email_templates)
                    st.success(f"✅ Template '{template_name}' sauvegardé avec succès !")
                    st.rerun()

def ai_template_section():
    """Interface pour la génération IA"""
    ai_template_interface()
    
    # Si un template IA a été sélectionné, pré-remplir le formulaire
    if hasattr(st.session_state, 'selected_ai_template') and st.session_state.selected_ai_template:
        template = st.session_state.selected_ai_template
        
        st.info("🎯 Template IA sélectionné - Complétez les informations ci-dessous")
        
        with st.form("ai_template_finalize"):
            template_name = st.text_input("Nom du template*", value=f"Template IA - {datetime.now().strftime('%H:%M')}")
            email_subject = st.text_input("Sujet de l'email*", value="Votre email personnalisé")
            
            # Aperçu final
            st.markdown("**Aperçu du template généré :**")
            st.components.v1.html(template['html'], height=300, scrolling=True)
            
            if st.form_submit_button("💾 Sauvegarder ce template"):
                st.session_state.email_templates[template_name] = {
                    "subject": email_subject,
                    "html": template['html'],
                    "text": template['text'],
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "ia_generated"
                }
                save_email_templates(st.session_state.email_templates)
                del st.session_state.selected_ai_template
                st.success("✅ Template IA sauvegardé !")
                st.rerun()

def display_existing_templates():
    """Affiche les templates existants"""
    st.subheader("📂 Templates existants")
    
    if st.session_state.email_templates:
        template_names = list(st.session_state.email_templates.keys())
        selected_template = st.selectbox("Sélectionner un template à modifier", [""] + template_names)

        if selected_template:
            template = st.session_state.email_templates[selected_template]
            
            # Indicateur de source
            source_badge = "🤖 IA" if template.get("source") == "ia_generated" else "✍️ Manuel"
            st.write(f"**Source :** {source_badge}")
            
            with st.form("edit_template_form"):
                new_name = st.text_input("Nom du template", value=selected_template)
                new_subject = st.text_input("Sujet", value=template["subject"])

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
                    new_html = st.text_area("Contenu HTML", value=template.get("html") or "", height=300)
                if option_edit in ["Texte uniquement", "Texte + HTML"]:
                    new_text = st.text_area("Contenu Texte", value=template.get("text") or "", height=300)

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
                            del st.session_state.email_templates[selected_template]
                        st.session_state.email_templates[new_name] = {
                            "subject": new_subject,
                            "html": new_html if option_edit in ["HTML uniquement", "Texte + HTML"] else None,
                            "text": new_text if option_edit in ["Texte uniquement", "Texte + HTML"] else None,
                            "created_at": template.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                            "source": template.get("source", "manual")
                        }
                        save_email_templates(st.session_state.email_templates)
                        st.success("✅ Template mis à jour avec succès !")
                        st.rerun()

                if delete_template:
                    del st.session_state.email_templates[selected_template]
                    save_email_templates(st.session_state.email_templates)
                    st.success("🗑️ Template supprimé !")
                    st.rerun()
    else:
        st.info("Aucun template enregistré.")