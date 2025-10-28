"""
Tests unitaires pour DataLoader
"""

import pytest
import pandas as pd
import json
from pathlib import Path
import tempfile
import os
from datetime import datetime, timedelta

# Import du module à tester
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import DataLoader

class TestDataLoader:
    
    @pytest.fixture
    def temp_data_dir(self):
        """Crée un répertoire temporaire pour les tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_logs_csv(self, temp_data_dir):
        """Crée un fichier CSV de logs de test"""
        logs_data = [
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
        ]
        
        df = pd.DataFrame(logs_data)
        csv_path = temp_data_dir / "logs.csv"
        df.to_csv(csv_path, index=False)
        return csv_path
    
    @pytest.fixture
    def sample_vulns_json(self, temp_data_dir):
        """Crée un fichier JSON de vulnérabilités de test"""
        vulns_data = [
            {
                "cve_id": "CVE-2024-TEST1",
                "host": "host-01",
                "service": "OpenSSH",
                "cvss_score": 9.8,
                "severity": "critical",
                "status": "open",
                "description": "Test vulnerability",
                "discovered_date": "2025-01-10",
                "patch_available": True
            },
            {
                "cve_id": "CVE-2024-TEST2",
                "host": "host-02",
                "service": "Apache",
                "cvss_score": 5.5,
                "severity": "medium",
                "status": "patched",
                "description": "Another test vulnerability",
                "discovered_date": "2025-01-12",
                "patch_available": True
            }
        ]
        
        json_path = temp_data_dir / "vulns.json"
        with open(json_path, 'w') as f:
            json.dump(vulns_data, f)
        return json_path
    
    def test_load_logs_success(self, temp_data_dir, sample_logs_csv):
        """Test du chargement réussi des logs"""
        # Modifier le data_dir du DataLoader
        loader = DataLoader()
        loader.data_dir = temp_data_dir
        
        logs_df = loader.load_logs()
        
        assert not logs_df.empty
        assert len(logs_df) == 2
        assert 'timestamp' in logs_df.columns
        assert logs_df['timestamp'].dtype == 'datetime64[ns]'
        assert logs_df.iloc[0]['src_ip'] == '192.168.1.100'
    
    def test_load_logs_empty_file(self, temp_data_dir):
        """Test du chargement avec fichier inexistant"""
        loader = DataLoader()
        loader.data_dir = temp_data_dir
        
        logs_df = loader.load_logs()
        
        assert logs_df.empty
    
    def test_load_vulnerabilities_success(self, temp_data_dir, sample_vulns_json):
        """Test du chargement réussi des vulnérabilités"""
        loader = DataLoader()
        loader.data_dir = temp_data_dir
        
        vulns_df = loader.load_vulnerabilities()
        
        assert not vulns_df.empty
        assert len(vulns_df) == 2
        assert vulns_df.iloc[0]['cve_id'] == 'CVE-2024-TEST1'
        assert vulns_df.iloc[0]['cvss_score'] == 9.8
    
    def test_get_kpis_with_data(self, temp_data_dir, sample_logs_csv, sample_vulns_json):
        """Test du calcul des KPIs avec données"""
        loader = DataLoader()
        loader.data_dir = temp_data_dir
        
        kpis = loader.get_kpis()
        
        assert kpis['total_alerts'] == 2
        assert kpis['critical_alerts'] == 1
        assert kpis['low_alerts'] == 1
        assert kpis['critical_vulns'] == 1
        assert kpis['patch_rate'] == 50.0  # 1 sur 2 patchée
    
    def test_get_kpis_empty_data(self, temp_data_dir):
        """Test du calcul des KPIs sans données"""
        loader = DataLoader()
        loader.data_dir = temp_data_dir
        
        kpis = loader.get_kpis()
        
        assert kpis['total_alerts'] == 0
        assert kpis['critical_alerts'] == 0
        assert kpis['patch_rate'] == 0
    
    def test_get_recent_alerts(self, temp_data_dir, sample_logs_csv):
        """Test de récupération des alertes récentes"""
        loader = DataLoader()
        loader.data_dir = temp_data_dir
        
        # Les logs de test sont récents, donc devraient être inclus
        recent_alerts = loader.get_recent_alerts(hours=24)
        
        # Seule l'alerte critique devrait être retournée
        assert len(recent_alerts) == 1
        assert recent_alerts.iloc[0]['severity'] == 'critical'
    
    def test_get_network_stats(self, temp_data_dir, sample_logs_csv):
        """Test des statistiques réseau"""
        loader = DataLoader()
        loader.data_dir = temp_data_dir
        
        stats = loader.get_network_stats()
        
        assert 'top_src_ips' in stats
        assert 'top_dst_ips' in stats
        assert 'protocols' in stats
        assert stats['protocols']['TCP'] == 2
        assert stats['total_bytes_in'] == 2300  # 1500 + 800
        assert stats['total_bytes_out'] == 700   # 500 + 200
    
    def test_refresh_data(self, temp_data_dir, sample_logs_csv):
        """Test du rafraîchissement des données"""
        loader = DataLoader()
        loader.data_dir = temp_data_dir
        
        # Premier chargement
        logs1 = loader.load_logs()
        assert len(logs1) == 2
        
        # Modifier le fichier
        new_data = pd.DataFrame([{
            "timestamp": "2025-01-15 11:00:00",
            "src_ip": "192.168.1.200",
            "dst_ip": "10.0.0.2",
            "src_port": 11111,
            "dst_port": 443,
            "protocol": "TCP",
            "bytes_in": 2000,
            "bytes_out": 1000,
            "duration": 60,
            "event_type": "https_request",
            "severity": "low",
            "username": "user2",
            "host": "host-02"
        }])
        new_data.to_csv(temp_data_dir / "logs.csv", index=False)
        
        # Recharger avec refresh
        logs2 = loader.load_logs(refresh=True)
        assert len(logs2) == 1
        assert logs2.iloc[0]['src_ip'] == '192.168.1.200'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])