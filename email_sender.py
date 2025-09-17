import streamlit as st
import pandas as pd
import smtplib, ssl, re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

def send_email_section():
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
                    default_values[var] = st.text_input(f"Valeur par défaut pour '{var}'", value=f"[{var}]")

        # Aperçu
        st.subheader("👀 Aperçu du premier email")
        preview_html, preview_text = html_template, text_template
        if not df.empty:
            for var in variables:
                if var in var_mapping:
                    col = var_mapping[var]
                    preview_value = str(df.iloc[0][col]) if pd.notna(df.iloc[0][col]) else default_values.get(var, f"[{var}]")
                else:
                    preview_value = default_values.get(var, f"[{var}]")
                preview_html = preview_html.replace(f"[{var}]", preview_value)
                preview_text = preview_text.replace(f"[{var}]", preview_value)

        if preview_html.strip():
            st.components.v1.html(preview_html, height=400, scrolling=True)
        else:
            st.text_area("Aperçu (texte brut)", preview_text, height=200)

        # Envoi
        smtp_config = st.session_state.smtp_configs[selected_smtp]
        password = st.text_input("Mot de passe SMTP", type="password", value=smtp_config["password"])
        if st.button("🚀 Démarrer l'envoi des emails"):
            context = ssl.create_default_context()
            logs, success_count, error_count, results = [], 0, 0, []

            try:
                with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
                    server.starttls(context=context)
                    server.login(smtp_config["email"], password)
                    progress_bar = st.progress(0)

                    for index, row in df.iterrows():
                        email_dest = row["email"]
                        personalized_html, personalized_text = html_template, text_template

                        for var in variables:
                            if var in var_mapping and var_mapping[var] in row and pd.notna(row[var_mapping[var]]):
                                value = str(row[var_mapping[var]])
                            else:
                                value = default_values.get(var, f"[{var}]")
                            personalized_html = personalized_html.replace(f"[{var}]", value)
                            personalized_text = personalized_text.replace(f"[{var}]", value)

                        message = MIMEMultipart("mixed")
                        message["From"], message["To"], message["Subject"] = smtp_config['email'], email_dest, template["subject"]
                        alternative = MIMEMultipart('alternative')
                        if personalized_text.strip():
                            alternative.attach(MIMEText(personalized_text, "plain"))
                        if personalized_html.strip():
                            alternative.attach(MIMEText(personalized_html, "html"))
                        message.attach(alternative)

                        if attachment_file is not None:
                            attachment_file.seek(0)
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment_file.read())
                            encoders.encode_base64(part)
                            part.add_header("Content-Disposition", f"attachment; filename={attachment_file.name}")
                            message.attach(part)

                        try:
                            server.sendmail(smtp_config["email"], email_dest, message.as_string())
                            logs.append(f"✅ Envoyé à {email_dest}")
                            results.append({"Email": email_dest, "Statut": "✅ Envoyé"})
                            success_count += 1
                        except Exception as e:
                            logs.append(f"❌ Erreur {email_dest}: {str(e)}")
                            results.append({"Email": email_dest, "Statut": f"❌ {str(e)}"})
                            error_count += 1

                        progress_bar.progress((index + 1) / len(df))

            except Exception as e:
                st.error(f"Erreur SMTP: {e}")

            # Résultats
            st.subheader("📊 Résultats")
            st.success(f"{success_count} emails envoyés")
            if error_count > 0:
                st.error(f"{error_count} erreurs")
            st.dataframe(pd.DataFrame(results))
            st.download_button("📥 Télécharger les logs", "\n".join(logs), file_name=f"logs_{datetime.now().strftime('%Y%m%d')}.txt")
