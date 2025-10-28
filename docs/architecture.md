# Architecture SOC Dashboard

## Vue d'ensemble

Le SOC Dashboard est une application modulaire construite avec Streamlit pour l'interface utilisateur, intégrant des capacités de machine learning pour la détection d'anomalies et des connecteurs pour les outils de sécurité populaires.

## Architecture Technique

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Streamlit                      │
├─────────────────────────────────────────────────────────────┤
│  Dashboard  │  Threats  │  Network  │  Vulns  │  Incidents  │
├─────────────────────────────────────────────────────────────┤
│                    Couche Utilitaires                       │
├─────────────────────────────────────────────────────────────┤
│ DataLoader │ AIDetector │ AlertManager │ Exporters          │
├─────────────────────────────────────────────────────────────┤
│                    Couche Services                          │
├─────────────────────────────────────────────────────────────┤
│ ElasticClient │ WazuhClient │ SuricataParser                │
├─────────────────────────────────────────────────────────────┤
│                    Couche Données                           │
├─────────────────────────────────────────────────────────────┤
│    CSV/JSON    │    Models ML    │    Configuration         │
└─────────────────────────────────────────────────────────────┘
```

## Composants Principaux

### 1. Interface Utilisateur (streamlit_app/)

#### main.py
- Point d'entrée principal
- Gestion de la navigation
- Initialisation des composants
- Gestion du state Streamlit

#### Pages
- **dashboard.py**: Vue d'ensemble avec KPIs et métriques
- **threats.py**: Détection ML et gestion des menaces
- **network.py**: Analyse du trafic réseau
- **vulns.py**: Gestion des vulnérabilités CVE
- **incidents.py**: Système de ticketing

#### Composants
- **log_viewer.py**: Visualiseur de logs avec recherche
- **kpi_card.py**: Cartes de métriques réutilisables
- **ticket_manager.py**: Gestionnaire de tickets

### 2. Couche Utilitaires (utils/)

#### DataLoader
```python
class DataLoader:
    - load_logs()           # Chargement CSV/JSON
    - load_vulnerabilities() # Import CVE
    - get_kpis()            # Calcul métriques
    - get_network_stats()   # Statistiques réseau
```

#### AIDetector
```python
class AIDetector:
    - train_model()         # Entraînement IsolationForest
    - predict_anomalies()   # Détection temps réel
    - save_model()          # Persistance modèle
    - load_model()          # Chargement modèle
```

#### AlertManager
```python
class AlertManager:
    - check_alerts()        # Vérification règles
    - send_notification()   # Notifications (email/telegram)
    - get_alert_history()   # Historique alertes
```

### 3. Couche Services (services/)

#### Connecteurs Externes
- **elastic_client.py**: Interface Elasticsearch
- **wazuh_client.py**: Interface Wazuh Manager
- **suricata_parser.py**: Parser logs Suricata

Tous les connecteurs incluent:
- Stubs pour développement local
- Exemples de configuration réelle
- Documentation d'intégration

### 4. Couche Données

#### Formats Supportés
- **CSV**: Logs, hôtes, métriques
- **JSON**: Vulnérabilités, configuration, tickets
- **PKL**: Modèles ML entraînés

#### Structure des Données

**Logs (logs.csv)**
```csv
timestamp,src_ip,dst_ip,src_port,dst_port,protocol,bytes_in,bytes_out,duration,event_type,severity,username,host
```

**Vulnérabilités (vulns.json)**
```json
{
  "cve_id": "CVE-2024-0001",
  "host": "host-01",
  "cvss_score": 9.8,
  "severity": "critical",
  "status": "open"
}
```

## Flux de Données

### 1. Ingestion
```
Sources → Services → DataLoader → Cache Streamlit
```

### 2. Traitement ML
```
Logs → Feature Engineering → IsolationForest → Scores de Risque
```

### 3. Alerting
```
Données → Règles → AlertManager → Notifications
```

### 4. Visualisation
```
Données → Plotly → Streamlit → Interface Web
```

## Sécurité

### Authentification
- Authentification basique intégrée
- Support pour OAuth/SSO (configuration)
- Gestion des sessions Streamlit

### Protection des Données
- Variables d'environnement pour secrets
- Chiffrement des mots de passe (bcrypt)
- Validation des entrées utilisateur

### Audit
- Logs d'activité utilisateur
- Traçabilité des actions
- Historique des modifications

## Performance

### Optimisations
- Cache Streamlit pour les données
- Pagination des résultats
- Chargement lazy des modèles ML

### Scalabilité
- Architecture modulaire
- Séparation des préoccupations
- Support pour clustering (futur)

## Monitoring

### Métriques Applicatives
- Temps de réponse des pages
- Utilisation mémoire des modèles ML
- Taux d'erreur des connecteurs

### Métriques Métier
- MTTD (Mean Time To Detect)
- MTTR (Mean Time To Resolve)
- Taux de faux positifs ML

## Déploiement

### Environnements
- **Développement**: Données simulées, stubs
- **Test**: Intégration partielle, données test
- **Production**: Connecteurs réels, monitoring

### Configuration
```bash
# Variables d'environnement
ELK_HOST=elasticsearch.local
WAZUH_HOST=wazuh.local
SMTP_HOST=mail.company.com

# Lancement
streamlit run streamlit_app/main.py --server.port 8501
```

## Extensions Futures

### Connecteurs Additionnels
- Splunk
- QRadar
- Sentinel
- CrowdStrike

### Fonctionnalités Avancées
- Corrélation d'événements
- Threat Intelligence
- Automated Response
- Reporting avancé

### Intégrations
- SOAR Platforms
- Ticketing Systems (Jira, ServiceNow)
- Communication (Slack, Teams)

## Maintenance

### Mise à Jour des Modèles
- Réentraînement automatique (cron)
- Validation des performances
- Rollback en cas de dégradation

### Sauvegarde
- Export régulier des données
- Sauvegarde des modèles ML
- Configuration versionnée

### Monitoring Santé
- Health checks des services
- Alertes système
- Métriques de performance