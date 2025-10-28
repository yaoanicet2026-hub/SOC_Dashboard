"""
SOC Dashboard - Version simplifiée pour Streamlit Cloud
Auteur: Yao Kouakou Luc Anicet Béranger
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import json
from pathlib import Path

# Import des fonctionnalités avancées
try:
    from advanced_features import show_advanced_features
except ImportError:
    def show_advanced_features():
        return False

try:
    from real_time_features import show_realtime_features
except ImportError:
    def show_realtime_features():
        return False

# Configuration de la page
st.set_page_config(
    page_title="SOC Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentification simple
def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Connexion SOC Dashboard")
        with st.form("login"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter"):
                if username == "admin" and password == "admin":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
        return False
    return True

# Données par défaut
@st.cache_data
def load_sample_data():
    logs = pd.DataFrame([
        {
            "timestamp": datetime.now() - timedelta(minutes=i),
            "src_ip": f"192.168.1.{100+i%50}",
            "dst_ip": "10.0.0.1",
            "event_type": ["web_request", "ssh_login", "port_scan", "dns_query"][i%4],
            "severity": ["low", "medium", "high", "critical"][i%4],
            "bytes_in": np.random.randint(100, 10000),
            "bytes_out": np.random.randint(50, 5000)
        } for i in range(100)
    ])
    
    vulns = pd.DataFrame([
        {
            "cve_id": f"CVE-2024-000{i}",
            "host": f"host-0{i%5+1}",
            "cvss_score": np.random.uniform(4.0, 10.0),
            "severity": ["low", "medium", "high", "critical"][i%4],
            "status": ["open", "patched", "in_progress"][i%3]
        } for i in range(20)
    ])
    
    return logs, vulns

def show_dashboard():
    st.header("🏠 Dashboard Principal")
    
    logs_df, vulns_df = load_sample_data()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Alertes", len(logs_df))
    with col2:
        critical = len(logs_df[logs_df['severity'] == 'critical'])
        st.metric("Critiques", critical)
    with col3:
        st.metric("MTTD", "15 min")
    with col4:
        st.metric("MTTR", "120 min")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        severity_counts = logs_df['severity'].value_counts()
        fig = px.pie(values=severity_counts.values, names=severity_counts.index, 
                    title="Alertes par Sévérité")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        hourly_data = logs_df.groupby(logs_df['timestamp'].dt.hour).size()
        fig = px.bar(x=hourly_data.index, y=hourly_data.values, 
                    title="Alertes par Heure")
        st.plotly_chart(fig, use_container_width=True)
    
    # Table récente
    st.subheader("🚨 Incidents Récents")
    recent = logs_df.head(10)[['timestamp', 'src_ip', 'event_type', 'severity']]
    st.dataframe(recent, use_container_width=True)

def show_threats():
    st.header("⚠️ Menaces & Anomalies")
    
    logs_df, _ = load_sample_data()
    
    # Simulation ML
    risk_scores = np.random.uniform(0, 100, len(logs_df))
    logs_df['risk_score'] = risk_scores
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Anomalies Détectées", len(logs_df[risk_scores > 70]))
    with col2:
        st.metric("Score Moyen", f"{risk_scores.mean():.1f}")
    with col3:
        st.metric("Haut Risque", len(logs_df[risk_scores > 80]))
    
    # Distribution des scores
    fig = px.histogram(x=risk_scores, title="Distribution Scores de Risque")
    st.plotly_chart(fig, use_container_width=True)
    
    # Top anomalies
    st.subheader("🚨 Top Anomalies")
    high_risk = logs_df[risk_scores > 70].sort_values('risk_score', ascending=False)
    st.dataframe(high_risk[['timestamp', 'src_ip', 'event_type', 'risk_score']], 
                use_container_width=True)

def show_network():
    st.header("🌐 Réseau & Trafic")
    
    logs_df, _ = load_sample_data()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Connexions", len(logs_df))
    with col2:
        st.metric("IPs Uniques", logs_df['src_ip'].nunique())
    with col3:
        st.metric("Volume Total", f"{logs_df['bytes_in'].sum()/1024:.1f} KB")
    with col4:
        st.metric("Protocoles", 3)
    
    # Top IPs
    col1, col2 = st.columns(2)
    
    with col1:
        top_ips = logs_df['src_ip'].value_counts().head(10)
        fig = px.bar(x=top_ips.values, y=top_ips.index, orientation='h',
                    title="Top IPs Sources")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        event_counts = logs_df['event_type'].value_counts()
        fig = px.pie(values=event_counts.values, names=event_counts.index,
                    title="Types d'Événements")
        st.plotly_chart(fig, use_container_width=True)

def show_vulns():
    st.header("🔍 Vulnérabilités")
    
    _, vulns_df = load_sample_data()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", len(vulns_df))
    with col2:
        critical = len(vulns_df[vulns_df['cvss_score'] >= 9.0])
        st.metric("Critiques", critical)
    with col3:
        patched = len(vulns_df[vulns_df['status'] == 'patched'])
        st.metric("Patchées", patched)
    with col4:
        rate = (patched / len(vulns_df)) * 100
        st.metric("Taux Patch", f"{rate:.1f}%")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        severity_counts = vulns_df['severity'].value_counts()
        fig = px.pie(values=severity_counts.values, names=severity_counts.index,
                    title="Vulnérabilités par Sévérité")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(vulns_df, x='cvss_score', title="Distribution CVSS")
        st.plotly_chart(fig, use_container_width=True)
    
    # Table
    st.subheader("📋 Liste des Vulnérabilités")
    st.dataframe(vulns_df, use_container_width=True)

def show_incidents():
    st.header("📋 Gestion des Incidents")
    
    # Tickets simulés
    tickets = [
        {"id": "INC-001", "title": "SSH Bruteforce détecté", "severity": "high", "status": "open"},
        {"id": "INC-002", "title": "Port scan activité", "severity": "medium", "status": "in_progress"},
        {"id": "INC-003", "title": "Malware détecté", "severity": "critical", "status": "resolved"}
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", len(tickets))
    with col2:
        open_tickets = len([t for t in tickets if t['status'] == 'open'])
        st.metric("Ouverts", open_tickets)
    with col3:
        st.metric("MTTD", "15 min")
    with col4:
        st.metric("MTTR", "120 min")
    
    # Table des tickets
    st.subheader("🎫 Tickets Actifs")
    df_tickets = pd.DataFrame(tickets)
    st.dataframe(df_tickets, use_container_width=True)

def show_logs():
    st.header("📊 Visualiseur de Logs")
    
    logs_df, _ = load_sample_data()
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        severity_filter = st.selectbox("Sévérité", ['Tous'] + list(logs_df['severity'].unique()))
    with col2:
        event_filter = st.selectbox("Type", ['Tous'] + list(logs_df['event_type'].unique()))
    
    # Appliquer filtres
    filtered_logs = logs_df.copy()
    if severity_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['severity'] == severity_filter]
    if event_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['event_type'] == event_filter]
    
    st.info(f"📊 {len(filtered_logs)} logs trouvés")
    st.dataframe(filtered_logs, use_container_width=True)

def main():
    if not check_auth():
        return
    
    st.title("🛡️ SOC Dashboard")
    st.markdown("**Auteur**: Yao Kouakou Luc Anicet Béranger")
    
    # Navigation
    st.sidebar.title("Navigation")
    
    if st.sidebar.button("🚪 Déconnexion"):
        st.session_state.authenticated = False
        st.rerun()
    
    pages = {
        "🏠 Dashboard": show_dashboard,
        "⚠️ Menaces": show_threats,
        "🌐 Réseau": show_network,
        "🔍 Vulnérabilités": show_vulns,
        "📋 Incidents": show_incidents,
        "📊 Logs": show_logs
    }
    
    selected = st.sidebar.selectbox("Page", list(pages.keys()))
    
    # Vérifier si une fonctionnalité avancée ou temps réel est sélectionnée
    if not show_advanced_features() and not show_realtime_features():
        pages[selected]()

if __name__ == "__main__":
    main()