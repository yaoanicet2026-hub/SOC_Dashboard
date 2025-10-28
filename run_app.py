#!/usr/bin/env python3
"""
Script de lancement simplifié pour SOC Dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Changer vers le répertoire du projet
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("Lancement du SOC Dashboard...")
    print("URL: http://localhost:8501")
    print("Identifiants: admin / admin")
    print("-" * 50)
    
    try:
        # Lancer Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app/main.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\nArret de l'application")
    except Exception as e:
        print(f"Erreur: {e}")
        print("Essayez: pip install streamlit plotly pandas numpy scikit-learn")

if __name__ == "__main__":
    main()