# Guide d'Intégration Elasticsearch/ELK Stack

## Vue d'ensemble

Ce guide explique comment remplacer les stubs par de vraies connexions à Elasticsearch et intégrer le SOC Dashboard avec votre stack ELK existante.

## Prérequis

- Elasticsearch 7.x ou 8.x
- Kibana (optionnel, pour visualisation)
- Logstash ou Beats pour l'ingestion
- Accès réseau au cluster Elasticsearch
- Credentials d'authentification

## Configuration Elasticsearch

### 1. Installation du Client Python

```bash
pip install elasticsearch>=8.0.0
```

### 2. Configuration des Variables d'Environnement

Modifier le fichier `.env`:

```bash
# Elasticsearch Configuration
ELK_HOST=your-elasticsearch-host.com
ELK_PORT=9200
ELK_USERNAME=elastic
ELK_PASSWORD=your-secure-password
ELK_USE_SSL=true
ELK_VERIFY_CERTS=false
ELK_CA_CERTS=/path/to/ca.crt

# Index Configuration
ELK_LOGS_INDEX=logs-*
ELK_ALERTS_INDEX=alerts-*
ELK_METRICS_INDEX=metrics-*
```

### 3. Remplacement du Stub

Modifier `services/elastic_client.py`:

```python
from elasticsearch import Elasticsearch
import ssl
import urllib3

class ElasticsearchClient:
    def __init__(self, host, port=9200, username=None, password=None, use_ssl=True):
        self.host = host
        self.port = port
        
        # Configuration SSL
        if use_ssl:
            context = ssl.create_default_context()
            if not verify_certs:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Initialisation du client
        self.es = Elasticsearch(
            [{'host': host, 'port': port, 'use_ssl': use_ssl}],
            http_auth=(username, password) if username else None,
            ssl_context=context if use_ssl else None,
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
    
    def connect(self):
        """Test de connexion"""
        try:
            info = self.es.info()
            logging.info(f"Connected to Elasticsearch: {info['version']['number']}")
            return True
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            return False
    
    def search_logs(self, query="*", index="logs-*", size=100, time_range_hours=24):
        """Recherche dans les logs"""
        
        # Construction de la requête temporelle
        time_filter = {
            "range": {
                "@timestamp": {
                    "gte": f"now-{time_range_hours}h",
                    "lte": "now"
                }
            }
        }
        
        # Construction de la requête complète
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": query}},
                        time_filter
                    ]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": size
        }
        
        try:
            response = self.es.search(index=index, body=body)
            return response
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return {"hits": {"total": {"value": 0}, "hits": []}}
```

## Mapping des Index

### 1. Template pour les Logs de Sécurité

```json
PUT _index_template/security-logs
{
  "index_patterns": ["security-logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1,
      "index.refresh_interval": "5s"
    },
    "mappings": {
      "properties": {
        "@timestamp": {"type": "date"},
        "source_ip": {"type": "ip"},
        "destination_ip": {"type": "ip"},
        "source_port": {"type": "integer"},
        "destination_port": {"type": "integer"},
        "protocol": {"type": "keyword"},
        "event_type": {"type": "keyword"},
        "severity": {"type": "keyword"},
        "bytes_in": {"type": "long"},
        "bytes_out": {"type": "long"},
        "duration": {"type": "integer"},
        "username": {"type": "keyword"},
        "host": {"type": "keyword"},
        "message": {"type": "text"},
        "tags": {"type": "keyword"}
      }
    }
  }
}
```

### 2. Template pour les Alertes

```json
PUT _index_template/security-alerts
{
  "index_patterns": ["security-alerts-*"],
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": {"type": "date"},
        "alert_id": {"type": "keyword"},
        "rule_name": {"type": "keyword"},
        "severity": {"type": "keyword"},
        "source_ip": {"type": "ip"},
        "destination_ip": {"type": "ip"},
        "description": {"type": "text"},
        "risk_score": {"type": "float"},
        "status": {"type": "keyword"},
        "assignee": {"type": "keyword"}
      }
    }
  }
}
```

