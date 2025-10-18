import json
import os

def load_data():
    """Charge les données depuis les fichiers JSON"""
    # SMTP Configs
    if os.path.exists("smtp_configs.json"):
        with open("smtp_configs.json", "r") as f:
            smtp_configs = json.load(f)
    else:
        smtp_configs = {}

    # Email Templates
    if os.path.exists("email_templates.json"):
        with open("email_templates.json", "r") as f:
            email_templates = json.load(f)
    else:
        email_templates = {}

    # SMS Templates (NOUVEAU)
    if os.path.exists("sms_templates.json"):
        with open("sms_templates.json", "r") as f:
            sms_templates = json.load(f)
    else:
        sms_templates = {}

    # RETOURNER 3 VALEURS maintenant
    return smtp_configs, email_templates, sms_templates

def save_smtp_configs(smtp_configs):
    with open("smtp_configs.json", "w") as f:
        json.dump(smtp_configs, f, indent=4)

def save_email_templates(email_templates):
    with open("email_templates.json", "w") as f:
        json.dump(email_templates, f, indent=4)

def save_sms_templates(sms_templates):
    with open("sms_templates.json", "w") as f:
        json.dump(sms_templates, f, indent=4)