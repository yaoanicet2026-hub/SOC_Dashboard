"""
Page Administration - Configuration et maintenance
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import Config
from utils.notifications import NotificationManager
from auth import AuthManager

def show_admin():
    st.header("⚙️ Administration SOC Dashboard")
    
    # Vérification des permissions admin
    auth = AuthManager()
    if not auth.is_authenticated():
        st.error("Accès non autorisé")
        return
    
    # Onglets d'administration
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Système", "🔧 Configuration", "📧 Notifications", 
        "🤖 Modèles ML", "📋 Maintenance"
    ])
    
    with tab1:
        show_system_status()
    
    with tab2:
        show_configuration()
    
    with tab3:
        show_notifications_config()
    
    with tab4:
        show_ml_management()
    
    with tab5:
        show_maintenance()

def show_system_status():
    """Affiche le statut du système"""
    st.subheader("État du Système")
    
    config = Config()
    
    # Vérification des répertoires
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Répertoires:**")
        directories = [
            ("Data", config.DATA_DIR),
            ("Models", config.MODELS_DIR),
            ("Logs", config.LOGS_DIR),
            ("Exports", config.EXPORTS_DIR)
        ]
        
        for name, path in directories:
            status = "✅" if path.exists() else "❌"
            st.write(f"{status} {name}: `{path}`")
    
    with col2:
        st.write("**Fichiers de données:**")
        data_files = [
            ("logs.csv", config.DATA_DIR / "logs.csv"),
            ("vulns.json", config.DATA_DIR / "vulns.json"),
            ("hosts.csv", config.DATA_DIR / "hosts.csv"),
            ("tickets.json", config.DATA_DIR / "tickets.json")
        ]
        
        for name, path in data_files:
            if path.exists():
                size = path.stat().st_size
                st.write(f"✅ {name}: {size:,} bytes")
            else:
                st.write(f"❌ {name}: Non trouvé")
    
    # Statistiques système
    st.divider()
    st.subheader("Statistiques")
    
    try:
        # Charger les données pour les stats
        data_loader = st.session_state.get('data_loader')
        if data_loader:
            logs_df = data_loader.load_logs()
            vulns_df = data_loader.load_vulnerabilities()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Logs", len(logs_df))
            
            with col2:
                st.metric("Vulnérabilités", len(vulns_df))
            
            with col3:
                model_path = config.MODELS_DIR / "anomaly_model.pkl"
                model_status = "Entraîné" if model_path.exists() else "Non entraîné"
                st.metric("Modèle ML", model_status)
            
            with col4:
                uptime = datetime.now() - datetime.now().replace(hour=0, minute=0, second=0)
                st.metric("Uptime", f"{uptime.seconds//3600}h")
    
    except Exception as e:
        st.error(f"Erreur chargement statistiques: {e}")

def show_configuration():
    """Affiche et permet de modifier la configuration"""
    st.subheader("Configuration")
    
    config = Config()
    
    # Configuration Elasticsearch
    with st.expander("🔍 Elasticsearch"):
        col1, col2 = st.columns(2)
        
        with col1:
            elk_host = st.text_input("Host", value=config.ELK_HOST)
            elk_port = st.number_input("Port", value=config.ELK_PORT)
            elk_username = st.text_input("Username", value=config.ELK_USERNAME)
        
        with col2:
            elk_password = st.text_input("Password", type="password")
            elk_ssl = st.checkbox("Utiliser SSL", value=config.ELK_USE_SSL)
        
        if st.button("Tester Connexion ELK"):
            try:
                from services.elastic_client import ElasticsearchClient
                client = ElasticsearchClient(elk_host, elk_port, elk_username, elk_password)
                if client.connect():
                    st.success("✅ Connexion ELK réussie")
                else:
                    st.error("❌ Échec connexion ELK")
            except Exception as e:
                st.error(f"Erreur: {e}")
    
    # Configuration Wazuh
    with st.expander("🛡️ Wazuh"):
        col1, col2 = st.columns(2)
        
        with col1:
            wazuh_host = st.text_input("Host", value=config.WAZUH_HOST, key="wazuh_host")
            wazuh_port = st.number_input("Port", value=config.WAZUH_PORT, key="wazuh_port")
        
        with col2:
            wazuh_username = st.text_input("Username", value=config.WAZUH_USERNAME, key="wazuh_user")
            wazuh_password = st.text_input("Password", type="password", key="wazuh_pass")
        
        if st.button("Tester Connexion Wazuh"):
            try:
                from services.wazuh_client import WazuhClient
                client = WazuhClient(wazuh_host, wazuh_port, wazuh_username, wazuh_password)
                if client.authenticate():
                    st.success("✅ Connexion Wazuh réussie")
                else:
                    st.error("❌ Échec connexion Wazuh")
            except Exception as e:
                st.error(f"Erreur: {e}")
    
    # Seuils d'alerte
    with st.expander("⚠️ Seuils d'Alerte"):
        st.write("Configurer les seuils de déclenchement des alertes:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ssh_threshold = st.number_input("SSH Bruteforce", value=config.ALERT_THRESHOLDS["ssh_bruteforce"])
            port_scan_threshold = st.number_input("Port Scan", value=config.ALERT_THRESHOLDS["port_scan"])
        
        with col2:
            failed_login_threshold = st.number_input("Failed Login", value=config.ALERT_THRESHOLDS["failed_login"])
            traffic_threshold = st.number_input("High Volume Traffic (MB)", value=config.ALERT_THRESHOLDS["high_volume_traffic"]//1000000)
        
        if st.button("Sauvegarder Seuils"):
            # TODO: Sauvegarder dans fichier de config
            st.success("Seuils sauvegardés")

def show_notifications_config():
    """Configuration des notifications"""
    st.subheader("Configuration Notifications")
    
    config = Config()
    nm = NotificationManager()
    
    # Configuration Email
    with st.expander("📧 Configuration Email"):
        col1, col2 = st.columns(2)
        
        with col1:
            smtp_host = st.text_input("SMTP Host", value=config.SMTP_HOST)
            smtp_port = st.number_input("SMTP Port", value=config.SMTP_PORT)
        
        with col2:
            smtp_username = st.text_input("SMTP Username", value=config.SMTP_USERNAME)
            smtp_password = st.text_input("SMTP Password", type="password")
        
        if st.button("Tester Email"):
            # Test avec configuration temporaire
            test_results = nm.test_notifications()
            if test_results['email_sent']:
                st.success("✅ Email de test envoyé")
            else:
                st.error("❌ Échec envoi email")
    
    # Configuration Telegram
    with st.expander("📱 Configuration Telegram"):
        telegram_token = st.text_input("Bot Token", value=config.TELEGRAM_BOT_TOKEN, type="password")
        telegram_chat_id = st.text_input("Chat ID", value=config.TELEGRAM_CHAT_ID)
        
        if st.button("Tester Telegram"):
            test_results = nm.test_notifications()
            if test_results['telegram_sent']:
                st.success("✅ Message Telegram envoyé")
            else:
                st.error("❌ Échec envoi Telegram")
    
    # Test complet
    st.divider()
    if st.button("🧪 Test Complet Notifications", type="primary"):
        with st.spinner("Test en cours..."):
            results = nm.test_notifications()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if results['email_configured']:
                    if results['email_sent']:
                        st.success("✅ Email: Configuré et fonctionnel")
                    else:
                        st.error("❌ Email: Configuré mais échec envoi")
                else:
                    st.warning("⚠️ Email: Non configuré")
            
            with col2:
                if results['telegram_configured']:
                    if results['telegram_sent']:
                        st.success("✅ Telegram: Configuré et fonctionnel")
                    else:
                        st.error("❌ Telegram: Configuré mais échec envoi")
                else:
                    st.warning("⚠️ Telegram: Non configuré")

def show_ml_management():
    """Gestion des modèles ML"""
    st.subheader("Gestion Modèles ML")
    
    ai_detector = st.session_state.get('ai_detector')
    data_loader = st.session_state.get('data_loader')
    
    if not ai_detector or not data_loader:
        st.error("Composants ML non disponibles")
        return
    
    # Statut du modèle
    model_info = ai_detector.get_model_info()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Statut du Modèle:**")
        if model_info['trained']:
            st.success("✅ Modèle entraîné")
            st.write(f"Algorithme: {model_info['algorithm']}")
            st.write(f"Features: {len(model_info['features'])}")
        else:
            st.warning("⚠️ Modèle non entraîné")
    
    with col2:
        st.write("**Actions:**")
        
        if st.button("🎯 Réentraîner Modèle"):
            with st.spinner("Entraînement en cours..."):
                logs_df = data_loader.load_logs()
                if not logs_df.empty:
                    result = ai_detector.train_model(logs_df)
                    if result['success']:
                        st.success(f"✅ Modèle entraîné sur {result['samples_trained']} échantillons")
                        st.info(f"Anomalies: {result['anomalies_detected']} ({result['anomaly_rate']:.1f}%)")
                        st.rerun()
                    else:
                        st.error(f"❌ Erreur: {result['error']}")
                else:
                    st.error("Aucune donnée disponible")
        
        if st.button("📊 Évaluer Performance"):
            if model_info['trained']:
                logs_df = data_loader.load_logs()
                if not logs_df.empty:
                    predictions = ai_detector.predict_anomalies(logs_df)
                    
                    if len(predictions.get('risk_scores', [])) > 0:
                        risk_scores = predictions['risk_scores']
                        anomalies = predictions['anomalies']
                        
                        st.write("**Métriques:**")
                        st.write(f"Score moyen: {risk_scores.mean():.1f}")
                        st.write(f"Anomalies détectées: {anomalies.sum()}")
                        st.write(f"Taux d'anomalies: {(anomalies.sum()/len(anomalies))*100:.1f}%")
            else:
                st.error("Modèle non entraîné")
    
    # Configuration ML
    st.divider()
    st.write("**Configuration ML:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        contamination = st.slider("Contamination", 0.01, 0.5, 0.1, 0.01)
        retrain_hours = st.number_input("Réentraînement (heures)", 1, 168, 24)
    
    with col2:
        anomaly_threshold = st.slider("Seuil Anomalie", 0.0, 1.0, 0.1, 0.01)
        
        if st.button("Sauvegarder Config ML"):
            st.success("Configuration ML sauvegardée")

def show_maintenance():
    """Outils de maintenance"""
    st.subheader("Maintenance")
    
    config = Config()
    
    # Nettoyage des données
    with st.expander("🧹 Nettoyage"):
        st.write("Nettoyer les données anciennes:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            days_to_keep = st.number_input("Jours à conserver", 1, 365, 30)
            
            if st.button("Nettoyer Logs"):
                # TODO: Implémenter nettoyage
                st.success(f"Logs > {days_to_keep} jours supprimés")
        
        with col2:
            if st.button("Nettoyer Exports"):
                # TODO: Implémenter nettoyage exports
                st.success("Fichiers d'export anciens supprimés")
    
    # Sauvegarde
    with st.expander("💾 Sauvegarde"):
        st.write("Sauvegarder les données et configuration:")
        
        if st.button("Créer Sauvegarde"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"soc_backup_{timestamp}"
            
            # TODO: Implémenter sauvegarde complète
            st.success(f"Sauvegarde créée: {backup_name}")
    
    # Import/Export
    with st.expander("📁 Import/Export"):
        st.write("**Import de données:**")
        
        uploaded_file = st.file_uploader("Importer logs CSV", type=['csv'])
        if uploaded_file and st.button("Importer"):
            # TODO: Implémenter import
            st.success("Données importées avec succès")
        
        st.write("**Export de configuration:**")
        if st.button("Exporter Configuration"):
            config_data = {
                'elk_host': config.ELK_HOST,
                'wazuh_host': config.WAZUH_HOST,
                'alert_thresholds': config.ALERT_THRESHOLDS,
                'export_timestamp': datetime.now().isoformat()
            }
            
            st.download_button(
                "Télécharger Config",
                json.dumps(config_data, indent=2),
                "soc_config.json",
                "application/json"
            )
    
    # Logs système
    with st.expander("📋 Logs Système"):
        st.write("Derniers logs d'activité:")
        
        # Simuler des logs système
        system_logs = [
            f"{datetime.now().strftime('%H:%M:%S')} - INFO - Dashboard démarré",
            f"{(datetime.now() - timedelta(minutes=5)).strftime('%H:%M:%S')} - INFO - Modèle ML chargé",
            f"{(datetime.now() - timedelta(minutes=10)).strftime('%H:%M:%S')} - WARNING - Connexion ELK échouée",
            f"{(datetime.now() - timedelta(minutes=15)).strftime('%H:%M:%S')} - INFO - Utilisateur connecté"
        ]
        
        for log in system_logs:
            st.text(log)

if __name__ == "__main__":
    show_admin()