## Requêtes Utiles

### 1. Recherche d'Événements de Sécurité

```python
# Recherche par IP source
def search_by_source_ip(self, ip_address, hours=24):
    query = f'source_ip:"{ip_address}"'
    return self.search_logs(query, time_range_hours=hours)

# Recherche par type d'événement
def search_by_event_type(self, event_type, hours=24):
    query = f'event_type:"{event_type}"'
    return self.search_logs(query, time_range_hours=hours)

# Recherche d'anomalies
def search_anomalies(self, risk_threshold=70, hours=24):
    body = {
        "query": {
            "bool": {
                "must": [
                    {"range": {"risk_score": {"gte": risk_threshold}}},
                    {"range": {"@timestamp": {"gte": f"now-{hours}h"}}}
                ]
            }
        },
        "sort": [{"risk_score": {"order": "desc"}}]
    }
    return self.es.search(index="security-alerts-*", body=body)
```

### 2. Agrégations pour Statistiques

```python
def get_top_source_ips(self, hours=24, size=10):
    """Top IPs sources par volume"""
    body = {
        "query": {
            "range": {"@timestamp": {"gte": f"now-{hours}h"}}
        },
        "aggs": {
            "top_ips": {
                "terms": {
                    "field": "source_ip",
                    "size": size,
                    "order": {"total_bytes": "desc"}
                },
                "aggs": {
                    "total_bytes": {"sum": {"field": "bytes_in"}}
                }
            }
        },
        "size": 0
    }
    return self.es.search(index="security-logs-*", body=body)

def get_events_timeline(self, hours=24, interval="1h"):
    """Timeline des événements"""
    body = {
        "query": {
            "range": {"@timestamp": {"gte": f"now-{hours}h"}}
        },
        "aggs": {
            "events_over_time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "fixed_interval": interval
                },
                "aggs": {
                    "by_severity": {
                        "terms": {"field": "severity"}
                    }
                }
            }
        },
        "size": 0
    }
    return self.es.search(index="security-logs-*", body=body)
```

## Intégration avec Logstash

### 1. Configuration Logstash pour SOC Dashboard

```ruby
# /etc/logstash/conf.d/soc-dashboard.conf
input {
  beats {
    port => 5044
  }
  
  tcp {
    port => 5000
    codec => json
  }
}

filter {
  # Parsing des logs de sécurité
  if [fields][log_type] == "security" {
    grok {
      match => { 
        "message" => "%{TIMESTAMP_ISO8601:timestamp} %{IP:source_ip} %{IP:destination_ip} %{WORD:event_type}" 
      }
    }
    
    # Enrichissement géographique
    geoip {
      source => "source_ip"
      target => "source_geo"
    }
    
    # Classification de sévérité
    if [event_type] in ["ssh_bruteforce", "malware_detected"] {
      mutate { add_field => { "severity" => "critical" } }
    } else if [event_type] in ["port_scan", "failed_login"] {
      mutate { add_field => { "severity" => "high" } }
    } else {
      mutate { add_field => { "severity" => "medium" } }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "security-logs-%{+YYYY.MM.dd}"
    template_name => "security-logs"
  }
  
  # Debug
  stdout { codec => rubydebug }
}
```

### 2. Envoi de Données vers Elasticsearch

```python
def send_alert_to_elasticsearch(self, alert_data):
    """Envoie une alerte vers Elasticsearch"""
    
    # Enrichissement de l'alerte
    enriched_alert = {
        "@timestamp": datetime.now().isoformat(),
        "alert_id": alert_data.get("id"),
        "rule_name": alert_data.get("rule_name"),
        "severity": alert_data.get("severity"),
        "source_ip": alert_data.get("source_ip"),
        "destination_ip": alert_data.get("destination_ip"),
        "description": alert_data.get("message"),
        "risk_score": alert_data.get("risk_score", 0),
        "status": "open",
        "created_by": "soc_dashboard"
    }
    
    # Index avec rotation quotidienne
    index_name = f"security-alerts-{datetime.now().strftime('%Y.%m.%d')}"
    
    try:
        response = self.es.index(
            index=index_name,
            body=enriched_alert
        )
        logging.info(f"Alert sent to Elasticsearch: {response['_id']}")
        return response
    except Exception as e:
        logging.error(f"Failed to send alert: {e}")
        return None
```

