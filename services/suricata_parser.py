"""
Suricata Parser - Analyse des logs EVE JSON
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd

class SuricataParser:
    def __init__(self):
        self.supported_event_types = [
            'alert', 'http', 'dns', 'tls', 'ssh', 'flow', 
            'netflow', 'fileinfo', 'stats', 'drop'
        ]
    
    def parse_eve_log(self, log_line):
        """Parse une ligne de log EVE JSON"""
        try:
            event = json.loads(log_line.strip())
            return self._normalize_event(event)
        except json.JSONDecodeError as e:
            logging.error(f"Erreur parsing JSON: {e}")
            return None
        except Exception as e:
            logging.error(f"Erreur parsing event: {e}")
            return None
    
    def parse_eve_file(self, file_path, max_events=None):
        """Parse un fichier EVE complet"""
        events = []
        
        try:
            with open(file_path, 'r') as f:
                for i, line in enumerate(f):
                    if max_events and i >= max_events:
                        break
                    
                    event = self.parse_eve_log(line)
                    if event:
                        events.append(event)
            
            return pd.DataFrame(events)
        
        except FileNotFoundError:
            logging.error(f"Fichier non trouvé: {file_path}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Erreur lecture fichier: {e}")
            return pd.DataFrame()
    
    def _normalize_event(self, event):
        """Normalise un événement Suricata vers le format SOC Dashboard"""
        
        # Extraction des champs communs
        normalized = {
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
            'event_type': event.get('event_type', 'unknown'),
            'src_ip': event.get('src_ip', ''),
            'dst_ip': event.get('dest_ip', ''),
            'src_port': event.get('src_port', 0),
            'dst_port': event.get('dest_port', 0),
            'protocol': event.get('proto', '').upper(),
            'flow_id': event.get('flow_id', 0)
        }
        
        # Traitement spécifique par type d'événement
        event_type = event.get('event_type')
        
        if event_type == 'alert':
            normalized.update(self._parse_alert(event))
        elif event_type == 'http':
            normalized.update(self._parse_http(event))
        elif event_type == 'dns':
            normalized.update(self._parse_dns(event))
        elif event_type == 'tls':
            normalized.update(self._parse_tls(event))
        elif event_type == 'ssh':
            normalized.update(self._parse_ssh(event))
        elif event_type == 'flow':
            normalized.update(self._parse_flow(event))
        
        return normalized
    
    def _parse_alert(self, event):
        """Parse les alertes Suricata"""
        alert = event.get('alert', {})
        
        return {
            'severity': self._map_severity(alert.get('severity', 3)),
            'signature': alert.get('signature', ''),
            'signature_id': alert.get('signature_id', 0),
            'category': alert.get('category', ''),
            'action': alert.get('action', ''),
            'bytes_in': event.get('flow', {}).get('bytes_toserver', 0),
            'bytes_out': event.get('flow', {}).get('bytes_toclient', 0),
            'packets_in': event.get('flow', {}).get('pkts_toserver', 0),
            'packets_out': event.get('flow', {}).get('pkts_toclient', 0)
        }
    
    def _parse_http(self, event):
        """Parse les événements HTTP"""
        http = event.get('http', {})
        
        return {
            'severity': 'low',
            'http_method': http.get('http_method', ''),
            'hostname': http.get('hostname', ''),
            'url': http.get('url', ''),
            'user_agent': http.get('http_user_agent', ''),
            'status_code': http.get('status', 0),
            'length': http.get('length', 0),
            'bytes_in': http.get('request_body_len', 0),
            'bytes_out': http.get('response_body_len', 0)
        }
    
    def _parse_dns(self, event):
        """Parse les événements DNS"""
        dns = event.get('dns', {})
        
        return {
            'severity': 'low',
            'dns_query': dns.get('rrname', ''),
            'dns_type': dns.get('rrtype', ''),
            'dns_response': dns.get('rcode', ''),
            'dns_answers': len(dns.get('answers', [])),
            'bytes_in': 64,  # Taille approximative requête DNS
            'bytes_out': 128  # Taille approximative réponse DNS
        }
    
    def _parse_tls(self, event):
        """Parse les événements TLS"""
        tls = event.get('tls', {})
        
        return {
            'severity': 'low',
            'tls_version': tls.get('version', ''),
            'tls_subject': tls.get('subject', ''),
            'tls_issuer': tls.get('issuerdn', ''),
            'tls_fingerprint': tls.get('fingerprint', ''),
            'tls_sni': tls.get('sni', ''),
            'bytes_in': 1000,  # Estimation handshake TLS
            'bytes_out': 1500
        }
    
    def _parse_ssh(self, event):
        """Parse les événements SSH"""
        ssh = event.get('ssh', {})
        
        return {
            'severity': 'medium' if ssh.get('client', {}).get('software_version') else 'low',
            'ssh_client': ssh.get('client', {}).get('software_version', ''),
            'ssh_server': ssh.get('server', {}).get('software_version', ''),
            'bytes_in': 500,  # Estimation connexion SSH
            'bytes_out': 300
        }
    
    def _parse_flow(self, event):
        """Parse les événements de flux"""
        flow = event.get('flow', {})
        
        return {
            'severity': 'low',
            'bytes_in': flow.get('bytes_toserver', 0),
            'bytes_out': flow.get('bytes_toclient', 0),
            'packets_in': flow.get('pkts_toserver', 0),
            'packets_out': flow.get('pkts_toclient', 0),
            'duration': self._calculate_duration(flow),
            'flow_state': flow.get('state', ''),
            'flow_reason': flow.get('reason', '')
        }
    
    def _map_severity(self, suricata_severity):
        """Mappe la sévérité Suricata vers notre format"""
        severity_map = {
            1: 'critical',
            2: 'high', 
            3: 'medium',
            4: 'low'
        }
        return severity_map.get(suricata_severity, 'low')
    
    def _calculate_duration(self, flow):
        """Calcule la durée d'un flux"""
        try:
            start = flow.get('start')
            end = flow.get('end')
            
            if start and end:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                return int((end_dt - start_dt).total_seconds())
        except:
            pass
        
        return 0
    
    def get_statistics(self, events_df):
        """Calcule des statistiques sur les événements parsés"""
        if events_df.empty:
            return {}
        
        stats = {
            'total_events': len(events_df),
            'event_types': events_df['event_type'].value_counts().to_dict(),
            'severity_distribution': events_df['severity'].value_counts().to_dict(),
            'top_source_ips': events_df['src_ip'].value_counts().head(10).to_dict(),
            'top_dest_ips': events_df['dst_ip'].value_counts().head(10).to_dict(),
            'protocol_distribution': events_df['protocol'].value_counts().to_dict(),
            'total_bytes_in': events_df['bytes_in'].sum(),
            'total_bytes_out': events_df['bytes_out'].sum(),
            'time_range': {
                'start': events_df['timestamp'].min(),
                'end': events_df['timestamp'].max()
            }
        }
        
        return stats
    
    def filter_high_risk_events(self, events_df, risk_threshold=None):
        """Filtre les événements à haut risque"""
        if events_df.empty:
            return events_df
        
        # Critères de haut risque
        high_risk_conditions = (
            (events_df['severity'].isin(['critical', 'high'])) |
            (events_df['event_type'] == 'alert') |
            (events_df['bytes_in'] > 100000) |  # Gros volumes
            (events_df['bytes_out'] > 100000)
        )
        
        return events_df[high_risk_conditions]

