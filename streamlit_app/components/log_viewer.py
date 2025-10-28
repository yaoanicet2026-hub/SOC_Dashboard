"""
Log Viewer - Visualiseur de logs avec recherche
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

def show_log_viewer():
    st.header("📊 Visualiseur de Logs")
    
    data_loader = st.session_state.data_loader
    logs_df = data_loader.load_logs()
    
    if logs_df.empty:
        st.warning("Aucun log disponible")
        return
    
    # Statistiques générales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Logs", len(logs_df))
    
    with col2:
        unique_ips = logs_df['src_ip'].nunique()
        st.metric("IPs Uniques", unique_ips)
    
    with col3:
        unique_events = logs_df['event_type'].nunique()
        st.metric("Types d'Événements", unique_events)
    
    with col4:
        recent_logs = len(logs_df[logs_df['timestamp'] >= datetime.now() - timedelta(hours=1)])
        st.metric("Logs (1h)", recent_logs)
    
    st.divider()
    
    # Filtres de recherche
    st.subheader("🔍 Recherche et Filtres")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_text = st.text_input("Recherche full-text", placeholder="IP, utilisateur, hash...")
        
    with col2:
        event_filter = st.selectbox(
            "Type d'événement",
            ['Tous'] + list(logs_df['event_type'].unique())
        )
    
    with col3:
        severity_filter = st.selectbox(
            "Sévérité",
            ['Tous'] + list(logs_df['severity'].unique())
        )
    
    # Filtres temporels
    col1, col2 = st.columns(2)
    
    with col1:
        date_from = st.date_input("Date début", value=datetime.now().date() - timedelta(days=1))
    
    with col2:
        date_to = st.date_input("Date fin", value=datetime.now().date())
    
    # Appliquer les filtres
    filtered_logs = logs_df.copy()
    
    # Filtre texte
    if search_text:
        mask = (
            filtered_logs['src_ip'].str.contains(search_text, case=False, na=False) |
            filtered_logs['dst_ip'].str.contains(search_text, case=False, na=False) |
            filtered_logs['username'].str.contains(search_text, case=False, na=False) |
            filtered_logs['host'].str.contains(search_text, case=False, na=False) |
            filtered_logs['event_type'].str.contains(search_text, case=False, na=False)
        )
        filtered_logs = filtered_logs[mask]
    
    # Filtre événement
    if event_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['event_type'] == event_filter]
    
    # Filtre sévérité
    if severity_filter != 'Tous':
        filtered_logs = filtered_logs[filtered_logs['severity'] == severity_filter]
    
    # Filtre temporel
    filtered_logs = filtered_logs[
        (filtered_logs['timestamp'].dt.date >= date_from) &
        (filtered_logs['timestamp'].dt.date <= date_to)
    ]
    
    st.info(f"📊 {len(filtered_logs)} logs trouvés (sur {len(logs_df)} total)")
    
    st.divider()
    
    # Options d'affichage
    col1, col2, col3 = st.columns(3)
    
    with col1:
        page_size = st.selectbox("Logs par page", [25, 50, 100, 200], index=1)
    
    with col2:
        sort_column = st.selectbox("Trier par", ['timestamp', 'severity', 'src_ip', 'event_type'])
    
    with col3:
        sort_order = st.selectbox("Ordre", ['Décroissant', 'Croissant'])
    
    # Pagination
    if len(filtered_logs) > 0:
        total_pages = (len(filtered_logs) - 1) // page_size + 1
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            page = st.selectbox(f"Page (1-{total_pages})", range(1, total_pages + 1))
        
        # Trier et paginer
        ascending = sort_order == 'Croissant'
        sorted_logs = filtered_logs.sort_values(sort_column, ascending=ascending)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_logs = sorted_logs.iloc[start_idx:end_idx]
        
        # Affichage des logs
        st.subheader(f"📋 Logs (Page {page}/{total_pages})")
        
        # Mode d'affichage
        display_mode = st.radio("Mode d'affichage", ['Table', 'JSON Raw'], horizontal=True)
        
        if display_mode == 'Table':
            # Formatage conditionnel pour la sévérité
            def color_severity(val):
                colors = {
                    'critical': 'background-color: #ff4444; color: white',
                    'high': 'background-color: #ff8800; color: white',
                    'medium': 'background-color: #ffcc00; color: black',
                    'low': 'background-color: #44ff44; color: black'
                }
                return colors.get(val, '')
            
            # Colonnes à afficher
            display_columns = ['timestamp', 'src_ip', 'dst_ip', 'event_type', 'severity', 'username', 'host']
            
            styled_logs = page_logs[display_columns].style.applymap(
                color_severity, subset=['severity']
            )
            
            st.dataframe(styled_logs, use_container_width=True)
            
        else:  # Mode JSON Raw
            st.subheader("🔧 Mode DEBUG - JSON Raw")
            
            for idx, row in page_logs.iterrows():
                with st.expander(f"Log {idx} - {row['timestamp']} - {row['event_type']}"):
                    log_json = row.to_dict()
                    # Convertir timestamp en string pour JSON
                    log_json['timestamp'] = str(log_json['timestamp'])
                    st.json(log_json)
        
        # Actions sur les logs sélectionnés
        st.divider()
        st.subheader("⚡ Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📥 Exporter CSV"):
                csv = filtered_logs.to_csv(index=False)
                st.download_button(
                    "Télécharger CSV",
                    csv,
                    f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )
        
        with col2:
            if st.button("📄 Exporter JSON"):
                json_data = filtered_logs.to_json(orient='records', date_format='iso')
                st.download_button(
                    "Télécharger JSON",
                    json_data,
                    f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json"
                )
        
        with col3:
            if st.button("🚨 Créer Alerte"):
                st.success("Règle d'alerte créée pour ces critères!")
                # TODO: Implémenter création de règle
        
        with col4:
            if st.button("🎫 Créer Incident"):
                st.success("Ticket d'incident créé!")
                # TODO: Rediriger vers page incidents
        
        # Statistiques sur les logs filtrés
        if len(filtered_logs) > 0:
            st.divider()
            st.subheader("📈 Statistiques des Logs Filtrés")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top 5 IPs Sources:**")
                top_src_ips = filtered_logs['src_ip'].value_counts().head(5)
                for ip, count in top_src_ips.items():
                    st.write(f"• {ip}: {count} logs")
            
            with col2:
                st.write("**Top 5 Types d'Événements:**")
                top_events = filtered_logs['event_type'].value_counts().head(5)
                for event, count in top_events.items():
                    st.write(f"• {event}: {count} logs")
    
    else:
        st.info("Aucun log ne correspond aux critères de recherche")