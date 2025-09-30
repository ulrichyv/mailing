import requests
import subprocess
import sys

def check_ollama():
    print("🔍 Diagnostic Ollama...")
    
    # Vérifier si Ollama est installé
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama est installé")
            print(f"   Version: {result.stdout.strip()}")
        else:
            print("❌ Ollama n'est pas installé ou pas dans le PATH")
            return False
    except FileNotFoundError:
        print("❌ Ollama n'est pas installé")
        return False
    
    # Vérifier si le serveur tourne
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur Ollama démarré")
            models = response.json().get("models", [])
            if models:
                print("📦 Modèles disponibles:")
                for model in models:
                    print(f"   - {model['name']}")
            else:
                print("⚠️  Aucun modèle téléchargé")
        else:
            print("❌ Serveur Ollama inaccessible")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Le serveur Ollama ne tourne pas")
        print("💡 Démarrez-le avec: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_ollama()