# Fonctions utilitaires
def parse_suricata_stats(stats_event):
    """Parse les statistiques Suricata"""
    stats = stats_event.get('stats', {})
    
    return {
        'uptime': stats.get('uptime', 0),
        'packets_received': stats.get('capture', {}).get('kernel_packets', 0),
        'packets_dropped': stats.get('capture', {}).get('kernel_drops', 0),
        'alerts_generated': stats.get('detect', {}).get('alert', 0),
        'tcp_sessions': stats.get('flow', {}).get('tcp', 0),
        'udp_sessions': stats.get('flow', {}).get('udp', 0),
        'memory_usage': stats.get('memuse', 0)
    }

def create_suricata_rules_from_events(events_df, min_occurrences=5):
    """Crée des règles Suricata basées sur les patterns détectés"""
    if events_df.empty:
        return []
    
    rules = []
    
    # Analyser les patterns d'attaque
    attack_patterns = events_df[
        events_df['severity'].isin(['critical', 'high'])
    ].groupby(['src_ip', 'dst_port', 'event_type']).size()
    
    frequent_patterns = attack_patterns[attack_patterns >= min_occurrences]
    
    for (src_ip, dst_port, event_type), count in frequent_patterns.items():
        rule = {
            'action': 'alert',
            'protocol': 'tcp',
            'source_ip': src_ip,
            'source_port': 'any',
            'direction': '->',
            'dest_ip': 'any',
            'dest_port': dst_port,
            'msg': f'Suspicious {event_type} activity from {src_ip}',
            'sid': hash(f"{src_ip}_{dst_port}_{event_type}") % 1000000,
            'rev': 1,
            'threshold': f'type both, track by_src, count {min_occurrences}, seconds 300'
        }
        rules.append(rule)
    
    return rules

# Configuration par défaut
SURICATA_CONFIG = {
    'eve_log_path': '/var/log/suricata/eve.json',
    'max_events_per_batch': 10000,
    'high_risk_threshold': 70,
    'supported_versions': ['6.0', '7.0'],
    'default_severity_mapping': {
        1: 'critical',
        2: 'high',
        3: 'medium', 
        4: 'low'
    }
}

if __name__ == "__main__":
    # Test du parser
    print("Test du parser Suricata...")
    
    parser = SuricataParser()
    
    # Test avec un événement d'exemple
    sample_eve_log = '''{"timestamp":"2025-01-15T10:30:00.000000+0000","flow_id":123456,"event_type":"alert","src_ip":"192.168.1.100","dest_ip":"10.0.0.1","src_port":12345,"dest_port":80,"proto":"TCP","alert":{"action":"allowed","gid":1,"signature_id":2001,"rev":1,"signature":"Test Alert","category":"Attempted Information Leak","severity":2}}'''
    
    event = parser.parse_eve_log(sample_eve_log)
    if event:
        print("Événement parsé avec succès:")
        for key, value in event.items():
            print(f"  {key}: {value}")
    
    # Test avec données simulées
    sample_events = pd.DataFrame([event] if event else [])
    
    if not sample_events.empty:
        stats = parser.get_statistics(sample_events)
        print(f"\nStatistiques: {stats}")
        
        high_risk = parser.filter_high_risk_events(sample_events)
        print(f"Événements à haut risque: {len(high_risk)}")
    
    print("\nParser Suricata initialisé avec succès!")