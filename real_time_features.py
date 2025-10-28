"""
Fonctionnalités temps réel pour SOC Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

def show_real_time_monitoring():
    """Monitoring temps réel"""
    st.header("⚡ Monitoring Temps Réel")
    
    # Auto-refresh
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=True)
    
    if auto_refresh:
        # Placeholder pour les métriques temps réel
        placeholder = st.empty()
        
        # Simulation de données temps réel
        while auto_refresh:
            with placeholder.container():
                # KPIs temps réel
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    current_alerts = np.random.randint(15, 25)
                    st.metric("Alertes Actives", current_alerts, 
                             delta=np.random.randint(-3, 5))
                
                with col2:
                    cpu_usage = np.random.randint(45, 85)
                    st.metric("CPU Usage", f"{cpu_usage}%",
                             delta=f"{np.random.randint(-5, 5)}%")
                
                with col3:
                    network_traffic = np.random.randint(800, 1200)
                    st.metric("Trafic Réseau", f"{network_traffic} MB/s",
                             delta=f"{np.random.randint(-50, 100)} MB/s")
                
                with col4:
                    threat_level = np.random.choice(["Low", "Medium", "High"])
                    color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                    st.metric("Niveau Menace", f"{color[threat_level]} {threat_level}")
                
                # Graphique temps réel
                st.subheader("📈 Activité en Temps Réel")
                
                # Générer données pour les 60 dernières minutes
                times = [datetime.now() - timedelta(minutes=i) for i in range(60, 0, -1)]
                values = [max(0, 10 + 5 * np.sin(i/10) + np.random.normal(0, 2)) for i in range(60)]
                
                df_realtime = pd.DataFrame({
                    'Time': times,
                    'Alerts': values
                })
                
                fig = px.line(df_realtime, x='Time', y='Alerts',
                             title="Alertes par Minute (Dernière Heure)")
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # Log d'activité temps réel
                st.subheader("📋 Log d'Activité")
                
                recent_events = [
                    f"{datetime.now().strftime('%H:%M:%S')} - Nouvelle connexion SSH depuis 203.0.113.45",
                    f"{(datetime.now() - timedelta(seconds=30)).strftime('%H:%M:%S')} - Scan de ports détecté sur 192.168.1.100",
                    f"{(datetime.now() - timedelta(minutes=1)).strftime('%H:%M:%S')} - Tentative de login échouée pour admin",
                    f"{(datetime.now() - timedelta(minutes=2)).strftime('%H:%M:%S')} - Trafic suspect vers domaine malveillant"
                ]
                
                for event in recent_events:
                    st.text(event)
            
            # Attendre 30 secondes avant le prochain refresh
            time.sleep(30)
            st.rerun()
    
    else:
        st.info("Auto-refresh désactivé. Cochez la case pour activer le monitoring temps réel.")

def show_alert_center():
    """Centre d'alertes avancé"""
    st.header("🚨 Centre d'Alertes")
    
    # Filtres d'alertes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        severity_filter = st.multiselect("Sévérité", 
                                       ["Critical", "High", "Medium", "Low"],
                                       default=["Critical", "High"])
    
    with col2:
        status_filter = st.multiselect("Statut",
                                     ["New", "Acknowledged", "In Progress", "Resolved"],
                                     default=["New", "Acknowledged"])
    
    with col3:
        time_filter = st.selectbox("Période", 
                                 ["Dernière heure", "Dernières 24h", "Dernière semaine"])
    
    # Génération d'alertes simulées
    alerts_data = []
    for i in range(50):
        alert = {
            'ID': f"ALT-{i:04d}",
            'Timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, 1440)),
            'Severity': np.random.choice(["Critical", "High", "Medium", "Low"]),
            'Status': np.random.choice(["New", "Acknowledged", "In Progress", "Resolved"]),
            'Source': f"192.168.1.{np.random.randint(1, 254)}",
            'Rule': np.random.choice([
                "SSH Brute Force", "Port Scan", "Malware Detection", 
                "Suspicious DNS", "Data Exfiltration"
            ]),
            'Description': f"Alert description {i}"
        }
        alerts_data.append(alert)
    
    alerts_df = pd.DataFrame(alerts_data)
    
    # Appliquer les filtres
    if severity_filter:
        alerts_df = alerts_df[alerts_df['Severity'].isin(severity_filter)]
    if status_filter:
        alerts_df = alerts_df[alerts_df['Status'].isin(status_filter)]
    
    # Statistiques des alertes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Alertes", len(alerts_df))
    with col2:
        critical_count = len(alerts_df[alerts_df['Severity'] == 'Critical'])
        st.metric("Critiques", critical_count)
    with col3:
        new_count = len(alerts_df[alerts_df['Status'] == 'New'])
        st.metric("Nouvelles", new_count)
    with col4:
        avg_age = np.random.randint(15, 120)
        st.metric("Âge Moyen", f"{avg_age} min")
    
    # Graphique de distribution
    col1, col2 = st.columns(2)
    
    with col1:
        severity_dist = alerts_df['Severity'].value_counts()
        fig = px.pie(values=severity_dist.values, names=severity_dist.index,
                    title="Distribution par Sévérité")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        rule_dist = alerts_df['Rule'].value_counts().head(5)
        fig = px.bar(x=rule_dist.values, y=rule_dist.index, orientation='h',
                    title="Top 5 Règles Déclenchées")
        st.plotly_chart(fig, use_container_width=True)
    
    # Table des alertes avec actions
    st.subheader("📋 Liste des Alertes")
    
    # Sélection d'alertes pour actions en lot
    selected_alerts = st.multiselect("Sélectionner pour actions en lot",
                                   alerts_df['ID'].tolist())
    
    if selected_alerts:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Marquer Résolues"):
                st.success(f"{len(selected_alerts)} alertes marquées comme résolues")
        with col2:
            if st.button("👁️ Marquer Vues"):
                st.info(f"{len(selected_alerts)} alertes marquées comme vues")
        with col3:
            if st.button("🗑️ Supprimer"):
                st.warning(f"{len(selected_alerts)} alertes supprimées")
    
    # Affichage de la table
    st.dataframe(alerts_df.sort_values('Timestamp', ascending=False),
                use_container_width=True)

