"""
Elasticsearch Client - Stub pour intégration ELK
"""

import json
import logging
from datetime import datetime, timedelta
import random

class ElasticsearchClient:
    def __init__(self, host="localhost", port=9200, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connected = False
        
        # Simuler connexion
        logging.info(f"Elasticsearch stub initialized for {host}:{port}")
    
    def connect(self):
        """Stub de connexion"""
        # TODO: Remplacer par vraie connexion Elasticsearch
        # from elasticsearch import Elasticsearch
        # self.es = Elasticsearch([{'host': self.host, 'port': self.port}])
        
        self.connected = True
        logging.info("Connected to Elasticsearch (STUB)")
        return True
    
    def search_logs(self, query="*", index="logs-*", size=100, time_range_hours=24):
        """Stub de recherche dans les logs"""
        
        # Simuler des résultats de recherche
        fake_results = []
        base_time = datetime.now() - timedelta(hours=time_range_hours)
        
        for i in range(min(size, 50)):  # Limiter pour la démo
            timestamp = base_time + timedelta(minutes=random.randint(0, time_range_hours*60))
            
            fake_log = {
                "_index": f"logs-{timestamp.strftime('%Y.%m.%d')}",
                "_id": f"fake_id_{i}",
                "_source": {
                    "@timestamp": timestamp.isoformat(),
                    "host": f"server-{random.randint(1,10)}",
                    "message": f"Sample log message {i}",
                    "level": random.choice(["INFO", "WARN", "ERROR"]),
                    "source_ip": f"192.168.1.{random.randint(1,254)}",
                    "user_agent": "Mozilla/5.0...",
                    "response_code": random.choice([200, 404, 500, 403])
                }
            }
            fake_results.append(fake_log)
        
        return {
            "hits": {
                "total": {"value": len(fake_results)},
                "hits": fake_results
            }
        }
    
    def get_security_alerts(self, severity="high", hours=24):
        """Récupère les alertes de sécurité"""
        
        # Simuler des alertes de sécurité
        alerts = []
        severities = ["low", "medium", "high", "critical"]
        
        for i in range(random.randint(5, 15)):
            alert = {
                "id": f"alert_{i}",
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(0, hours*60))).isoformat(),
                "severity": random.choice(severities),
                "rule_name": random.choice([
                    "SSH Brute Force",
                    "Port Scan Detected", 
                    "Malware Communication",
                    "Suspicious File Access",
                    "Failed Login Attempts"
                ]),
                "source_ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "destination_ip": f"192.168.1.{random.randint(1,254)}",
                "description": f"Security alert {i} detected"
            }
            alerts.append(alert)
        
        return alerts
    
    def create_index(self, index_name, mapping=None):
        """Stub de création d'index"""
        logging.info(f"Creating index {index_name} (STUB)")
        return {"acknowledged": True}
    
    def bulk_insert(self, documents, index_name):
        """Stub d'insertion en lot"""
        logging.info(f"Bulk inserting {len(documents)} documents to {index_name} (STUB)")
        return {"errors": False, "items": []}

# Exemple d'utilisation
def example_usage():
    """Exemple d'utilisation du client Elasticsearch"""
    
    # Initialisation
    client = ElasticsearchClient(
        host="localhost",
        port=9200,
        username="elastic",
        password="changeme"
    )
    
    # Connexion
    if client.connect():
        print("✅ Connecté à Elasticsearch")
        
        # Recherche de logs
        results = client.search_logs(
            query="error OR warning",
            index="logs-*",
            size=50,
            time_range_hours=24
        )
        
        print(f"📊 {results['hits']['total']['value']} logs trouvés")
        
        # Alertes de sécurité
        alerts = client.get_security_alerts(severity="high", hours=24)
        print(f"🚨 {len(alerts)} alertes de sécurité")
        
        return results, alerts
    
    return None, None

# Configuration pour remplacer le stub par une vraie connexion
REAL_ELASTICSEARCH_CONFIG = """
# Pour utiliser une vraie instance Elasticsearch:

1. Installer le client Python:
   pip install elasticsearch

2. Remplacer les stubs par:

from elasticsearch import Elasticsearch

class ElasticsearchClient:
    def __init__(self, host="localhost", port=9200, username=None, password=None):
        self.es = Elasticsearch(
            [{'host': host, 'port': port}],
            http_auth=(username, password) if username else None,
            use_ssl=True,
            verify_certs=False
        )
    
    def search_logs(self, query="*", index="logs-*", size=100):
        body = {
            "query": {
                "query_string": {
                    "query": query
                }
            },
            "size": size,
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        return self.es.search(index=index, body=body)

3. Exemples de requêtes:
   
   # Recherche par IP
   client.search_logs('source_ip:"192.168.1.100"')
   
   # Recherche par plage de temps
   client.search_logs('level:ERROR AND @timestamp:[now-1h TO now]')
   
   # Agrégations
   body = {
       "aggs": {
           "top_ips": {
               "terms": {"field": "source_ip.keyword", "size": 10}
           }
       }
   }
"""

if __name__ == "__main__":
    print("🔌 Test du client Elasticsearch (STUB)")
    results, alerts = example_usage()
    
    if results:
        print("\n📋 Exemples de logs:")
        for hit in results['hits']['hits'][:3]:
            print(f"  • {hit['_source']['@timestamp']} - {hit['_source']['message']}")
    
    if alerts:
        print(f"\n🚨 Exemples d'alertes:")
        for alert in alerts[:3]:
            print(f"  • {alert['severity'].upper()} - {alert['rule_name']}")
    
    print(f"\n📖 Configuration réelle:\n{REAL_ELASTICSEARCH_CONFIG}")