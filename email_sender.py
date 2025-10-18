import streamlit as st
import pandas as pd
import smtplib, ssl, re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

def safe_get_value(var, row, var_mapping, default_values):
    """Version sécurisée pour récupérer les valeurs des variables"""
    try:
        if var in var_mapping and var_mapping[var] in row:
            value = row[var_mapping[var]]
            # Vérifier tous les cas de valeurs nulles
            if pd.isna(value) or value is None or str(value).strip() == "":
                return default_values.get(var, f"[{var}]") or f"[{var}]"
            return str(value).strip()
        else:
            return default_values.get(var, f"[{var}]") or f"[{var}]"
    except Exception:
        return default_values.get(var, f"[{var}]") or f"[{var}]"

def send_email_campaign(df, email_config, var_mapping, default_values, attachment_file=None):
    """Version modulaire pour l'envoi d'emails (CORRIGÉE)"""
    
    logs, success_count, error_count = [], 0, 0
    smtp_config = email_config["config_data"]
    template = email_config["template_data"]
    
    # S'assurer que les templates ne sont pas None
    html_template = template.get("html", "") or ""
    text_template = template.get("text", "") or ""
    subject_template = template.get("subject", "Sans objet") or "Sans objet"
    
    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
            server.starttls(context=context)
            server.login(smtp_config["email"], smtp_config["password"])
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, row in df.iterrows():
                # Récupérer l'email de manière sécurisée
                email_dest = str(row.get("email", "") or "").strip()
                
                if not email_dest or "@" not in email_dest:
                    logs.append(f"❌ Email invalide ignoré: {email_dest}")
                    error_count += 1
                    continue
                
                status_text.text(f"📧 Envoi à {email_dest}... ({index + 1}/{len(df)})")
                
                # Personnalisation du message - VERSION SÉCURISÉE
                personalized_html = html_template
                personalized_text = text_template
                personalized_subject = subject_template
                
                # Trouver toutes les variables dans tous les templates
                all_vars = set(re.findall(r'\[(.*?)\]', html_template + text_template + subject_template))
                
                for var in all_vars:
                    # Utiliser la fonction sécurisée
                    value = safe_get_value(var, row, var_mapping, default_values)
                    
                    # S'assurer que la valeur n'est jamais None
                    safe_value = str(value) if value is not None else f"[{var}]"
                    
                    # Remplacer dans tous les templates
                    personalized_html = personalized_html.replace(f"[{var}]", safe_value)
                    personalized_text = personalized_text.replace(f"[{var}]", safe_value)
                    personalized_subject = personalized_subject.replace(f"[{var}]", safe_value)
                
                # Création du message
                message = MIMEMultipart("mixed")
                message["From"] = smtp_config['email']
                message["To"] = email_dest
                message["Subject"] = personalized_subject
                
                alternative = MIMEMultipart('alternative')
                if personalized_text.strip():
                    alternative.attach(MIMEText(personalized_text, "plain"))
                if personalized_html.strip():
                    alternative.attach(MIMEText(personalized_html, "html"))
                message.attach(alternative)
                
                # Pièce jointe (si fournie)
                if attachment_file is not None:
                    try:
                        attachment_file.seek(0)
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment_file.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={attachment_file.name}")
                        message.attach(part)
                    except Exception as e:
                        logs.append(f"⚠️ Erreur pièce jointe pour {email_dest}: {str(e)}")
                
                try:
                    server.sendmail(smtp_config["email"], email_dest, message.as_string())
                    logs.append(f"✅ Email envoyé à {email_dest}")
                    success_count += 1
                except Exception as e:
                    logs.append(f"❌ Erreur {email_dest}: {str(e)}")
                    error_count += 1
                
                progress_bar.progress((index + 1) / len(df))
            
            status_text.text("✅ Envoi des emails terminé!")
            
    except Exception as e:
        # Message d'erreur sécurisé
        error_msg = f"❌ Erreur SMTP globale: {str(e) if e else 'Erreur inconnue'}"
        logs.append(error_msg)
    
    return {
        "success_count": success_count,
        "error_count": error_count,
        "logs": logs
    }

