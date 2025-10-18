import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class SMSConfig:
    def __init__(self, name: str, operator: str, api_key: str, sender_name: str):
        self.name = name
        self.operator = operator
        self.api_key = api_key
        self.sender_name = sender_name

def load_sms_configs():
    """Charge les configurations SMS"""
    if os.path.exists("sms_configs.json"):
        with open("sms_configs.json", "r") as f:
            return json.load(f)
    return {}

def save_sms_configs(sms_configs):
    """Sauvegarde les configurations SMS"""
    with open("sms_configs.json", "w") as f:
        json.dump(sms_configs, f, indent=4)

def load_sms_templates():
    """Charge les templates SMS"""
    if os.path.exists("sms_templates.json"):
        with open("sms_templates.json", "r") as f:
            return json.load(f)
    return {}

def save_sms_templates(sms_templates):
    """Sauvegarde les templates SMS"""
    with open("sms_templates.json", "w") as f:
        json.dump(sms_templates, f, indent=4)

def load_sms_campaigns():
    """Charge l'historique des campagnes SMS"""
    if os.path.exists("sms_campaigns.json"):
        with open("sms_campaigns.json", "r") as f:
            return json.load(f)
    return []

def save_sms_campaign(campaign_data):
    """Sauvegarde une campagne SMS"""
    campaigns = load_sms_campaigns()
    campaigns.append({
        **campaign_data,
        "id": len(campaigns) + 1,
        "sent_at": datetime.now().isoformat()
    })
    with open("sms_campaigns.json", "w") as f:
        json.dump(campaigns, f, indent=4)