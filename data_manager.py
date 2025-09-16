import json
import os

def load_data():
    """Charge les données depuis les fichiers JSON"""
    if os.path.exists("smtp_configs.json"):
        with open("smtp_configs.json", "r") as f:
            smtp_configs = json.load(f)
    else:
        smtp_configs = {}

    if os.path.exists("email_templates.json"):
        with open("email_templates.json", "r") as f:
            email_templates = json.load(f)
    else:
        email_templates = {}

    return smtp_configs, email_templates

def save_smtp_configs(smtp_configs):
    with open("smtp_configs.json", "w") as f:
        json.dump(smtp_configs, f, indent=4)

def save_email_templates(email_templates):
    with open("email_templates.json", "w") as f:
        json.dump(email_templates, f, indent=4)
