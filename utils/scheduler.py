"""
Scheduler - Tâches automatisées et monitoring
"""

import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

from config import Config
from utils.data_loader import DataLoader
from utils.ai_detector import AIDetector
from utils.alert_manager import AlertManager
from utils.notifications import NotificationManager

class SOCScheduler:
    def __init__(self):
        self.config = Config()
        self.data_loader = DataLoader()
        self.ai_detector = AIDetector()
        self.alert_manager = AlertManager()
        self.notification_manager = NotificationManager()
        self.running = False
        self.thread = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Démarre le scheduler"""
        if self.running:
            return
        
        self.running = True
        self._schedule_jobs()
        
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        self.logger.info("SOC Scheduler démarré")
    
    def stop(self):
        """Arrête le scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("SOC Scheduler arrêté")
    
    def _schedule_jobs(self):
        """Configure les tâches planifiées"""
        
        # Vérification des alertes toutes les minutes
        schedule.every(1).minutes.do(self._check_alerts)
        
        # Réentraînement du modèle ML quotidien
        schedule.every().day.at("02:00").do(self._retrain_model)
        
        # Nettoyage des logs anciens hebdomadaire
        schedule.every().sunday.at("03:00").do(self._cleanup_old_logs)
        
        # Rapport quotidien
        schedule.every().day.at("08:00").do(self._send_daily_report)
        
        # Sauvegarde des données
        schedule.every().day.at("01:00").do(self._backup_data)
        
        # Health check toutes les 5 minutes
        schedule.every(5).minutes.do(self._health_check)
    
    def _run_scheduler(self):
        """Boucle principale du scheduler"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Erreur scheduler: {e}")
                time.sleep(60)  # Attendre 1 minute avant de reprendre
    
    def _check_alerts(self):
        """Vérifie les nouvelles alertes"""
        try:
            logs_df = self.data_loader.load_logs()
            if logs_df.empty:
                return
            
            # Vérifier les règles d'alerte
            triggered_alerts = self.alert_manager.check_alerts(logs_df, time_window_minutes=5)
            
            # Envoyer les notifications pour les nouvelles alertes
            for alert in triggered_alerts:
                if alert['severity'] in ['critical', 'high']:
                    self.notification_manager.send_alert_notification(alert)
            
            if triggered_alerts:
                self.logger.info(f"{len(triggered_alerts)} nouvelles alertes détectées")
        
        except Exception as e:
            self.logger.error(f"Erreur vérification alertes: {e}")
    
    def _retrain_model(self):
        """Réentraîne le modèle ML"""
        try:
            logs_df = self.data_loader.load_logs(refresh=True)
            if logs_df.empty:
                self.logger.warning("Pas de données pour réentraînement")
                return
            
            # Réentraîner seulement si assez de nouvelles données
            if len(logs_df) < 100:
                self.logger.info("Pas assez de données pour réentraînement")
                return
            
            result = self.ai_detector.train_model(logs_df)
            
            if result['success']:
                self.logger.info(f"Modèle réentraîné: {result['samples_trained']} échantillons")
                
                # Notification du réentraînement
                self.notification_manager.send_alert_notification({
                    'rule_name': 'ML Model Retrained',
                    'severity': 'low',
                    'message': f"Modèle ML réentraîné avec {result['samples_trained']} échantillons. Anomalies: {result['anomaly_rate']:.1f}%",
                    'timestamp': datetime.now().isoformat()
                }, channels=['telegram'])
            else:
                self.logger.error(f"Échec réentraînement: {result['error']}")
        
        except Exception as e:
            self.logger.error(f"Erreur réentraînement: {e}")
    
    def _cleanup_old_logs(self):
        """Nettoie les anciens logs"""
        try:
            logs_dir = self.config.LOGS_DIR
            exports_dir = self.config.EXPORTS_DIR
            
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # Nettoyer les logs
            cleaned_files = 0
            for log_file in logs_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    cleaned_files += 1
            
            # Nettoyer les exports
            for export_file in exports_dir.glob("*"):
                if export_file.stat().st_mtime < cutoff_date.timestamp():
                    export_file.unlink()
                    cleaned_files += 1
            
            self.logger.info(f"Nettoyage terminé: {cleaned_files} fichiers supprimés")
        
        except Exception as e:
            self.logger.error(f"Erreur nettoyage: {e}")
    
    def _send_daily_report(self):
        """Envoie le rapport quotidien"""
        try:
            # Calculer les statistiques des dernières 24h
            logs_df = self.data_loader.load_logs()
            if logs_df.empty:
                return
            
            # Filtrer les logs des dernières 24h
            cutoff = datetime.now() - timedelta(hours=24)
            recent_logs = logs_df[logs_df['timestamp'] >= cutoff]
            
            # Statistiques
            total_events = len(recent_logs)
            critical_events = len(recent_logs[recent_logs['severity'] == 'critical'])
            high_events = len(recent_logs[recent_logs['severity'] == 'high'])
            
            # Alertes des dernières 24h
            alert_history = self.alert_manager.get_alert_history(24)
            
            # Préparer le rapport
            report = {
                'rule_name': 'Rapport Quotidien SOC',
                'severity': 'low',
                'message': f"""
