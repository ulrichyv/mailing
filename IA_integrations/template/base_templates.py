class BaseTemplates:
    """Classe contenant les templates prédéfinis"""
    
    @staticmethod
    def get_styles_config():
        return {
            "professional": {"primary": "#2563eb", "secondary": "#1e40af", "bg_color": "#f8fafc"},
            "modern": {"primary": "#7c3aed", "secondary": "#6d28d9", "bg_color": "#fafafa"},
            "creative": {"primary": "#dc2626", "secondary": "#b91c1c", "bg_color": "#fef7ed"},
            "minimalist": {"primary": "#000000", "secondary": "#374151", "bg_color": "#ffffff"},
            "warm": {"primary": "#ea580c", "secondary": "#c2410c", "bg_color": "#fef7ed"}
        }
    
    def generate_basic_template(self, prompt: str, style_preference: str) -> str:
        style = self.get_styles_config().get(style_preference, self.get_styles_config()["professional"])
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: {style['bg_color']};">
    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <tr>
            <td style="padding: 30px 25px; background: linear-gradient(135deg, {style['primary']}, {style['secondary']}); text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">[Entreprise]</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Votre partenaire de confiance</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 40px 30px;">
                <h2 style="color: #1f2937; margin: 0 0 20px 0; font-size: 22px;">Bonjour [Prénom] [Nom],</h2>
                <p style="color: #4b5563; line-height: 1.6; font-size: 16px; margin: 0 0 20px 0;">
                    Nous sommes ravis de vous contacter de la part de <strong>[Entreprise]</strong>. 
                    Votre profil en tant que <strong>[Poste]</strong> à <strong>[Entreprise]</strong> 
                    a retenu toute notre attention.
                </p>
                <p style="color: #4b5563; line-height: 1.6; font-size: 16px; margin: 0 0 30px 0;">
                    Nous pensons que notre solution <strong>[Produit]</strong> pourrait vous aider 
                    à atteindre vos objectifs plus efficacement.
                </p>
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; border-left: 4px solid {style['primary']}; margin: 25px 0;">
                    <h3 style="color: {style['primary']}; margin: 0 0 10px 0; font-size: 18px;">🎯 Offre Spéciale</h3>
                    <p style="color: #6b7280; margin: 0; font-size: 15px;">
                        Bénéficiez de <strong>[Promotion]</strong> sur [Produit] jusqu'au [Date] !
                    </p>
                </div>
                <table border="0" cellpadding="0" cellspacing="0" style="margin: 30px 0; text-align: center;">
                    <tr>
                        <td>
                            <a href="[Lien]" style="background: {style['primary']}; color: #ffffff; padding: 14px 35px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; font-size: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                Découvrir l'offre ›
                            </a>
                        </td>
                    </tr>
                </table>
                <p style="color: #6b7280; font-size: 14px; line-height: 1.5; margin: 30px 0 0 0;">
                    Cordialement,<br>
                    <strong>L'équipe [Entreprise]</strong><br>
                    📞 [Téléphone] | 🌐 [Site web]<br>
                    📧 [Email]
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding: 25px 30px; background: #f9fafb; text-align: center;">
                <p style="color: #9ca3af; font-size: 12px; line-height: 1.4; margin: 0;">
                    &copy; 2024 [Entreprise]. Tous droits réservés.<br>
                    <a href="#" style="color: {style['primary']}; text-decoration: none;">Se désabonner</a> • 
                    <a href="#" style="color: {style['primary']}; text-decoration: none;">Gérer mes préférences</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>'''
    
    def generate_professional_template(self, prompt: str, style_preference: str) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: #ffffff;">
        <tr>
            <td style="padding: 30px 20px; background: #2563eb; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px;">[Entreprise]</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Communication Professionnelle</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 40px 30px;">
                <h2 style="color: #1e293b; margin-top: 0;">Bonjour [Prénom] [Nom],</h2>
                <p style="color: #475569; line-height: 1.6; font-size: 16px;">
                    Nous sommes ravis de vous contacter concernant [Produit]. 
                    Votre entreprise <strong>[Entreprise]</strong> située à [Ville] représente 
                    un partenaire idéal pour nous.
                </p>
                <div style="background: #f1f5f9; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="color: #334155; margin-top: 0;">Offre Spéciale pour vous</h3>
                    <p style="color: #475569; margin: 10px 0;">
                        Bénéficiez de <strong>[Promotion]</strong> sur [Produit] jusqu'au [Date].
                    </p>
                </div>
                <table border="0" cellpadding="0" cellspacing="0" style="margin: 30px 0; text-align: center;">
                    <tr>
                        <td>
                            <a href="[Lien]" style="background: #2563eb; color: #ffffff; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Découvrir l'offre</a>
                        </td>
                    </tr>
                </table>
                <p style="color: #64748b; font-size: 14px;">
                    Cordialement,<br>
                    L'équipe [Entreprise]<br>
                    [Site web] | [Téléphone]
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px; background: #f8fafc; text-align: center;">
                <p style="color: #64748b; font-size: 14px; margin: 0;">
                    &copy; 2024 [Entreprise]. Tous droits réservés.<br>
                    <a href="#" style="color: #2563eb; text-decoration: none;">Se désabonner</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    def generate_modern_template(self, prompt: str, style_preference: str) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <tr>
            <td style="padding: 40px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: 300;">[Entreprise]</h1>
                <p style="color: rgba(255,255,255,0.8); margin: 15px 0 0 0; font-size: 16px;">Innovation & Excellence</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 50px 40px;">
                <h2 style="color: #2d3748; margin-top: 0; font-weight: 400;">Bonjour [Prénom],</h2>
                <p style="color: #4a5568; line-height: 1.7; font-size: 16px;">
                    Votre profil au sein de <strong>[Entreprise]</strong> en tant que <strong>[Poste]</strong> 
                    a retenu notre attention. Nous pensons que notre solution <strong>[Produit]</strong> 
                    pourrait considérablement optimiser vos processus.
                </p>
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 25px; border-radius: 10px; margin: 30px 0; text-align: center;">
                    <h3 style="color: #ffffff; margin: 0 0 10px 0;">Offre Exclusive</h3>
                    <p style="color: #ffffff; margin: 0; font-size: 18px; font-weight: 500;">
                        Économisez [Montant] jusqu'au [Date] !
                    </p>
                </div>
                <table border="0" cellpadding="0" cellspacing="0" style="margin: 40px 0; text-align: center;">
                    <tr>
                        <td>
                            <a href="[Lien]" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 15px 35px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: 500; letter-spacing: 0.5px;">Profiter de l'offre</a>
                        </td>
                    </tr>
                </table>
                <p style="color: #718096; font-size: 14px; text-align: center;">
                    Besoin d'informations ? Contactez-nous au [Téléphone] ou à [Email]
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding: 30px; background: #f7fafc; text-align: center;">
                <p style="color: #718096; font-size: 14px; margin: 0;">
                    &copy; 2024 [Entreprise]. [Site web]<br>
                    <a href="#" style="color: #667eea; text-decoration: none;">Gérer mes préférences</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    def generate_newsletter_template(self, prompt: str, style_preference: str) -> str:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', sans-serif;">
    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: #ffffff;">
        <tr>
            <td style="padding: 25px 20px; background: #dc2626; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Newsletter [Entreprise]</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">[Date]</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 30px 25px;">
                <h2 style="color: #1f2937; margin: 0 0 15px 0;">Bonjour [Prénom] !</h2>
                <p style="color: #4b5563; line-height: 1.6; margin: 0 0 20px 0;">
                    Voici les dernières actualités de [Entreprise] spécialement pour vous.
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding: 0 25px 20px 25px;">
                <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background: #fef2f2; border-radius: 8px; overflow: hidden;">
                    <tr>
                        <td style="padding: 20px;">
                            <h3 style="color: #dc2626; margin: 0 0 10px 0;">Nouveau [Produit]</h3>
                            <p style="color: #7f1d1d; line-height: 1.5; margin: 0 0 15px 0;">
                                Découvrez notre nouvelle gamme [Produit] avec une promotion exclusive de [Promotion].
                            </p>
                            <a href="[Lien]" style="color: #dc2626; text-decoration: none; font-weight: bold;">En savoir plus →</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td style="padding: 0 25px 20px 25px;">
                <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background: #f0f9ff; border-radius: 8px; overflow: hidden;">
                    <tr>
                        <td style="padding: 20px;">
                            <h3 style="color: #0369a1; margin: 0 0 10px 0;">Événement à [Ville]</h3>
                            <p style="color: #0c4a6e; line-height: 1.5; margin: 0 0 15px 0;">
                                Rencontrez-nous à notre prochain événement le [Date] dans votre ville.
                            </p>
                            <a href="[Lien]" style="color: #0369a1; text-decoration: none; font-weight: bold;">S'inscrire →</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td style="padding: 0 25px 30px 25px; text-align: center;">
                <a href="[Lien]" style="background: #dc2626; color: #ffffff; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Voir toutes les actualités
                </a>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px; background: #f8fafc; text-align: center;">
                <p style="color: #6b7280; font-size: 12px; margin: 0 0 10px 0;">
                    [Entreprise] - [Site web] - [Téléphone]<br>
                    [Adresse], [Ville]
                </p>
                <p style="color: #9ca3af; font-size: 11px; margin: 0;">
                    <a href="#" style="color: #6b7280; text-decoration: none;">Se désabonner</a> | 
                    <a href="#" style="color: #6b7280; text-decoration: none;">Gérer les préférences</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>"""