## Configuration Kibana

### 1. Index Patterns

Créer les index patterns dans Kibana:
- `security-logs-*` avec timestamp field `@timestamp`
- `security-alerts-*` avec timestamp field `@timestamp`

### 2. Dashboards Recommandés

```json
{
  "version": "8.0.0",
  "objects": [
    {
      "id": "soc-overview",
      "type": "dashboard",
      "attributes": {
        "title": "SOC Overview",
        "panelsJSON": "[{\"version\":\"8.0.0\",\"gridData\":{\"x\":0,\"y\":0,\"w\":24,\"h\":15},\"panelIndex\":\"1\",\"embeddableConfig\":{},\"panelRefName\":\"panel_1\"}]"
      }
    }
  ]
}
```

## Monitoring et Alerting

### 1. Watcher pour Alertes Automatiques

```json
PUT _watcher/watch/high_risk_events
{
  "trigger": {
    "schedule": {"interval": "1m"}
  },
  "input": {
    "search": {
      "request": {
        "search_type": "query_then_fetch",
        "indices": ["security-logs-*"],
        "body": {
          "query": {
            "bool": {
              "must": [
                {"range": {"@timestamp": {"gte": "now-5m"}}},
                {"terms": {"severity": ["critical", "high"]}}
              ]
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {"ctx.payload.hits.total": {"gt": 10}}
  },
  "actions": {
    "send_email": {
      "email": {
        "to": ["soc@company.com"],
        "subject": "High Risk Security Events Detected",
        "body": "{{ctx.payload.hits.total}} high risk events detected in the last 5 minutes."
      }
    }
  }
}
```

## Dépannage

### Problèmes Courants

1. **Connexion SSL**
   ```python
   # Désactiver la vérification SSL pour les tests
   urllib3.disable_warnings()
   context = ssl.create_default_context()
   context.check_hostname = False
   context.verify_mode = ssl.CERT_NONE
   ```

2. **Timeout de Connexion**
   ```python
   # Augmenter les timeouts
   self.es = Elasticsearch(
       hosts,
       timeout=60,
       max_retries=5,
       retry_on_timeout=True
   )
   ```

3. **Authentification**
   ```python
   # Vérifier les credentials
   try:
       self.es.security.get_user()
   except Exception as e:
       logging.error(f"Auth failed: {e}")
   ```

### Logs de Debug

```python
import logging
logging.basicConfig(level=logging.DEBUG)
elasticsearch_logger = logging.getLogger('elasticsearch')
elasticsearch_logger.setLevel(logging.DEBUG)
```

## Performance

### Optimisations Recommandées

1. **Bulk Operations**
   ```python
   def bulk_index_logs(self, logs_data):
       actions = []
       for log in logs_data:
           action = {
               "_index": f"security-logs-{log['@timestamp'][:10]}",
               "_source": log
           }
           actions.append(action)
       
       return helpers.bulk(self.es, actions)
   ```

2. **Pagination**
   ```python
   def scroll_search(self, query, index="logs-*", scroll_time="2m"):
       response = self.es.search(
           index=index,
           body=query,
           scroll=scroll_time,
           size=1000
       )
       
       while response['hits']['hits']:
           yield response['hits']['hits']
           response = self.es.scroll(
               scroll_id=response['_scroll_id'],
               scroll=scroll_time
           )
   ```

3. **Cache des Requêtes**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def cached_search(self, query_hash, index, hours):
       return self.search_logs(query_hash, index, hours)
   ```