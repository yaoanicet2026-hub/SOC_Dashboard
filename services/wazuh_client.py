"""
Wazuh Client - Stub pour intégration Wazuh
"""

import json
import requests
import logging
from datetime import datetime, timedelta
import random

class WazuhClient:
    def __init__(self, host="localhost", port=55000, username="wazuh", password="wazuh"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.base_url = f"https://{host}:{port}"
        self.token = None
        
        logging.info(f"Wazuh client initialized for {host}:{port}")
    
    def authenticate(self):
        """Stub d'authentification"""
        # TODO: Remplacer par vraie authentification Wazuh
        # auth_url = f"{self.base_url}/security/user/authenticate"
        # response = requests.post(auth_url, auth=(self.username, self.password))
        
        self.token = "fake_jwt_token_stub"
        logging.info("Authenticated to Wazuh (STUB)")
        return True
    
    def get_alerts(self, limit=100, severity_min=5, hours=24):
        """Récupère les alertes Wazuh"""
        
        # Simuler des alertes Wazuh
        alerts = []
        rule_ids = [5710, 5712, 31100, 31101, 40111, 40112, 87101, 87102]
        
        for i in range(random.randint(10, limit)):
            timestamp = datetime.now() - timedelta(minutes=random.randint(0, hours*60))
            
            alert = {
                "id": f"wazuh_alert_{i}",
                "timestamp": timestamp.isoformat(),
                "rule": {
                    "id": random.choice(rule_ids),
                    "level": random.randint(severity_min, 15),
                    "description": random.choice([
                        "SSH authentication failure",
                        "Multiple authentication failures",
                        "Port scan detected",
                        "Web attack detected",
                        "Malware detected",
                        "File integrity monitoring alert"
                    ])
                },
                "agent": {
                    "id": f"00{random.randint(1,9)}",
                    "name": f"agent-{random.randint(1,20)}",
                    "ip": f"192.168.1.{random.randint(1,254)}"
                },
                "location": random.choice([
                    "/var/log/auth.log",
                    "/var/log/apache2/access.log", 
                    "/var/log/syslog",
                    "windows-security"
                ]),
                "full_log": f"Sample log entry {i} with security event"
            }
            alerts.append(alert)
        
        return alerts
    
    def get_agents(self):
        """Récupère la liste des agents"""
        
        agents = []
        for i in range(1, 21):  # 20 agents simulés
            agent = {
                "id": f"00{i}",
                "name": f"agent-{i}",
                "ip": f"192.168.1.{i+10}",
                "status": random.choice(["active", "disconnected", "never_connected"]),
                "os": {
                    "platform": random.choice(["ubuntu", "centos", "windows", "macos"]),
                    "version": random.choice(["20.04", "8", "Server 2019", "12.0"])
                },
                "version": "4.5.0",
                "last_keep_alive": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat()
            }
            agents.append(agent)
        
        return agents
    
    def get_rules(self, search=None):
        """Récupère les règles Wazuh"""
        
        rules = [
            {
                "id": 5710,
                "level": 5,
                "description": "SSH authentication failure",
                "groups": ["authentication_failure", "sshd"]
            },
            {
                "id": 5712,
                "level": 10,
                "description": "Multiple SSH authentication failures",
                "groups": ["authentication_failures", "sshd"]
            },
            {
                "id": 31100,
                "level": 6,
                "description": "Port scan detected",
                "groups": ["recon", "network_scan"]
            },
            {
                "id": 40111,
                "level": 12,
                "description": "Web attack detected",
                "groups": ["web", "attack"]
            }
        ]
        
        if search:
            rules = [r for r in rules if search.lower() in r['description'].lower()]
        
        return rules
    
    def get_sca_results(self, agent_id=None):
        """Récupère les résultats SCA (Security Configuration Assessment)"""
        
        policies = [
            {
                "name": "CIS Ubuntu 20.04",
                "pass": random.randint(80, 120),
                "fail": random.randint(5, 25),
                "invalid": random.randint(0, 5),
                "score": random.randint(75, 95)
            },
            {
                "name": "CIS Windows Server 2019",
                "pass": random.randint(90, 140),
                "fail": random.randint(10, 30),
                "invalid": random.randint(0, 8),
                "score": random.randint(70, 90)
            }
        ]
        
        return policies
    
    def get_vulnerability_data(self, agent_id=None):
        """Récupère les données de vulnérabilités"""
        
        vulns = []
        cve_list = ["CVE-2024-0001", "CVE-2024-0002", "CVE-2023-1234", "CVE-2023-5678"]
        
        for cve in cve_list:
            vuln = {
                "cve": cve,
                "cvss2_score": round(random.uniform(4.0, 10.0), 1),
                "cvss3_score": round(random.uniform(4.0, 10.0), 1),
                "severity": random.choice(["Low", "Medium", "High", "Critical"]),
                "package": random.choice(["openssl", "apache2", "mysql-server", "openssh-server"]),
                "version": "1.0.0",
                "architecture": "amd64",
                "condition": "Package unfixed"
            }
            vulns.append(vuln)
        
        return vulns

# Exemple d'utilisation
def example_usage():
    """Exemple d'utilisation du client Wazuh"""
    
    client = WazuhClient(
        host="localhost",
        port=55000,
        username="wazuh",
        password="wazuh"
    )
    
    if client.authenticate():
        print("✅ Authentifié sur Wazuh")
        
        # Récupérer les alertes
        alerts = client.get_alerts(limit=50, severity_min=5, hours=24)
        print(f"🚨 {len(alerts)} alertes récupérées")
        
        # Récupérer les agents
        agents = client.get_agents()
        active_agents = [a for a in agents if a['status'] == 'active']
        print(f"🖥️ {len(active_agents)}/{len(agents)} agents actifs")
        
        # Récupérer les règles
        rules = client.get_rules()
        print(f"📋 {len(rules)} règles disponibles")
        
        return alerts, agents, rules
    
    return None, None, None

# Configuration pour remplacer le stub par une vraie connexion
REAL_WAZUH_CONFIG = """
# Pour utiliser une vraie instance Wazuh:

1. Installer les dépendances:
   pip install requests urllib3

2. Remplacer les stubs par:

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WazuhClient:
    def authenticate(self):
        auth_url = f"{self.base_url}/security/user/authenticate"
        
        response = requests.post(
            auth_url,
            auth=(self.username, self.password),
            verify=False
        )
        
        if response.status_code == 200:
            self.token = response.json()['data']['token']
            return True
        return False
    
    def get_alerts(self, limit=100, severity_min=5):
        headers = {'Authorization': f'Bearer {self.token}'}
        
        params = {
            'limit': limit,
            'rule.level': f'>{severity_min}',
            'sort': '-timestamp'
        }
        
        response = requests.get(
            f"{self.base_url}/alerts",
            headers=headers,
            params=params,
            verify=False
        )
        
        return response.json()['data']['affected_items']

3. Exemples de requêtes API:

   # Alertes par agent
   GET /alerts?agent.id=001&limit=100
   
   # Alertes par règle
   GET /alerts?rule.id=5710&limit=50
   
   # Agents déconnectés
   GET /agents?status=disconnected
   
   # Résultats SCA
   GET /sca/001/checks/cis_ubuntu20-04

4. Configuration SSL:
   - Certificat: /var/ossec/api/configuration/ssl/server.crt
   - Clé privée: /var/ossec/api/configuration/ssl/server.key
"""

if __name__ == "__main__":
    print("🔌 Test du client Wazuh (STUB)")
    alerts, agents, rules = example_usage()
    
    if alerts:
        print("\n🚨 Exemples d'alertes:")
        for alert in alerts[:3]:
            print(f"  • Niveau {alert['rule']['level']} - {alert['rule']['description']}")
    
    if agents:
        print(f"\n🖥️ Exemples d'agents:")
        for agent in agents[:3]:
            print(f"  • {agent['name']} ({agent['ip']}) - {agent['status']}")
    
    print(f"\n📖 Configuration réelle:\n{REAL_WAZUH_CONFIG}")