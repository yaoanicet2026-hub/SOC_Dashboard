"""
Point d'entrée principal pour Streamlit Cloud
"""

import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
sys.path.insert(0, str(Path(__file__).parent))

# Importer et lancer l'application
from streamlit_app.main import main

if __name__ == "__main__":
    main()