📊 RAPPORT QUOTIDIEN SOC - {datetime.now().strftime('%d/%m/%Y')}

🔢 Événements (24h):
• Total: {total_events:,}
• Critiques: {critical_events}
• Élevés: {high_events}

🚨 Alertes générées: {len(alert_history)}

🤖 Modèle ML: {'✅ Actif' if self.ai_detector.is_model_trained() else '❌ Inactif'}

📈 Top événements:
{recent_logs['event_type'].value_counts().head(3).to_string() if not recent_logs.empty else 'Aucun'}

---
Rapport automatique SOC Dashboard
                """,
                'timestamp': datetime.now().isoformat()
            }
            
            # Envoyer le rapport
            self.notification_manager.send_alert_notification(report, channels=['email', 'telegram'])
            
            self.logger.info("Rapport quotidien envoyé")
        
        except Exception as e:
            self.logger.error(f"Erreur rapport quotidien: {e}")
    
    def _backup_data(self):
        """Sauvegarde les données importantes"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.config.BASE_DIR / "backups" / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder les fichiers de données
            import shutil
            
            files_to_backup = [
                self.config.DATA_DIR / "logs.csv",
                self.config.DATA_DIR / "vulns.json", 
                self.config.DATA_DIR / "hosts.csv",
                self.config.DATA_DIR / "tickets.json"
            ]
            
            backed_up = 0
            for file_path in files_to_backup:
                if file_path.exists():
                    shutil.copy2(file_path, backup_dir)
                    backed_up += 1
            
            # Sauvegarder les modèles ML
            models_backup = backup_dir / "models"
            models_backup.mkdir(exist_ok=True)
            
            for model_file in self.config.MODELS_DIR.glob("*.pkl"):
                shutil.copy2(model_file, models_backup)
                backed_up += 1
            
            self.logger.info(f"Sauvegarde créée: {backed_up} fichiers dans {backup_dir}")
        
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde: {e}")
    
    def _health_check(self):
        """Vérification de santé du système"""
        try:
            issues = []
            
            # Vérifier les répertoires
            required_dirs = [
                self.config.DATA_DIR,
                self.config.MODELS_DIR,
                self.config.LOGS_DIR
            ]
            
            for dir_path in required_dirs:
                if not dir_path.exists():
                    issues.append(f"Répertoire manquant: {dir_path}")
            
            # Vérifier les fichiers de données
            data_files = [
                self.config.DATA_DIR / "logs.csv",
                self.config.DATA_DIR / "vulns.json"
            ]
            
            for file_path in data_files:
                if not file_path.exists():
                    issues.append(f"Fichier manquant: {file_path}")
                elif file_path.stat().st_size == 0:
                    issues.append(f"Fichier vide: {file_path}")
            
            # Vérifier le modèle ML
            if not self.ai_detector.is_model_trained():
                issues.append("Modèle ML non entraîné")
            
            # Alerter si des problèmes sont détectés
            if issues:
                self.logger.warning(f"Health check: {len(issues)} problèmes détectés")
                
                # Envoyer alerte pour problèmes critiques
                critical_issues = [issue for issue in issues if "manquant" in issue]
                if critical_issues:
                    self.notification_manager.send_alert_notification({
                        'rule_name': 'System Health Check',
                        'severity': 'high',
                        'message': f"Problèmes système détectés:\n" + "\n".join(critical_issues),
                        'timestamp': datetime.now().isoformat()
                    }, channels=['telegram'])
            else:
                self.logger.debug("Health check: Système OK")
        
        except Exception as e:
            self.logger.error(f"Erreur health check: {e}")
    
    def run_manual_task(self, task_name):
        """Exécute une tâche manuellement"""
        tasks = {
            'check_alerts': self._check_alerts,
            'retrain_model': self._retrain_model,
            'cleanup_logs': self._cleanup_old_logs,
            'send_report': self._send_daily_report,
            'backup_data': self._backup_data,
            'health_check': self._health_check
        }
        
        if task_name in tasks:
            try:
                tasks[task_name]()
                return True
            except Exception as e:
                self.logger.error(f"Erreur tâche {task_name}: {e}")
                return False
        else:
            self.logger.error(f"Tâche inconnue: {task_name}")
            return False

# Instance globale du scheduler
soc_scheduler = SOCScheduler()

def start_scheduler():
    """Démarre le scheduler global"""
    soc_scheduler.start()

def stop_scheduler():
    """Arrête le scheduler global"""
    soc_scheduler.stop()

if __name__ == "__main__":
    # Test du scheduler
    scheduler = SOCScheduler()
    
    print("Démarrage du scheduler de test...")
    scheduler.start()
    
    try:
        # Laisser tourner pendant 30 secondes
        time.sleep(30)
        
        # Test d'une tâche manuelle
        print("Test tâche manuelle...")
        scheduler.run_manual_task('health_check')
        
    except KeyboardInterrupt:
        print("Arrêt du scheduler...")
    finally:
        scheduler.stop()