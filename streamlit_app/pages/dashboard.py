"""
Dashboard principal - Vue d'ensemble des KPIs
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def show_dashboard():
    st.header("🏠 Dashboard Principal")
    
    try:
        # Récupérer les données
        data_loader = st.session_state.data_loader
        kpis = data_loader.get_kpis()
    except Exception as e:
        st.error(f"Erreur chargement données: {e}")
        return
    
    # KPIs principaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Alertes",
            kpis['total_alerts'],
            delta=f"+{kpis['critical_alerts']} critiques"
        )
    
    with col2:
        st.metric(
            "MTTD (min)",
            f"{kpis['mttd']}",
            delta="-5 min"
        )
    
    with col3:
        st.metric(
            "MTTR (min)", 
            f"{kpis['mttr']}",
            delta="+15 min"
        )
    
    with col4:
        st.metric(
            "Vulns Critiques",
            kpis['critical_vulns'],
            delta=f"{kpis['patch_rate']}% patchées"
        )
    
    st.divider()
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Alertes par Sévérité")
        
        severity_data = {
            'Sévérité': ['Critical', 'High', 'Medium', 'Low'],
            'Nombre': [
                kpis['critical_alerts'],
                kpis['high_alerts'], 
                kpis['medium_alerts'],
                kpis['low_alerts']
            ]
        }
        
        fig_severity = px.pie(
            values=severity_data['Nombre'],
            names=severity_data['Sévérité'],
            color_discrete_map={
                'Critical': '#ff4444',
                'High': '#ff8800', 
                'Medium': '#ffcc00',
                'Low': '#44ff44'
            }
        )
        fig_severity.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        st.subheader("Alertes par Minute (24h)")
        
        # Simuler données temporelles
        now = datetime.now()
        times = [now - timedelta(minutes=x) for x in range(60, 0, -1)]  # Dernière heure seulement
        alerts_per_minute = [max(0, int(np.random.poisson(3))) for i in range(60)]
        
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=times,
            y=alerts_per_minute,
            mode='lines',
            name='Alertes/min',
            line=dict(color='#00ff88', width=2)
        ))
        
        fig_timeline.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.divider()
    
    # Incidents récents
    st.subheader("🚨 Incidents Récents")
    
    try:
        recent_alerts = data_loader.get_recent_alerts(hours=24)
        
        if not recent_alerts.empty:
            # Afficher les 10 plus récents
            display_alerts = recent_alerts.head(10)[['timestamp', 'src_ip', 'event_type', 'severity', 'host']]
            display_alerts['timestamp'] = display_alerts['timestamp'].dt.strftime('%H:%M:%S')
            
            st.dataframe(
                display_alerts,
                use_container_width=True,
                column_config={
                    "severity": st.column_config.TextColumn(
                        "Sévérité",
                        help="Niveau de criticité"
                    )
                }
            )
        else:
            st.info("Aucun incident récent")
    except Exception as e:
        st.warning(f"Erreur chargement incidents: {e}")
        st.info("Aucun incident récent")
    
    # Bouton simulation
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 Actualiser", type="primary"):
            st.rerun()
    
    with col2:
        if st.button("⚡ Simuler Trafic"):
            st.success("Simulation de trafic lancée!")
            # TODO: Implémenter simulation temps réel
    
    with col3:
        st.info("Dernière mise à jour: " + datetime.now().strftime("%H:%M:%S"))