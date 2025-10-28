"""
Initialisation pour déploiement cloud
"""

import os
import streamlit as st
from pathlib import Path
import pandas as pd
import json

def init_cloud_environment():
    """Initialise l'environnement cloud"""
    
    # Créer les répertoires nécessaires
    base_dir = Path(__file__).parent.parent
    
    required_dirs = [
        base_dir / "data",
        base_dir / "models", 
        base_dir / "logs",
        base_dir / "exports"
    ]
    
    for dir_path in required_dirs:
        dir_path.mkdir(exist_ok=True)
    
    # Initialiser les données si elles n'existent pas
    init_sample_data()

def init_sample_data():
    """Initialise les données d'exemple pour le cloud"""
    
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    
    # Logs CSV minimal
    logs_file = data_dir / "logs.csv"
    if not logs_file.exists():
        sample_logs = pd.DataFrame([
            {
                "timestamp": "2025-01-15 10:00:00",
                "src_ip": "192.168.1.100",
                "dst_ip": "10.0.0.1",
                "src_port": 12345,
                "dst_port": 80,
                "protocol": "TCP",
                "bytes_in": 1500,
                "bytes_out": 500,
                "duration": 30,
                "event_type": "web_request",
                "severity": "low",
                "username": "user1",
                "host": "host-01"
            },
            {
                "timestamp": "2025-01-15 10:05:00",
                "src_ip": "45.89.22.4",
                "dst_ip": "192.168.1.100",
                "src_port": 54321,
                "dst_port": 22,
                "protocol": "TCP",
                "bytes_in": 800,
                "bytes_out": 200,
                "duration": 15,
                "event_type": "ssh_bruteforce",
                "severity": "critical",
                "username": "root",
                "host": "host-01"
            }
        ])
        sample_logs.to_csv(logs_file, index=False)
    
    # Vulnérabilités JSON minimal
    vulns_file = data_dir / "vulns.json"
    if not vulns_file.exists():
        sample_vulns = [
            {
                "cve_id": "CVE-2024-0001",
                "host": "host-01",
                "service": "OpenSSH",
                "cvss_score": 9.8,
                "severity": "critical",
                "status": "open",
                "description": "Remote code execution vulnerability",
                "discovered_date": "2025-01-10",
                "patch_available": True
            }
        ]
        with open(vulns_file, 'w') as f:
            json.dump(sample_vulns, f, indent=2)
    
    # Hôtes CSV minimal
    hosts_file = data_dir / "hosts.csv"
    if not hosts_file.exists():
        sample_hosts = pd.DataFrame([
            {
                "hostname": "host-01",
                "ip_address": "192.168.1.12",
                "os": "Ubuntu 20.04",
                "department": "IT",
                "criticality": "high",
                "last_seen": "2025-01-15 09:00:00",
                "status": "online"
            }
        ])
        sample_hosts.to_csv(hosts_file, index=False)

def get_cloud_config():
    """Récupère la configuration depuis les secrets Streamlit"""
    
    config = {}
    
    # Configuration depuis st.secrets si disponible
    if hasattr(st, 'secrets'):
        try:
            config.update({
                'admin_username': st.secrets.get('auth', {}).get('admin_username', 'admin'),
                'admin_password': st.secrets.get('auth', {}).get('admin_password', 'admin'),
                'elk_host': st.secrets.get('elk', {}).get('host', 'localhost'),
                'elk_port': st.secrets.get('elk', {}).get('port', 9200),
                'wazuh_host': st.secrets.get('wazuh', {}).get('host', 'localhost'),
                'wazuh_port': st.secrets.get('wazuh', {}).get('port', 55000)
            })
        except:
            pass
    
    # Configuration par défaut
    config.setdefault('admin_username', 'admin')
    config.setdefault('admin_password', 'admin')
    config.setdefault('elk_host', 'localhost')
    config.setdefault('elk_port', 9200)
    config.setdefault('wazuh_host', 'localhost')
    config.setdefault('wazuh_port', 55000)
    
    return config

# Initialiser automatiquement lors de l'import
if __name__ != "__main__":
    init_cloud_environment()