def show_network_topology():
    """Topologie réseau interactive"""
    st.header("🌐 Topologie Réseau")
    
    # Simulation de données de topologie
    nodes = [
        {"id": "Firewall", "group": "security", "size": 30},
        {"id": "Switch-Core", "group": "network", "size": 25},
        {"id": "Server-Web", "group": "server", "size": 20},
        {"id": "Server-DB", "group": "server", "size": 20},
        {"id": "Workstation-1", "group": "endpoint", "size": 15},
        {"id": "Workstation-2", "group": "endpoint", "size": 15},
        {"id": "Workstation-3", "group": "endpoint", "size": 15},
        {"id": "Router", "group": "network", "size": 25},
        {"id": "DMZ-Server", "group": "server", "size": 20}
    ]
    
    # Matrice de connectivité
    connections = [
        ("Firewall", "Switch-Core", 95),
        ("Switch-Core", "Server-Web", 78),
        ("Switch-Core", "Server-DB", 82),
        ("Switch-Core", "Workstation-1", 45),
        ("Switch-Core", "Workstation-2", 38),
        ("Switch-Core", "Workstation-3", 52),
        ("Firewall", "Router", 88),
        ("Router", "DMZ-Server", 67)
    ]
    
    # Métriques de réseau
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Nœuds Actifs", len(nodes))
    with col2:
        st.metric("Connexions", len(connections))
    with col3:
        avg_utilization = np.mean([conn[2] for conn in connections])
        st.metric("Utilisation Moy.", f"{avg_utilization:.1f}%")
    with col4:
        st.metric("Alertes Réseau", np.random.randint(2, 8))
    
    # Graphique de topologie (simplifié)
    st.subheader("🔗 Carte du Réseau")
    
    # Créer un graphique de réseau avec Plotly
    fig = go.Figure()
    
    # Ajouter les connexions
    for source, target, utilization in connections:
        # Positions simulées des nœuds
        source_pos = hash(source) % 10
        target_pos = hash(target) % 10
        
        fig.add_trace(go.Scatter(
            x=[source_pos, target_pos],
            y=[source_pos % 5, target_pos % 5],
            mode='lines',
            line=dict(width=utilization/20, color=f'rgba(0,255,136,{utilization/100})'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Ajouter les nœuds
    for node in nodes:
        pos_x = hash(node['id']) % 10
        pos_y = hash(node['id']) % 5
        
        color_map = {
            'security': '#ff4444',
            'network': '#4444ff',
            'server': '#44ff44',
            'endpoint': '#ffff44'
        }
        
        fig.add_trace(go.Scatter(
            x=[pos_x],
            y=[pos_y],
            mode='markers+text',
            marker=dict(size=node['size'], color=color_map[node['group']]),
            text=node['id'],
            textposition='middle center',
            showlegend=False,
            hovertext=f"{node['id']} ({node['group']})"
        ))
    
    fig.update_layout(
        title="Topologie Réseau Interactive",
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Table des connexions
    st.subheader("📊 Détails des Connexions")
    
    connections_df = pd.DataFrame(connections, columns=['Source', 'Destination', 'Utilisation %'])
    connections_df['Statut'] = connections_df['Utilisation %'].apply(
        lambda x: '🔴 Critique' if x > 90 else '🟡 Élevé' if x > 70 else '🟢 Normal'
    )
    
    st.dataframe(connections_df, use_container_width=True)

# Fonction principale pour les fonctionnalités temps réel
def show_realtime_features():
    """Affiche les fonctionnalités temps réel"""
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Temps Réel")
    
    realtime_pages = {
        "⚡ Monitoring": show_real_time_monitoring,
        "🚨 Centre Alertes": show_alert_center,
        "🌐 Topologie": show_network_topology
    }
    
    selected_realtime = st.sidebar.selectbox("Fonctions TR", list(realtime_pages.keys()))
    
    if selected_realtime:
        realtime_pages[selected_realtime]()
        return True
    
    return False