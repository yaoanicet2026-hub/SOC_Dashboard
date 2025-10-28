#!/bin/bash

echo "🔧 Installation SOC Dashboard..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 requis"
    exit 1
fi

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Créer fichiers de config
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Fichier .env créé - modifiez les paramètres"
fi

# Initialiser données
python seed_data.py

echo "✅ Installation terminée!"
echo "🚀 Lancer avec: streamlit run streamlit_app/main.py"