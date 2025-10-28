# SOC Dashboard

**Auteur**: Yao Kouakou Luc Anicet Béranger  
**Licence**: MIT  
**Version**: 1.0.0

## Description

Tableau de bord SOC (Security Operations Center) complet avec détection d'anomalies ML, visualisations interactives et intégrations pour ELK/Wazuh/Suricata.

## Installation Rapide

```bash
# Cloner et installer
cd SOC_Dashboard
bash setup.sh

# Lancer l'application
streamlit run streamlit_app/main.py
```

## Fonctionnalités

- **Dashboard Principal**: KPIs temps réel, alertes par minute, heatmap
- **Détection ML**: IsolationForest pour anomalies réseau
- **Gestion Incidents**: Système de tickets avec MTTD/MTTR
- **Vulnérabilités**: Import CVE, scoring CVSS
- **Analyse Réseau**: Flux IP, protocoles, graphiques interactifs
- **Logs Viewer**: Recherche full-text, pagination
- **Alerting**: Règles automatiques, notifications
- **Export**: CSV/PDF des rapports

## Architecture

```
streamlit_app/     # Interface utilisateur Streamlit
utils/            # Utilitaires (data, ML, alertes)
services/         # Connecteurs ELK/Wazuh (stubs)
data/            # Datasets simulés
models/          # Modèles ML entraînés
assets/          # CSS, logos
tests/           # Tests unitaires
```

## Configuration

1. Copier `.env.example` vers `.env`
2. Modifier les paramètres de connexion
3. Lancer `python seed_data.py` pour initialiser

## Tests

```bash
pytest -v
```

## Intégrations Réelles

Voir `docs/how_to_connect_elk.md` pour remplacer les stubs par de vraies connexions.

## Développement

- Python 3.10+
- Streamlit + Plotly
- scikit-learn pour ML
- Mode sombre par défaut