"""
Page Menaces & Anomalies - Détection ML
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def show_threats():
    st.header("⚠️ Menaces & Anomalies")
    
    data_loader = st.session_state.data_loader
    ai_detector = st.session_state.ai_detector
    
    # Status du modèle ML
    col1, col2 = st.columns([2, 1])
    
    with col1:
        model_info = ai_detector.get_model_info()
        if model_info['trained']:
            st.success("✅ Modèle ML entraîné et prêt")
            st.info(f"Algorithme: {model_info['algorithm']}")
        else:
            st.warning("⚠️ Modèle non entraîné")
    
    with col2:
        if st.button("🎯 Entraîner Modèle", type="primary"):
            with st.spinner("Entraînement en cours..."):
                logs_df = data_loader.load_logs()
                if not logs_df.empty:
                    result = ai_detector.train_model(logs_df)
                    if result['success']:
                        st.success(f"✅ Modèle entraîné sur {result['samples_trained']} échantillons")
                        st.info(f"Anomalies détectées: {result['anomalies_detected']} ({result['anomaly_rate']:.1f}%)")
                        st.rerun()
                    else:
                        st.error(f"❌ Erreur: {result['error']}")
                else:
                    st.error("Aucune donnée disponible")
    
    st.divider()
    
    # Analyse des anomalies
    logs_df = data_loader.load_logs()
    
    if not logs_df.empty and ai_detector.is_model_trained():
        st.subheader("🔍 Détection d'Anomalies")
        
        # Prédictions
        predictions = ai_detector.predict_anomalies(logs_df)
        
        if len(predictions.get('risk_scores', [])) > 0:
            # Ajouter scores aux données
            logs_with_scores = logs_df.copy()
            logs_with_scores['risk_score'] = predictions['risk_scores']
            logs_with_scores['is_anomaly'] = predictions['anomalies']
            
            # Métriques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_anomalies = np.sum(predictions['anomalies'])
                st.metric("Anomalies Détectées", total_anomalies)
            
            with col2:
                avg_risk = np.mean(predictions['risk_scores'])
                st.metric("Score Risque Moyen", f"{avg_risk:.1f}")
            
            with col3:
                high_risk = np.sum(predictions['risk_scores'] > 70)
                st.metric("Haut Risque (>70)", high_risk)
            
            # Graphique distribution des scores
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Distribution Scores de Risque")
                fig_hist = px.histogram(
                    x=predictions['risk_scores'],
                    nbins=20,
                    title="Distribution des Scores",
                    color_discrete_sequence=['#00ff88']
                )
                fig_hist.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                st.subheader("Anomalies par Type d'Événement")
                anomaly_data = logs_with_scores[logs_with_scores['is_anomaly']]
                if not anomaly_data.empty:
                    event_counts = anomaly_data['event_type'].value_counts()
                    fig_events = px.bar(
                        x=event_counts.index,
                        y=event_counts.values,
                        title="Types d'Événements Anormaux",
                        color_discrete_sequence=['#ff4444']
                    )
                    fig_events.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_events, use_container_width=True)
                else:
                    st.info("Aucune anomalie détectée")
            
            # Table des anomalies
            st.subheader("🚨 Top Anomalies")
            
            high_risk_data = logs_with_scores[logs_with_scores['risk_score'] > 50].sort_values('risk_score', ascending=False)
            
            if not high_risk_data.empty:
                display_cols = ['timestamp', 'src_ip', 'dst_ip', 'event_type', 'risk_score', 'severity']
                display_data = high_risk_data[display_cols].head(20)
                
                # Formatage conditionnel
                def color_risk_score(val):
                    if val > 80:
                        return 'background-color: #ff4444; color: white'
                    elif val > 60:
                        return 'background-color: #ff8800; color: white'
                    elif val > 40:
                        return 'background-color: #ffcc00; color: black'
                    else:
                        return 'background-color: #44ff44; color: black'
                
                styled_data = display_data.style.applymap(color_risk_score, subset=['risk_score'])
                st.dataframe(styled_data, use_container_width=True)
                
                # Export
                if st.button("📥 Exporter Anomalies CSV"):
                    csv = display_data.to_csv(index=False)
                    st.download_button(
                        "Télécharger CSV",
                        csv,
                        "anomalies.csv",
                        "text/csv"
                    )
            else:
                st.info("Aucune anomalie à haut risque")
        else:
            st.warning("Impossible de calculer les scores de risque")
    
    elif logs_df.empty:
        st.warning("Aucune donnée disponible pour l'analyse")
    else:
        st.info("Entraînez d'abord le modèle ML pour détecter les anomalies")
    
    # Alertes actives
    st.divider()
    st.subheader("🔔 Alertes Actives")
    
    alert_manager = st.session_state.alert_manager
    recent_alerts = alert_manager.check_alerts(logs_df)
    
    if recent_alerts:
        for alert in recent_alerts:
            severity_color = {
                'critical': '🔴',
                'high': '🟠', 
                'medium': '🟡',
                'low': '🟢'
            }
            
            st.warning(f"{severity_color.get(alert['severity'], '⚪')} **{alert['rule_name']}** - {alert['message']}")
    else:
        st.success("✅ Aucune alerte active")