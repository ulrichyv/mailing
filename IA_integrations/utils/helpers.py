from typing import Dict, List, Any

def get_smart_default_value(variable_name: str) -> str:
    """Retourne une valeur par défaut intelligente selon le nom de variable"""
    defaults = {
        # Informations personnelles
        "Nom": "Dupont",
        "Prénom": "Jean",
        "Email": "jean.dupont@email.com",
        "Téléphone": "+33 1 23 45 67 89",
        "Poste": "Directeur Marketing",
        
        # Entreprise
        "Entreprise": "Neurafrik",
        "Ville": "Paris",
        "Site web": "https://neurafrik.com",
        "Adresse": "123 Avenue des Champs-Élysées",
        "Secteur": "Technologie",
        
        # Offres
        "Produit": "Solution IA",
        "Service": "Service Premium",
        "Offre": "Offre Exclusive",
        "Promotion": "20% de réduction",
        "Montant": "199€",
        "Prix": "199€",
        
        # Dates
        "Date": "15 décembre 2024",
        "DateLimite": "31 décembre 2024",
        "DateDébut": "1 janvier 2024",
        "DateFin": "31 décembre 2024",
        
        # Liens
        "Lien": "https://neurafrik.com/offre",
        "LienProduit": "https://neurafrik.com/produit",
        "LienSite": "https://neurafrik.com",
        "LienDésabonnement": "https://neurafrik.com/desabonnement",
        
        # CTAs
        "CTA": "Découvrir l'offre",
        "Bouton": "Je profite de l'offre",
        "Action": "Télécharger maintenant",
        "Urgence": "Offre limitée !"
    }
    
    return defaults.get(variable_name, f"Valeur {variable_name}")

def organize_variables_by_category(detected_variables: List[str], categories: Dict[str, Any]) -> Dict[str, List[str]]:
    """Organise les variables détectées par catégorie"""
    organized = {}
    
    for var in detected_variables:
        found_category = None
        for category, info in categories.items():
            if var in info['variables']:
                found_category = category
                break
        
        if found_category:
            organized.setdefault(found_category, []).append(var)
        else:
            organized.setdefault("🔤 Autres Variables", []).append(var)
    
    return organized