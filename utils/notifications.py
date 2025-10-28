"""
Module de notifications - Email et Telegram
"""

import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config

class NotificationManager:
    def __init__(self):
        self.config = Config()
    
    def send_email(self, to_email, subject, body, html_body=None):
        """Envoie un email"""
        if not self.config.SMTP_HOST:
            logging.warning("SMTP non configuré")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.SMTP_USERNAME
            msg['To'] = to_email
            
            # Texte brut
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # HTML si fourni
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Connexion SMTP
            server = smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT)
            server.starttls()
            server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
            
            # Envoi
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email envoyé à {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Erreur envoi email: {e}")
            return False
    
    def send_telegram(self, message):
        """Envoie un message Telegram"""
        if not self.config.TELEGRAM_BOT_TOKEN:
            logging.warning("Telegram non configuré")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage"
            
            payload = {
                'chat_id': self.config.TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logging.info("Message Telegram envoyé")
                return True
            else:
                logging.error(f"Erreur Telegram: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Erreur Telegram: {e}")
            return False
    
    def send_alert_notification(self, alert_data, channels=['email', 'telegram']):
        """Envoie une notification d'alerte"""
        
        # Formatage du message
        subject = f"[SOC ALERT] {alert_data.get('severity', '').upper()} - {alert_data.get('rule_name', 'Unknown')}"
        
        body = f"""
ALERTE SOC DÉTECTÉE

Règle: {alert_data.get('rule_name', 'N/A')}
Sévérité: {alert_data.get('severity', 'N/A')}
Timestamp: {alert_data.get('timestamp', datetime.now().isoformat())}
Source IP: {alert_data.get('source_ip', 'N/A')}
Destination IP: {alert_data.get('destination_ip', 'N/A')}
Description: {alert_data.get('message', 'N/A')}

Score de risque: {alert_data.get('risk_score', 0)}/100

Action requise: Vérifier et traiter selon les procédures SOC.

---
SOC Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        html_body = f"""
        <html>
        <body>
        <h2 style="color: {'#ff4444' if alert_data.get('severity') == 'critical' else '#ff8800'};">
            🚨 ALERTE SOC DÉTECTÉE
        </h2>
        
        <table border="1" style="border-collapse: collapse;">
        <tr><td><b>Règle</b></td><td>{alert_data.get('rule_name', 'N/A')}</td></tr>
        <tr><td><b>Sévérité</b></td><td>{alert_data.get('severity', 'N/A')}</td></tr>
        <tr><td><b>Timestamp</b></td><td>{alert_data.get('timestamp', datetime.now().isoformat())}</td></tr>
        <tr><td><b>Source IP</b></td><td>{alert_data.get('source_ip', 'N/A')}</td></tr>
        <tr><td><b>Destination IP</b></td><td>{alert_data.get('destination_ip', 'N/A')}</td></tr>
        <tr><td><b>Score de risque</b></td><td>{alert_data.get('risk_score', 0)}/100</td></tr>
        </table>
        
        <p><b>Description:</b> {alert_data.get('message', 'N/A')}</p>
        
        <p><i>Action requise: Vérifier et traiter selon les procédures SOC.</i></p>
        
        <hr>
        <small>SOC Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
        </body>
        </html>
        """
        
        # Message Telegram (formaté)
        telegram_message = f"""
🚨 <b>ALERTE SOC</b>

<b>Règle:</b> {alert_data.get('rule_name', 'N/A')}
<b>Sévérité:</b> {alert_data.get('severity', 'N/A')}
<b>Source:</b> {alert_data.get('source_ip', 'N/A')}
<b>Risque:</b> {alert_data.get('risk_score', 0)}/100

{alert_data.get('message', 'N/A')}

<i>Timestamp: {datetime.now().strftime('%H:%M:%S')}</i>
        """
        
        results = {}
        
        # Envoi email
        if 'email' in channels and self.config.SMTP_HOST:
            # Email par défaut SOC
            soc_email = "soc@company.com"  # À configurer
            results['email'] = self.send_email(soc_email, subject, body, html_body)
        
        # Envoi Telegram
        if 'telegram' in channels:
            results['telegram'] = self.send_telegram(telegram_message)
        
        return results
    
    def send_incident_update(self, incident_data, update_type='created'):
        """Envoie une notification de mise à jour d'incident"""
        
        action_map = {
            'created': 'CRÉÉ',
            'updated': 'MIS À JOUR', 
            'resolved': 'RÉSOLU',
            'escalated': 'ESCALADÉ'
        }
        
        action = action_map.get(update_type, 'MODIFIÉ')
        
        subject = f"[SOC INCIDENT] {action} - {incident_data.get('id', 'N/A')}"
        
        body = f"""
INCIDENT {action}

ID: {incident_data.get('id', 'N/A')}
Titre: {incident_data.get('title', 'N/A')}
Sévérité: {incident_data.get('severity', 'N/A')}
Statut: {incident_data.get('status', 'N/A')}
Assigné: {incident_data.get('assignee', 'N/A')}

Description:
{incident_data.get('description', 'N/A')}

Lien: http://soc-dashboard/incidents/{incident_data.get('id', '')}

---
SOC Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Envoi selon la sévérité
        if incident_data.get('severity') in ['critical', 'high']:
            return self.send_alert_notification({
                'rule_name': f"Incident {action}",
                'severity': incident_data.get('severity'),
                'message': body,
                'timestamp': datetime.now().isoformat()
            })
        
        return {'email': False, 'telegram': False}
    
    def test_notifications(self):
        """Test des notifications"""
        test_alert = {
            'rule_name': 'Test Notification',
            'severity': 'medium',
            'source_ip': '192.168.1.100',
            'destination_ip': '10.0.0.1',
            'message': 'Ceci est un test de notification SOC Dashboard',
            'risk_score': 75,
            'timestamp': datetime.now().isoformat()
        }
        
        results = self.send_alert_notification(test_alert)
        
        return {
            'email_configured': bool(self.config.SMTP_HOST),
            'telegram_configured': bool(self.config.TELEGRAM_BOT_TOKEN),
            'email_sent': results.get('email', False),
            'telegram_sent': results.get('telegram', False)
        }

# Fonctions utilitaires
def format_alert_for_slack(alert_data):
    """Formate une alerte pour Slack (futur)"""
    color_map = {
        'critical': '#ff0000',
        'high': '#ff8800',
        'medium': '#ffcc00',
        'low': '#00ff00'
    }
    
    return {
        "attachments": [
            {
                "color": color_map.get(alert_data.get('severity'), '#888888'),
                "title": f"🚨 Alerte SOC - {alert_data.get('rule_name')}",
                "fields": [
                    {"title": "Sévérité", "value": alert_data.get('severity'), "short": True},
                    {"title": "Source IP", "value": alert_data.get('source_ip'), "short": True},
                    {"title": "Score de risque", "value": f"{alert_data.get('risk_score', 0)}/100", "short": True}
                ],
                "text": alert_data.get('message'),
                "footer": "SOC Dashboard",
                "ts": int(datetime.now().timestamp())
            }
        ]
    }

if __name__ == "__main__":
    # Test des notifications
    nm = NotificationManager()
    results = nm.test_notifications()
    
    print("Test des notifications:")
    print(f"Email configuré: {results['email_configured']}")
    print(f"Telegram configuré: {results['telegram_configured']}")
    print(f"Email envoyé: {results['email_sent']}")
    print(f"Telegram envoyé: {results['telegram_sent']}")