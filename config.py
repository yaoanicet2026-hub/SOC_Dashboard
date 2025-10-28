"""
Configuration centralisée pour SOC Dashboard
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    # Chemins
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
    LOGS_DIR = BASE_DIR / "logs"
    EXPORTS_DIR = BASE_DIR / "exports"
    
    # Application
    APP_NAME = "SOC Dashboard"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "Yao Kouakou Luc Anicet Béranger"
    
    # Streamlit
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))
    STREAMLIT_HOST = os.getenv("STREAMLIT_HOST", "localhost")
    
    # Authentification
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
    
    # Elasticsearch
    ELK_HOST = os.getenv("ELK_HOST", "localhost")
    ELK_PORT = int(os.getenv("ELK_PORT", 9200))
    ELK_USERNAME = os.getenv("ELK_USERNAME", "elastic")
    ELK_PASSWORD = os.getenv("ELK_PASSWORD", "changeme")
    ELK_USE_SSL = os.getenv("ELK_USE_SSL", "false").lower() == "true"
    
    # Wazuh
    WAZUH_HOST = os.getenv("WAZUH_HOST", "localhost")
    WAZUH_PORT = int(os.getenv("WAZUH_PORT", 55000))
    WAZUH_USERNAME = os.getenv("WAZUH_USERNAME", "wazuh")
    WAZUH_PASSWORD = os.getenv("WAZUH_PASSWORD", "wazuh")
    
    # ML Configuration
    MODEL_RETRAIN_HOURS = int(os.getenv("MODEL_RETRAIN_HOURS", 24))
    ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", 0.1))
    
    # Alerting
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Seuils d'alerte
    ALERT_THRESHOLDS = {
        "ssh_bruteforce": 10,
        "port_scan": 5,
        "failed_login": 20,
        "high_volume_traffic": 1000000
    }
    
    # SLA (en heures)
    SLA_CRITICAL = 4
    SLA_HIGH = 24
    SLA_MEDIUM = 72
    SLA_LOW = 168
    
    @classmethod
    def create_directories(cls):
        """Crée les répertoires nécessaires"""
        for dir_path in [cls.DATA_DIR, cls.MODELS_DIR, cls.LOGS_DIR, cls.EXPORTS_DIR]:
            dir_path.mkdir(exist_ok=True)
    
    @classmethod
    def get_sla_hours(cls, severity):
        """Retourne les heures SLA pour une sévérité"""
        sla_map = {
            "critical": cls.SLA_CRITICAL,
            "high": cls.SLA_HIGH,
            "medium": cls.SLA_MEDIUM,
            "low": cls.SLA_LOW
        }
        return sla_map.get(severity.lower(), cls.SLA_MEDIUM)