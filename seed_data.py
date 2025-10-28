#!/usr/bin/env python3
"""
Script d'initialisation des données pour SOC Dashboard
Génère des données simulées et entraîne le modèle ML
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from pathlib import Path
import random

def generate_logs_data(num_records=500):
    """Génère des données de logs simulées"""
    
    # IPs sources (mix d'internes et externes)
    internal_ips = [f"192.168.1.{i}" for i in range(1, 50)]
    internal_ips.extend([f"10.0.0.{i}" for i in range(1, 30)])
    internal_ips.extend([f"172.16.0.{i}" for i in range(1, 20)])
    
    external_ips = [
        "45.89.22.4", "203.0.113.50", "198.51.100.75", "185.220.101.32",
        "91.189.89.199", "151.101.193.140", "104.16.249.249", "172.217.16.142"
    ]
    
    # Types d'événements avec probabilités
    event_types = [
        ("normal_traffic", 0.4),
        ("web_request", 0.2),
        ("dns_query", 0.15),
        ("ssh_login", 0.08),
        ("ssh_bruteforce", 0.05),
        ("port_scan", 0.04),
        ("web_attack", 0.03),
        ("failed_login", 0.03),
        ("malware_detected", 0.02)
    ]
    
    # Sévérités correspondantes
    severity_map = {
        "normal_traffic": "low",
        "web_request": "low", 
        "dns_query": "low",
        "ssh_login": "low",
        "ssh_bruteforce": "critical",
        "port_scan": "high",
        "web_attack": "critical",
        "failed_login": "medium",
        "malware_detected": "critical"
    }
    
    # Ports communs
    common_ports = [22, 80, 443, 53, 21, 25, 110, 143, 993, 995, 3389, 445, 139]
    
    # Hôtes
    hosts = [f"host-{i:02d}" for i in range(1, 21)]
    
    # Utilisateurs
    usernames = ["", "admin", "root", "user1", "user2", "sshuser", "ftpuser", "webuser"]
    
    logs = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(num_records):
        # Timestamp avec distribution réaliste (plus d'activité en journée)
        hour_offset = random.gauss(12, 4)  # Centré sur midi
        hour_offset = max(0, min(23, hour_offset))
        
        timestamp = base_time + timedelta(
            days=random.randint(0, 6),
            hours=int(hour_offset),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        # Sélectionner type d'événement selon probabilités
        event_type = np.random.choice(
            [e[0] for e in event_types],
            p=[e[1] for e in event_types]
        )
        
        # IP source (plus d'internes que d'externes)
        if random.random() < 0.7:
            src_ip = random.choice(internal_ips)
        else:
            src_ip = random.choice(external_ips)
        
        # IP destination (principalement internes)
        dst_ip = random.choice(internal_ips)
        
        # Ports
        if event_type == "ssh_bruteforce" or event_type == "ssh_login":
            dst_port = 22
        elif event_type == "web_request" or event_type == "web_attack":
            dst_port = random.choice([80, 443])
        elif event_type == "dns_query":
            dst_port = 53
        else:
            dst_port = random.choice(common_ports)
        
        src_port = random.randint(1024, 65535)
        
        # Protocole
        if dst_port == 53:
            protocol = "UDP"
        else:
            protocol = "TCP"
        
        # Volumes de données (corrélés au type d'événement)
        if event_type == "web_attack":
            bytes_in = random.randint(50000, 500000)
            bytes_out = random.randint(1000, 10000)
        elif event_type == "port_scan":
            bytes_in = random.randint(100, 1000)
            bytes_out = random.randint(50, 500)
        elif event_type == "normal_traffic":
            bytes_in = random.randint(1000, 50000)
            bytes_out = random.randint(500, 25000)
        else:
            bytes_in = random.randint(200, 5000)
            bytes_out = random.randint(100, 2500)
        
        # Durée
        if event_type == "port_scan":
            duration = random.randint(1, 5)
        elif event_type == "web_attack":
            duration = random.randint(30, 300)
        else:
            duration = random.randint(1, 120)
        
        # Utilisateur
        if event_type in ["ssh_login", "ssh_bruteforce", "failed_login"]:
            username = random.choice(["root", "admin", "user1", "user2", ""])
        else:
            username = random.choice(usernames)
        
        log_entry = {
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": protocol,
            "bytes_in": bytes_in,
            "bytes_out": bytes_out,
            "duration": duration,
            "event_type": event_type,
            "severity": severity_map[event_type],
            "username": username,
            "host": random.choice(hosts)
        }
        
        logs.append(log_entry)
    
    return pd.DataFrame(logs)

def generate_vulnerabilities():
    """Génère des données de vulnérabilités"""
    
    services = ["OpenSSH", "Apache", "Nginx", "MySQL", "PostgreSQL", "Windows RDP", "SMB", "FTP"]
    hosts = [f"host-{i:02d}" for i in range(1, 21)]
    statuses = ["open", "in_progress", "patched"]
    
    vulns = []
    
    for i in range(1, 26):  # 25 vulnérabilités
        cve_id = f"CVE-2024-{i:04d}"
        host = random.choice(hosts)
        service = random.choice(services)
        
        # Score CVSS avec distribution réaliste
        cvss_score = round(random.triangular(2.0, 10.0, 6.5), 1)
        
        if cvss_score >= 9.0:
            severity = "critical"
        elif cvss_score >= 7.0:
            severity = "high"
        elif cvss_score >= 4.0:
            severity = "medium"
        else:
            severity = "low"
        
        # Status avec probabilités réalistes
        status = np.random.choice(statuses, p=[0.4, 0.3, 0.3])
        
        # Date de découverte
        discovered_date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        
        descriptions = [
            "Remote code execution vulnerability",
            "SQL injection vulnerability", 
            "Cross-site scripting (XSS)",
            "Authentication bypass",
            "Information disclosure vulnerability",
            "Buffer overflow vulnerability",
            "Directory traversal",
            "Privilege escalation",
            "Denial of service vulnerability",
            "Insecure deserialization"
        ]
        
        vuln = {
            "cve_id": cve_id,
            "host": host,
            "service": service,
            "cvss_score": cvss_score,
            "severity": severity,
            "status": status,
            "description": random.choice(descriptions),
            "discovered_date": discovered_date,
            "patch_available": random.choice([True, False])
        }
        
        vulns.append(vuln)
    
    return vulns

def generate_hosts():
    """Génère des informations sur les hôtes"""
    
    operating_systems = [
        "Ubuntu 20.04", "Ubuntu 18.04", "CentOS 8", "RHEL 8", "Debian 11",
        "Windows Server 2019", "Windows Server 2016", "Windows 10", "Windows 11",
        "macOS 12", "macOS 13"
    ]
    
    departments = ["IT", "Finance", "HR", "Operations", "Development", "Marketing", "Executive"]
    criticalities = ["low", "medium", "high", "critical"]
    statuses = ["online", "offline", "maintenance"]
    
    hosts = []
    
    for i in range(1, 21):  # 20 hôtes
        hostname = f"host-{i:02d}"
        
        # IP dans différents sous-réseaux
        if i <= 10:
            ip_address = f"192.168.1.{i+10}"
        elif i <= 15:
            ip_address = f"10.0.0.{i-5}"
        else:
            ip_address = f"172.16.0.{i-10}"
        
        host = {
            "hostname": hostname,
            "ip_address": ip_address,
            "os": random.choice(operating_systems),
            "department": random.choice(departments),
            "criticality": np.random.choice(criticalities, p=[0.3, 0.4, 0.2, 0.1]),
            "last_seen": (datetime.now() - timedelta(minutes=random.randint(0, 120))).strftime("%Y-%m-%d %H:%M:%S"),
            "status": np.random.choice(statuses, p=[0.8, 0.1, 0.1])
        }
        
        hosts.append(host)
    
    return pd.DataFrame(hosts)

def main():
    """Fonction principale d'initialisation"""
    
    print("Initialisation des donnees SOC Dashboard...")
    
    # Créer les répertoires
    data_dir = Path("data")
    models_dir = Path("models")
    logs_dir = Path("logs")
    
    data_dir.mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    # Générer et sauvegarder les logs
    print("Generation des logs...")
    logs_df = generate_logs_data(500)
    logs_df.to_csv(data_dir / "logs.csv", index=False)
    print(f"OK - {len(logs_df)} logs generes")
    
    # Générer et sauvegarder les vulnérabilités
    print("Generation des vulnerabilites...")
    vulns = generate_vulnerabilities()
    with open(data_dir / "vulns.json", 'w') as f:
        json.dump(vulns, f, indent=2)
    print(f"OK - {len(vulns)} vulnerabilites generees")
    
    # Générer et sauvegarder les hôtes
    print("Generation des informations hotes...")
    hosts_df = generate_hosts()
    hosts_df.to_csv(data_dir / "hosts.csv", index=False)
    print(f"OK - {len(hosts_df)} hotes generes")
    
    # Entraîner le modèle ML
    print("Entrainement du modele ML...")
    try:
        from utils.ai_detector import AIDetector
        
        ai_detector = AIDetector()
        result = ai_detector.train_model(logs_df)
        
        if result['success']:
            print(f"OK - Modele entraine sur {result['samples_trained']} echantillons")
            print(f"Anomalies detectees: {result['anomalies_detected']} ({result['anomaly_rate']:.1f}%)")
        else:
            print(f"ERREUR entrainement: {result['error']}")
    
    except ImportError:
        print("ATTENTION - Impossible d'importer AIDetector - entrainement manuel requis")
    
    # Créer fichiers de logs vides
    (logs_dir / "alerts_sent.log").touch()
    
    print("\nInitialisation terminee!")
    print("Lancer l'application avec: streamlit run streamlit_app/main.py")

if __name__ == "__main__":
    main()