def send_email_section():
    """Section originale d'envoi d'emails (conservée pour compatibilité)"""
    st.header("🚀 Envoyer une campagne email")

    if not st.session_state.smtp_configs or not st.session_state.email_templates:
        st.warning("Veuillez configurer au moins un serveur SMTP et un template.")
        return

    selected_smtp = st.selectbox("Configuration SMTP", list(st.session_state.smtp_configs.keys()))
    selected_template = st.selectbox("Template d'email", list(st.session_state.email_templates.keys()))

    uploaded_file = st.file_uploader("Fichier CSV des destinataires", type="csv")
    attachment_file = st.file_uploader("Pièce jointe (facultatif)")

    if uploaded_file and selected_template:
        df = pd.read_csv(uploaded_file)
        if "email" not in df.columns:
            st.error("Le CSV doit contenir une colonne 'email'")
            return
        df = df.dropna(subset=["email"])
        st.success(f"{len(df)} destinataires valides trouvés")

        # Charger le template
        template = st.session_state.email_templates[selected_template]
        html_template = template.get("html", "") or ""
        text_template = template.get("text", "") or ""

        # Variables détectées
        variables = set(re.findall(r'\[(.*?)\]', html_template + text_template))
        var_mapping, default_values = {}, {}

        if variables:
            st.subheader("🔧 Personnalisation des variables")
            for var in variables:
                col1, col2 = st.columns([2, 1])
                with col1:
                    if var in df.columns:
                        var_mapping[var] = var
                        st.write(f"✔️ `{var}` détecté dans CSV (colonne '{var}')")
                    else:
                        options = [col for col in df.columns if col != 'email']
                        selected_col = st.selectbox(f"Colonne pour '{var}'", ["(Ignorer)"] + options, key=f"var_{var}")
                        if selected_col != "(Ignorer)":
                            var_mapping[var] = selected_col
                with col2:
                    default_val = st.text_input(f"Valeur par défaut pour '{var}'", value=f"[{var}]")
                    default_values[var] = default_val or f"[{var}]"  # S'assurer que ce n'est pas None

        # Aperçu
        st.subheader("👀 Aperçu du premier email")
        preview_html, preview_text = html_template, text_template
        if not df.empty:
            for var in variables:
                # Utiliser la fonction sécurisée pour l'aperçu aussi
                value = safe_get_value(var, df.iloc[0], var_mapping, default_values)
                safe_value = str(value) if value is not None else f"[{var}]"
                preview_html = preview_html.replace(f"[{var}]", safe_value)
                preview_text = preview_text.replace(f"[{var}]", safe_value)

        if preview_html.strip():
            st.components.v1.html(preview_html, height=400, scrolling=True)
        else:
            st.text_area("Aperçu (texte brut)", preview_text, height=200)

        # Envoi
        smtp_config = st.session_state.smtp_configs[selected_smtp]
        password = st.text_input("Mot de passe SMTP", type="password", value=smtp_config["password"])
        if st.button("🚀 Démarrer l'envoi des emails"):
            
            # Utilisation de la nouvelle fonction modulaire
            email_config = {
                "config_data": smtp_config,
                "template_data": template
            }
            
            results = send_email_campaign(df, email_config, var_mapping, default_values, attachment_file)
            
            # Affichage des résultats
            st.subheader("📊 Résultats")
            st.success(f"{results['success_count']} emails envoyés")
            if results['error_count'] > 0:
                st.error(f"{results['error_count']} erreurs")
            
            # Téléchargement des logs
            st.download_button(
                "📥 Télécharger les logs", 
                "\n".join(results['logs']), 
                file_name=f"logs_email_{datetime.now().strftime('%Y%m%d')}.txt"
            )