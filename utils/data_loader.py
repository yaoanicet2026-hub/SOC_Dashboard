"""
Data Loader - Chargement et normalisation des données
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)

class DataLoader:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.logs_df = None
        self.vulns_df = None
        self.hosts_df = None
        
    def load_logs(self, refresh=False):
        """Charge les logs depuis CSV"""
        if self.logs_df is None or refresh:
            logs_path = self.data_dir / "logs.csv"
            try:
                if logs_path.exists():
                    self.logs_df = pd.read_csv(logs_path)
                    self.logs_df['timestamp'] = pd.to_datetime(self.logs_df['timestamp'])
                else:
                    # Créer des données par défaut si le fichier n'existe pas
                    self.logs_df = self._create_default_logs()
            except Exception as e:
                logging.error(f"Erreur chargement logs: {e}")
                self.logs_df = self._create_default_logs()
        return self.logs_df
    
    def load_vulnerabilities(self, refresh=False):
        """Charge les vulnérabilités depuis JSON"""
        if self.vulns_df is None or refresh:
            vulns_path = self.data_dir / "vulns.json"
            try:
                if vulns_path.exists():
                    with open(vulns_path) as f:
                        vulns_data = json.load(f)
                    self.vulns_df = pd.DataFrame(vulns_data)
                else:
                    self.vulns_df = self._create_default_vulns()
            except Exception as e:
                logging.error(f"Erreur chargement vulns: {e}")
                self.vulns_df = self._create_default_vulns()
        return self.vulns_df
    
    def load_hosts(self, refresh=False):
        """Charge les informations des hôtes"""
        if self.hosts_df is None or refresh:
            hosts_path = self.data_dir / "hosts.csv"
            if hosts_path.exists():
                self.hosts_df = pd.read_csv(hosts_path)
            else:
                self.hosts_df = pd.DataFrame()
        return self.hosts_df
    
    def get_recent_alerts(self, hours=24):
        """Récupère les alertes récentes"""
        logs = self.load_logs()
        if logs.empty:
            return pd.DataFrame()
        
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = logs[logs['timestamp'] >= cutoff]
        return recent[recent['severity'].isin(['critical', 'high'])]
    
    def get_kpis(self):
        """Calcule les KPIs principaux"""
        logs = self.load_logs()
        vulns = self.load_vulnerabilities()
        
        if logs.empty:
            return {
                'total_alerts': 0,
                'critical_alerts': 0,
                'high_alerts': 0,
                'medium_alerts': 0,
                'low_alerts': 0,
                'mttd': 0,
                'mttr': 0,
                'critical_vulns': 0,
                'patch_rate': 0
            }
        
        # Alertes par sévérité
        severity_counts = logs['severity'].value_counts()
        
        # Vulnérabilités critiques
        critical_vulns = 0
        patch_rate = 0
        if not vulns.empty:
            critical_vulns = len(vulns[vulns['cvss_score'] >= 9.0])
            patched = len(vulns[vulns['status'] == 'patched'])
            patch_rate = (patched / len(vulns)) * 100 if len(vulns) > 0 else 0
        
        return {
            'total_alerts': len(logs),
            'critical_alerts': severity_counts.get('critical', 0),
            'high_alerts': severity_counts.get('high', 0),
            'medium_alerts': severity_counts.get('medium', 0),
            'low_alerts': severity_counts.get('low', 0),
            'mttd': np.random.randint(5, 30),  # Simulé
            'mttr': np.random.randint(60, 240),  # Simulé
            'critical_vulns': critical_vulns,
            'patch_rate': round(patch_rate, 1)
        }
    
    def get_network_stats(self):
        """Statistiques réseau"""
        logs = self.load_logs()
        if logs.empty:
            return {}
        
        # Top IPs
        top_src_ips = logs['src_ip'].value_counts().head(10)
        top_dst_ips = logs['dst_ip'].value_counts().head(10)
        
        # Protocoles
        protocol_stats = logs['protocol'].value_counts()
        
        # Volume de données
        total_bytes_in = logs['bytes_in'].sum()
        total_bytes_out = logs['bytes_out'].sum()
        
        return {
            'top_src_ips': top_src_ips.to_dict(),
            'top_dst_ips': top_dst_ips.to_dict(),
            'protocols': protocol_stats.to_dict(),
            'total_bytes_in': total_bytes_in,
            'total_bytes_out': total_bytes_out
        }
    
    def _create_default_logs(self):
        """Crée des logs par défaut si aucun fichier n'existe"""
        default_data = [
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                "timestamp": (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
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
        ]
        df = pd.DataFrame(default_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def _create_default_vulns(self):
        """Crée des vulnérabilités par défaut"""
        return pd.DataFrame([
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
        ])