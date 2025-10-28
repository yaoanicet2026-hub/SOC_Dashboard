"""
Page Réseau & Trafic - Analyse du trafic réseau
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def show_network():
    st.header("🌐 Réseau & Trafic")
    
    data_loader = st.session_state.data_loader
    logs_df = data_loader.load_logs()
    network_stats = data_loader.get_network_stats()
    
    if logs_df.empty:
        st.warning("Aucune donnée réseau disponible")
        return
    
    # KPIs réseau
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_connections = len(logs_df)
        st.metric("Connexions Totales", f"{total_connections:,}")
    
    with col2:
        unique_ips = logs_df['src_ip'].nunique()
        st.metric("IPs Uniques", unique_ips)
    
    with col3:
        total_bytes = network_stats.get('total_bytes_in', 0) + network_stats.get('total_bytes_out', 0)
        st.metric("Volume Total", f"{total_bytes/1024/1024:.1f} MB")
    
    with col4:
        protocols = len(network_stats.get('protocols', {}))
        st.metric("Protocoles", protocols)
    
    st.divider()
    
    # Graphiques réseau
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 IPs Sources")
        
        if network_stats.get('top_src_ips'):
            top_src = pd.DataFrame(
                list(network_stats['top_src_ips'].items()),
                columns=['IP', 'Connexions']
            ).head(10)
            
            fig_src = px.bar(
                top_src,
                x='Connexions',
                y='IP',
                orientation='h',
                title="Sources les plus actives",
                color='Connexions',
                color_continuous_scale='Reds'
            )
            fig_src.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_src, use_container_width=True)
        else:
            st.info("Aucune donnée IP source")
    
    with col2:
        st.subheader("Top 10 IPs Destinations")
        
        if network_stats.get('top_dst_ips'):
            top_dst = pd.DataFrame(
                list(network_stats['top_dst_ips'].items()),
                columns=['IP', 'Connexions']
            ).head(10)
            
            fig_dst = px.bar(
                top_dst,
                x='Connexions',
                y='IP',
                orientation='h',
                title="Destinations les plus ciblées",
                color='Connexions',
                color_continuous_scale='Blues'
            )
            fig_dst.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_dst, use_container_width=True)
        else:
            st.info("Aucune donnée IP destination")
    
    # Protocoles et ports
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Répartition par Protocole")
        
        if network_stats.get('protocols'):
            protocols_df = pd.DataFrame(
                list(network_stats['protocols'].items()),
                columns=['Protocole', 'Nombre']
            )
            
            fig_proto = px.pie(
                protocols_df,
                values='Nombre',
                names='Protocole',
                title="Distribution des Protocoles"
            )
            fig_proto.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_proto, use_container_width=True)
        else:
            st.info("Aucune donnée protocole")
    
    with col2:
        st.subheader("Ports les Plus Utilisés")
        
        port_counts = logs_df['dst_port'].value_counts().head(10)
        
        if not port_counts.empty:
            fig_ports = px.bar(
                x=port_counts.index.astype(str),
                y=port_counts.values,
                title="Top 10 Ports Destination",
                labels={'x': 'Port', 'y': 'Connexions'},
                color=port_counts.values,
                color_continuous_scale='Viridis'
            )
            fig_ports.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_ports, use_container_width=True)
        else:
            st.info("Aucune donnée port")
    
    st.divider()
    
    # Graphique de flux réseau
    st.subheader("🔗 Graphique de Flux Réseau")
    
    # Créer un graphique de réseau simplifié
    if len(logs_df) > 0:
        # Prendre les connexions les plus fréquentes
        connections = logs_df.groupby(['src_ip', 'dst_ip']).size().reset_index(name='count')
        top_connections = connections.nlargest(20, 'count')
        
        # Créer les nœuds
        all_ips = set(top_connections['src_ip'].tolist() + top_connections['dst_ip'].tolist())
        
        # Graphique réseau avec Plotly
        fig_network = go.Figure()
        
        # Ajouter les connexions comme lignes
        for _, row in top_connections.iterrows():
            # Position simulée des IPs (en réalité, utiliser un algorithme de layout)
            src_pos = hash(row['src_ip']) % 100
            dst_pos = hash(row['dst_ip']) % 100
            
            fig_network.add_trace(go.Scatter(
                x=[src_pos, dst_pos],
                y=[src_pos % 50, dst_pos % 50],
                mode='lines',
                line=dict(width=row['count']/10, color='rgba(0,255,136,0.6)'),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Ajouter les nœuds IP
        for ip in list(all_ips)[:15]:  # Limiter pour la lisibilité
            pos_x = hash(ip) % 100
            pos_y = hash(ip) % 50
            
            fig_network.add_trace(go.Scatter(
                x=[pos_x],
                y=[pos_y],
                mode='markers+text',
                marker=dict(size=15, color='#ff4444'),
                text=ip.split('.')[-1],  # Afficher seulement le dernier octet
                textposition='middle center',
                showlegend=False,
                hovertext=ip
            ))
        
        fig_network.update_layout(
            title="Flux de Connexions Réseau",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        
        st.plotly_chart(fig_network, use_container_width=True)
    
    # Table détaillée
    st.divider()
    st.subheader("📊 Détails des Connexions")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        protocol_filter = st.selectbox(
            "Filtrer par Protocole",
            ['Tous'] + list(logs_df['protocol'].unique())
        )
    
    with col2:
        severity_filter = st.selectbox(
            "Filtrer par Sévérité", 
            ['Tous'] + list(logs_df['severity'].unique())
        )
    
    with col3:
        limit = st.number_input("Nombre de lignes", min_value=10, max_value=1000, value=50)
    
    # Appliquer les filtres
    filtered_df = logs_df.copy()
    
    if protocol_filter != 'Tous':
        filtered_df = filtered_df[filtered_df['protocol'] == protocol_filter]
    
    if severity_filter != 'Tous':
        filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
    
    # Afficher la table
    display_cols = ['timestamp', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol', 'bytes_in', 'bytes_out', 'severity']
    
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[display_cols].head(limit),
            use_container_width=True
        )
        
        # Export
        if st.button("📥 Exporter Données Réseau"):
            csv = filtered_df[display_cols].to_csv(index=False)
            st.download_button(
                "Télécharger CSV",
                csv,
                "network_data.csv",
                "text/csv"
            )
    else:
        st.info("Aucune donnée correspondant aux filtres")