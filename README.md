# 📧 Mailing App - Neurafrik

Application **Streamlit** pour gérer et envoyer des campagnes emails personnalisées.  
Elle permet de configurer un serveur SMTP, créer des templates (HTML ou texte), importer un CSV de destinataires et suivre l’envoi en temps réel avec logs détaillés.

---

## 🚀 Installation et lancement

### 1. Cloner le projet

```bash
git clone https://github.com/ulrichyv/mailing.git
cd mailing
```

### 2. Créer et activer un environnement virtuel

#### Linux / Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
streamlit run app.py
```
