# Guide de Déploiement SOC Dashboard

## 🚀 Déploiement Streamlit Community Cloud

### Étape 1: Préparer le dépôt GitHub
```bash
# Créer le dépôt sur github.com avec le nom: SOC_Dashboard
# Puis connecter votre code local:

git remote add origin https://github.com/VOTRE_USERNAME/SOC_Dashboard.git
git branch -M main
git push -u origin main
```

### Étape 2: Déployer sur Streamlit Cloud
1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Connectez-vous avec GitHub
3. Cliquez "New app"
4. Configurez:
   - Repository: `VOTRE_USERNAME/SOC_Dashboard`
   - Branch: `main`
   - Main file path: `streamlit_app/main.py`
5. Cliquez "Deploy!"

### Étape 3: Configuration des secrets (optionnel)
Dans l'interface Streamlit Cloud, ajoutez les secrets:
```toml
[auth]
admin_username = "admin"
admin_password = "votre_mot_de_passe_securise"

[notifications]
smtp_host = "smtp.gmail.com"
smtp_username = "votre_email@gmail.com"
smtp_password = "votre_mot_de_passe_app"
```

## 🐳 Déploiement Docker Local

### Option 1: Application seule
```bash
docker build -t soc-dashboard .
docker run -p 8501:8501 soc-dashboard
```

### Option 2: Stack complète avec ELK
```bash
docker-compose up -d
```

Accès:
- SOC Dashboard: http://localhost:8501
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601

## 🔧 Déploiement Production

### Prérequis
- Python 3.10+
- 2GB RAM minimum
- 10GB espace disque

### Installation
```bash
git clone https://github.com/VOTRE_USERNAME/SOC_Dashboard.git
cd SOC_Dashboard
python deploy.py local --env production
```

### Configuration SSL (production)
```bash
streamlit run streamlit_app/main.py \
  --server.port=443 \
  --server.sslCertFile=/path/to/cert.pem \
  --server.sslKeyFile=/path/to/key.pem
```

## 🔐 Identifiants par défaut
- **Username:** admin
- **Password:** admin

⚠️ **Important:** Changez ces identifiants en production !

## 📊 Fonctionnalités disponibles après déploiement
- ✅ Dashboard temps réel
- ✅ Détection ML d'anomalies
- ✅ Gestion des incidents
- ✅ Analyse des vulnérabilités
- ✅ Visualiseur de logs
- ✅ Administration système

## 🆘 Dépannage

### Erreur de dépendances
```bash
pip install -r requirements.txt
```

### Erreur de données manquantes
```bash
python seed_data.py
```

### Erreur de permissions
```bash
chmod +x setup.sh
./setup.sh
```