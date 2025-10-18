import streamlit as st
import pandas as pd
import re
from datetime import datetime
from sms_utils import validate_cameroon_phone, format_cameroon_phone, send_sms_orange_cm, send_sms_mtn_cm
from sms_manager import load_sms_configs, load_sms_templates, save_sms_campaign

def send_sms_campaign(df, sms_config, var_mapping, default_values):
    """Version modulaire pour l'envoi de SMS (utilisée par campaign_manager)"""
    
    logs, success_count, error_count = [], 0, 0
    config_data = sms_config["config_data"]
    template_data = sms_config["template_data"]
    sms_template = template_data.get("content", "")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for index, row in df.iterrows():
        phone_number = row["telephone"]
        status_text.text(f"📱 Envoi à {phone_number}... ({index + 1}/{len(df)})")
        
        # Personnalisation du message
        personalized_sms = sms_template
        
        for var in set(re.findall(r'\{(.*?)\}', sms_template)):
            if var in var_mapping and var_mapping[var] in row and pd.notna(row[var_mapping[var]]):
                value = str(row[var_mapping[var]])
            else:
                value = default_values.get(var, f"{{{var}}}")
            
            personalized_sms = personalized_sms.replace(f"{{{var}}}", value)
        
        # Envoi du SMS selon l'opérateur
        try:
            if config_data["operator"] == "orange_cm":
                success = send_sms_orange_cm(phone_number, personalized_sms, config_data)
            elif config_data["operator"] == "mtn_cm":
                success = send_sms_mtn_cm(phone_number, personalized_sms, config_data)
            else:
                success = False
            
            if success:
                logs.append(f"✅ SMS envoyé à {phone_number}")
                success_count += 1
            else:
                logs.append(f"❌ Erreur avec {phone_number}")
                error_count += 1
                
        except Exception as e:
            error_msg = f"❌ Erreur avec {phone_number}: {str(e)}"
            logs.append(error_msg)
            error_count += 1
        
        progress_bar.progress((index + 1) / len(df))
    
    status_text.text("✅ Envoi des SMS terminé!")
    
    return {
        "success_count": success_count,
        "error_count": error_count,
        "logs": logs
    }

def send_sms_section():
    """Section originale d'envoi de SMS (conservée pour compatibilité)"""
    st.header("📤 Envoyer une campagne SMS")

    sms_configs = load_sms_configs()
    sms_templates = load_sms_templates()

    if not sms_configs or not sms_templates:
        st.warning("Veuillez configurer au moins un opérateur SMS et un template.")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        selected_sms_config = st.selectbox("Configuration SMS", list(sms_configs.keys()))
    
    with col2:
        selected_template = st.selectbox("Template SMS", list(sms_templates.keys()))

    uploaded_file = st.file_uploader("Fichier CSV des destinataires", type="csv", key="sms_csv")
    
    if uploaded_file and selected_template:
        df = pd.read_csv(uploaded_file)
        
        if "telephone" not in df.columns:
            st.error("❌ Le CSV doit contenir une colonne 'telephone'")
            return
            
        df = df.dropna(subset=["telephone"])
        df["telephone"] = df["telephone"].astype(str)
        
        # Validation des numéros
        valid_numbers = []
        invalid_numbers = []
        
        for idx, row in df.iterrows():
            phone = str(row["telephone"]).strip()
            if validate_cameroon_phone(phone):
                valid_numbers.append(format_cameroon_phone(phone))
            else:
                invalid_numbers.append({"ligne": idx + 2, "numero": phone})
        
        if invalid_numbers:
            st.warning(f"⚠️ {len(invalid_numbers)} numéro(s) invalide(s) détectés:")
            invalid_df = pd.DataFrame(invalid_numbers)
            st.dataframe(invalid_df, use_container_width=True)
        
        if not valid_numbers:
            st.error("❌ Aucun numéro valide trouvé dans le fichier")
            return
            
        st.success(f"✅ **{len(valid_numbers)}** numéro(s) camerounais valide(s) trouvé(s)")

        # Charger le template
        template = sms_templates[selected_template]
        sms_template = template.get("content", "")
        
        # Variables détectées
        variables = set(re.findall(r'\{(.*?)\}', sms_template))
        var_mapping, default_values = {}, {}

        if variables:
            st.subheader("🔧 Personnalisation des variables")
            
            for var in variables:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if var in df.columns:
                        var_mapping[var] = var
                        st.write(f"✔️ `{var}` détecté dans CSV (colonne '{var}')")
                    else:
                        options = [col for col in df.columns if col not in ['telephone', 'email']]
                        selected_col = st.selectbox(f"Colonne pour '{var}'", ["(Ignorer)"] + options, key=f"sms_var_{var}")
                        if selected_col != "(Ignorer)":
                            var_mapping[var] = selected_col
                with col2:
                    default_values[var] = st.text_input(f"Valeur par défaut", value=f"{{{var}}}", key=f"default_{var}")

        # Aperçu
        st.subheader("👀 Aperçu du premier SMS")
        
        preview_sms = sms_template
        if valid_numbers and not df.empty:
            first_row = df.iloc[0]
            
            for var in variables:
                if var in var_mapping and var_mapping[var] in first_row and pd.notna(first_row[var_mapping[var]]):
                    preview_value = str(first_row[var_mapping[var]])
                else:
                    preview_value = default_values.get(var, f"{{{var}}}")
                
                preview_sms = preview_sms.replace(f"{{{var}}}", preview_value)

        st.text_area("Aperçu du message", preview_sms, height=100, disabled=True)
        
        char_count = len(preview_sms)
        st.write(f"📊 **{char_count}/160** caractères")
        
        # Bouton d'envoi
        if st.button("📤 Démarrer l'envoi des SMS", type="primary"):
            if char_count > 160:
                st.error("❌ Message trop long!")
                return
            
            config = sms_configs[selected_sms_config]
            
            # Utilisation de la nouvelle fonction modulaire
            sms_config = {
                "config_data": config,
                "template_data": template
            }
            
            # Filtrer le dataframe pour garder seulement les numéros valides
            valid_df = df[df["telephone"].apply(lambda x: validate_cameroon_phone(str(x)))]
            valid_df["telephone"] = valid_df["telephone"].apply(lambda x: format_cameroon_phone(str(x)))
            
            results = send_sms_campaign(valid_df, sms_config, var_mapping, default_values)
            
            # Affichage des résultats
            st.subheader("📊 Résultats")
            st.success(f"{results['success_count']} SMS envoyés")
            if results['error_count'] > 0:
                st.error(f"{results['error_count']} erreurs")
            
            # Téléchargement des logs
            st.download_button(
                "📥 Télécharger les logs",
                "\n".join(results['logs']),
                file_name=f"logs_sms_{datetime.now().strftime('%Y%m%d')}.txt"
            )