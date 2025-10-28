"""
Alert Manager - Gestion des alertes et notifications
"""

import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging

class AlertManager:
    def __init__(self):
        self.rules = self._load_rules()
        self.alerts_log = Path(__file__).parent.parent / "logs" / "alerts_sent.log"
        self.alerts_log.parent.mkdir(exist_ok=True)
    
    def _load_rules(self):
        """Charge les règles d'alerting"""
        return [
            {
                'name': 'SSH Bruteforce',
                'condition': lambda df: len(df[df['event_type'] == 'ssh_bruteforce']) > 10,
                'severity': 'critical',
                'message': 'Plus de 10 tentatives SSH bruteforce détectées'
            },
            {
                'name': 'Port Scan',
                'condition': lambda df: len(df[df['event_type'] == 'port_scan']) > 5,
                'severity': 'high',
                'message': 'Activité de scan de ports détectée'
            },
            {
                'name': 'High Volume Traffic',
                'condition': lambda df: df['bytes_in'].sum() > 1000000,
                'severity': 'medium',
                'message': 'Volume de trafic élevé détecté'
            },
            {
                'name': 'Failed Login',
                'condition': lambda df: len(df[df['event_type'] == 'failed_login']) > 20,
                'severity': 'high',
                'message': 'Nombreuses tentatives de connexion échouées'
            }
        ]
    
    def check_alerts(self, df, time_window_minutes=5):
        """Vérifie les règles d'alerte sur les données récentes"""
        if df.empty:
            return []
        
        # Filtrer les données récentes
        cutoff = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_df = df[df['timestamp'] >= cutoff] if 'timestamp' in df.columns else df
        
        triggered_alerts = []
        
        for rule in self.rules:
            try:
                if rule['condition'](recent_df):
                    alert = {
                        'timestamp': datetime.now(),
                        'rule_name': rule['name'],
                        'severity': rule['severity'],
                        'message': rule['message'],
                        'affected_records': len(recent_df)
                    }
                    triggered_alerts.append(alert)
                    self._log_alert(alert)
            except Exception as e:
                logging.error(f"Erreur règle {rule['name']}: {e}")
        
        return triggered_alerts
    
    def _log_alert(self, alert):
        """Enregistre l'alerte dans le fichier log"""
        try:
            with open(self.alerts_log, 'a') as f:
                log_entry = {
                    'timestamp': alert['timestamp'].isoformat(),
                    'rule': alert['rule_name'],
                    'severity': alert['severity'],
                    'message': alert['message']
                }
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logging.error(f"Erreur log alerte: {e}")
    
    def get_alert_history(self, hours=24):
        """Récupère l'historique des alertes"""
        if not self.alerts_log.exists():
            return []
        
        alerts = []
        cutoff = datetime.now() - timedelta(hours=hours)
        
        try:
            with open(self.alerts_log, 'r') as f:
                for line in f:
                    try:
                        alert = json.loads(line.strip())
                        alert_time = datetime.fromisoformat(alert['timestamp'])
                        if alert_time >= cutoff:
                            alerts.append(alert)
                    except:
                        continue
        except Exception as e:
            logging.error(f"Erreur lecture historique: {e}")
        
        return sorted(alerts, key=lambda x: x['timestamp'], reverse=True)
    
    def send_notification(self, alert, method='log'):
        """Envoie une notification (stub)"""
        if method == 'email':
            return self._send_email_stub(alert)
        elif method == 'telegram':
            return self._send_telegram_stub(alert)
        else:
            return self._log_notification(alert)
    
    def _send_email_stub(self, alert):
        """Stub pour notification email"""
        # TODO: Implémenter SMTP
        logging.info(f"EMAIL STUB: {alert['message']}")
        return True
    
    def _send_telegram_stub(self, alert):
        """Stub pour notification Telegram"""
        # TODO: Implémenter Telegram Bot API
        logging.info(f"TELEGRAM STUB: {alert['message']}")
        return True
    
    def _log_notification(self, alert):
        """Log de la notification"""
        logging.info(f"ALERT: {alert['severity'].upper()} - {alert['message']}")
        return True
    
    def get_alert_stats(self):
        """Statistiques des alertes"""
        history = self.get_alert_history(24)
        
        if not history:
            return {
                'total': 0,
                'by_severity': {},
                'by_rule': {},
                'last_24h': 0
            }
        
        severity_counts = {}
        rule_counts = {}
        
        for alert in history:
            severity = alert.get('severity', 'unknown')
            rule = alert.get('rule', 'unknown')
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
        
        return {
            'total': len(history),
            'by_severity': severity_counts,
            'by_rule': rule_counts,
            'last_24h': len(history)
        }