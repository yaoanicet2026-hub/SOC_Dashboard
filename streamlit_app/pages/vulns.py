"""
Page Vulnérabilités - Gestion des CVE et patches
"""

import streamlit as st
import plotly.express as px
import pandas as pd

def show_vulns():
    st.header("🔍 Gestion des Vulnérabilités")
    
    data_loader = st.session_state.data_loader
    vulns_df = data_loader.load_vulnerabilities()
    
    if vulns_df.empty:
        st.warning("Aucune donnée de vulnérabilité disponible")
        return
    
    # KPIs vulnérabilités
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vulns = len(vulns_df)
        st.metric("Total Vulnérabilités", total_vulns)
    
    with col2:
        critical_vulns = len(vulns_df[vulns_df['cvss_score'] >= 9.0])
        st.metric("Critiques (CVSS ≥9)", critical_vulns)
    
    with col3:
        patched = len(vulns_df[vulns_df['status'] == 'patched'])
        patch_rate = (patched / total_vulns) * 100 if total_vulns > 0 else 0
        st.metric("Taux de Patch", f"{patch_rate:.1f}%")
    
    with col4:
        open_vulns = len(vulns_df[vulns_df['status'] == 'open'])
        st.metric("Non Résolues", open_vulns)
    
    st.divider()
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Répartition par Sévérité")
        
        severity_counts = vulns_df['severity'].value_counts()
        
        fig_severity = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title="Distribution par Sévérité",
            color_discrete_map={
                'critical': '#ff4444',
                'high': '#ff8800',
                'medium': '#ffcc00',
                'low': '#44ff44'
            }
        )
        fig_severity.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        st.subheader("Status des Vulnérabilités")
        
        status_counts = vulns_df['status'].value_counts()
        
        fig_status = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title="État des Vulnérabilités",
            color=status_counts.values,
            color_continuous_scale='RdYlGn_r'
        )
        fig_status.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Distribution CVSS
    st.subheader("Distribution des Scores CVSS")
    
    fig_cvss = px.histogram(
        vulns_df,
        x='cvss_score',
        nbins=20,
        title="Distribution des Scores CVSS",
        color_discrete_sequence=['#00ff88']
    )
    fig_cvss.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_cvss, use_container_width=True)
    
    st.divider()
    
    # Filtres et table
    st.subheader("📋 Liste des Vulnérabilités")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        host_filter = st.selectbox(
            "Filtrer par Hôte",
            ['Tous'] + list(vulns_df['host'].unique())
        )
    
    with col2:
        severity_filter = st.selectbox(
            "Filtrer par Sévérité",
            ['Tous'] + list(vulns_df['severity'].unique())
        )
    
    with col3:
        status_filter = st.selectbox(
            "Filtrer par Status",
            ['Tous'] + list(vulns_df['status'].unique())
        )
    
    with col4:
        cvss_min = st.slider("Score CVSS Minimum", 0.0, 10.0, 0.0, 0.1)
    
    # Appliquer les filtres
    filtered_vulns = vulns_df.copy()
    
    if host_filter != 'Tous':
        filtered_vulns = filtered_vulns[filtered_vulns['host'] == host_filter]
    
    if severity_filter != 'Tous':
        filtered_vulns = filtered_vulns[filtered_vulns['severity'] == severity_filter]
    
    if status_filter != 'Tous':
        filtered_vulns = filtered_vulns[filtered_vulns['status'] == status_filter]
    
    filtered_vulns = filtered_vulns[filtered_vulns['cvss_score'] >= cvss_min]
    
    # Affichage de la table
    if not filtered_vulns.empty:
        # Formatage conditionnel
        def color_severity(val):
            colors = {
                'critical': 'background-color: #ff4444; color: white',
                'high': 'background-color: #ff8800; color: white',
                'medium': 'background-color: #ffcc00; color: black',
                'low': 'background-color: #44ff44; color: black'
            }
            return colors.get(val, '')
        
        def color_status(val):
            colors = {
                'open': 'background-color: #ff6666; color: white',
                'in_progress': 'background-color: #ffaa66; color: black',
                'patched': 'background-color: #66ff66; color: black'
            }
            return colors.get(val, '')
        
        def color_cvss(val):
            if val >= 9.0:
                return 'background-color: #ff4444; color: white'
            elif val >= 7.0:
                return 'background-color: #ff8800; color: white'
            elif val >= 4.0:
                return 'background-color: #ffcc00; color: black'
            else:
                return 'background-color: #44ff44; color: black'
        
        styled_vulns = filtered_vulns.style.applymap(
            color_severity, subset=['severity']
        ).applymap(
            color_status, subset=['status']
        ).applymap(
            color_cvss, subset=['cvss_score']
        )
        
        st.dataframe(styled_vulns, use_container_width=True)
        
        # Actions en lot
        st.subheader("⚡ Actions Rapides")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Marquer comme Patchées"):
                st.success("Vulnérabilités marquées comme patchées!")
                # TODO: Implémenter mise à jour status
        
        with col2:
            if st.button("🔄 Marquer en Cours"):
                st.info("Vulnérabilités marquées en cours de traitement!")
        
        with col3:
            if st.button("📥 Exporter CSV"):
                csv = filtered_vulns.to_csv(index=False)
                st.download_button(
                    "Télécharger CSV",
                    csv,
                    "vulnerabilities.csv",
                    "text/csv"
                )
        
        # Détails d'une vulnérabilité
        st.divider()
        st.subheader("🔍 Détails Vulnérabilité")
        
        selected_cve = st.selectbox(
            "Sélectionner une CVE",
            filtered_vulns['cve_id'].tolist()
        )
        
        if selected_cve:
            vuln_details = filtered_vulns[filtered_vulns['cve_id'] == selected_cve].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**CVE ID:** {vuln_details['cve_id']}")
                st.write(f"**Hôte:** {vuln_details['host']}")
                st.write(f"**Service:** {vuln_details['service']}")
                st.write(f"**Score CVSS:** {vuln_details['cvss_score']}")
            
            with col2:
                st.write(f"**Sévérité:** {vuln_details['severity']}")
                st.write(f"**Status:** {vuln_details['status']}")
                st.write(f"**Patch Disponible:** {'Oui' if vuln_details['patch_available'] else 'Non'}")
                st.write(f"**Découverte:** {vuln_details['discovered_date']}")
            
            st.write(f"**Description:** {vuln_details['description']}")
            
            # Actions sur la vulnérabilité
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔧 Assigner Ticket"):
                    st.success(f"Ticket créé pour {selected_cve}")
            
            with col2:
                if st.button("📋 Voir Playbook"):
                    st.info("Redirection vers le playbook de remediation")
            
            with col3:
                if st.button("🔗 Lien CVE"):
                    st.info(f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={selected_cve}")
    
    else:
        st.info("Aucune vulnérabilité correspondant aux filtres")