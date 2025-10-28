"""
Fonctionnalités avancées pour SOC Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def show_threat_hunting():
    """Page de threat hunting avancée"""
    st.header("🎯 Threat Hunting")
    
    # Requêtes prédéfinies
    queries = {
        "Connexions suspectes": "src_ip NOT IN (192.168.*, 10.*, 172.16.*)",
        "Activité nocturne": "timestamp BETWEEN 22:00 AND 06:00",
        "Volumes anormaux": "bytes_in > 100000 OR bytes_out > 50000",
        "Ports non standard": "dst_port NOT IN (80, 443, 22, 53, 25)"
    }
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Requêtes Prédéfinies")
        selected_query = st.selectbox("Sélectionner", list(queries.keys()))
        st.code(queries[selected_query])
        
        if st.button("Exécuter Requête"):
            st.success("Requête exécutée - 23 résultats trouvés")
    
    with col2:
        st.subheader("Résultats de Hunting")
        
        # Données simulées
        results = pd.DataFrame({
            'timestamp': pd.date_range(start='2025-01-15', periods=10, freq='H'),
            'src_ip': [f"203.0.113.{i}" for i in range(10)],
            'dst_ip': [f"192.168.1.{i+10}" for i in range(10)],
            'threat_score': np.random.randint(60, 100, 10),
            'ioc_match': ['Malicious IP', 'Suspicious Domain', 'Known C2'] * 3 + ['Clean']
        })
        
        st.dataframe(results, use_container_width=True)

def show_forensics():
    """Page d'analyse forensique"""
    st.header("🔬 Analyse Forensique")
    
    tabs = st.tabs(["Timeline", "Artefacts", "Mémoire", "Réseau"])
    
    with tabs[0]:
        st.subheader("Timeline des Événements")
        
        # Timeline interactive
        timeline_data = pd.DataFrame({
            'time': pd.date_range(start='2025-01-15 10:00', periods=20, freq='5min'),
            'event': ['Login', 'File Access', 'Network Connection', 'Process Start'] * 5,
            'severity': np.random.choice(['Low', 'Medium', 'High'], 20),
            'details': [f"Event details {i}" for i in range(20)]
        })
        
        fig = px.scatter(timeline_data, x='time', y='event', color='severity',
                        title="Timeline Forensique")
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        st.subheader("Artefacts Collectés")
        
        artifacts = pd.DataFrame({
            'type': ['Registry', 'File', 'Process', 'Network'] * 3,
            'path': [f"/path/to/artifact_{i}" for i in range(12)],
            'hash': [f"sha256:{i:064x}" for i in range(12)],
            'suspicious': np.random.choice([True, False], 12)
        })
        
        st.dataframe(artifacts, use_container_width=True)
    
    with tabs[2]:
        st.subheader("Analyse Mémoire")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Processus Suspects", "3")
            st.metric("Injections Détectées", "1")
        with col2:
            st.metric("Connexions Cachées", "2")
            st.metric("Rootkits", "0")
    
    with tabs[3]:
        st.subheader("Analyse Réseau")
        
        # Graphique de flux réseau
        network_data = pd.DataFrame({
            'source': ['Host A', 'Host B', 'Host C'] * 4,
            'target': ['Server 1', 'Server 2', 'External'] * 4,
            'bytes': np.random.randint(1000, 100000, 12)
        })
        
        fig = px.bar(network_data, x='source', y='bytes', color='target',
                    title="Flux Réseau par Hôte")
        st.plotly_chart(fig, use_container_width=True)

def show_compliance():
    """Page de conformité et audit"""
    st.header("📋 Conformité & Audit")
    
    # Frameworks de conformité
    frameworks = {
        'ISO 27001': {'score': 85, 'controls': 114, 'compliant': 97},
        'NIST CSF': {'score': 78, 'controls': 108, 'compliant': 84},
        'SOC 2': {'score': 92, 'controls': 64, 'compliant': 59},
        'GDPR': {'score': 88, 'controls': 32, 'compliant': 28}
    }
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Scores de Conformité")
        for framework, data in frameworks.items():
            st.metric(
                framework,
                f"{data['score']}%",
                f"{data['compliant']}/{data['controls']} contrôles"
            )
    
    with col2:
        st.subheader("Évolution de la Conformité")
        
        # Graphique d'évolution
        dates = pd.date_range(start='2024-01-01', end='2025-01-01', freq='M')
        compliance_evolution = pd.DataFrame({
            'Date': dates,
            'ISO 27001': np.random.randint(75, 90, len(dates)),
            'NIST CSF': np.random.randint(70, 85, len(dates)),
            'SOC 2': np.random.randint(85, 95, len(dates))
        })
        
        fig = px.line(compliance_evolution, x='Date', 
                     y=['ISO 27001', 'NIST CSF', 'SOC 2'],
                     title="Évolution des Scores de Conformité")
        st.plotly_chart(fig, use_container_width=True)
    
    # Contrôles non conformes
    st.subheader("⚠️ Contrôles Non Conformes")
    
    non_compliant = pd.DataFrame({
        'Framework': ['ISO 27001', 'NIST CSF', 'SOC 2', 'GDPR'],
        'Contrôle': ['A.12.1.2', 'PR.AC-1', 'CC6.1', 'Art. 32'],
        'Description': [
            'Gestion des vulnérabilités techniques',
            'Gestion des identités et authentification',
            'Contrôles d\'accès logique',
            'Sécurité du traitement'
        ],
        'Priorité': ['High', 'Medium', 'High', 'Critical'],
        'Échéance': ['2025-02-15', '2025-03-01', '2025-01-30', '2025-01-25']
    })
    
    st.dataframe(non_compliant, use_container_width=True)

def show_threat_intelligence():
    """Page de threat intelligence"""
    st.header("🧠 Threat Intelligence")
    
    tabs = st.tabs(["IOCs", "TTPs", "Campagnes", "Feeds"])
    
    with tabs[0]:
        st.subheader("Indicateurs de Compromission")
        
        iocs = pd.DataFrame({
            'Type': ['IP', 'Domain', 'Hash', 'URL'] * 5,
            'Valeur': [f"indicator_{i}" for i in range(20)],
            'Threat': ['APT29', 'Lazarus', 'FIN7', 'Carbanak'] * 5,
            'Confiance': np.random.randint(60, 100, 20),
            'Dernière Vue': pd.date_range(start='2025-01-10', periods=20, freq='H')
        })
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            type_filter = st.selectbox("Type IOC", ['Tous'] + list(iocs['Type'].unique()))
        with col2:
            threat_filter = st.selectbox("Groupe", ['Tous'] + list(iocs['Threat'].unique()))
        
        filtered_iocs = iocs.copy()
        if type_filter != 'Tous':
            filtered_iocs = filtered_iocs[filtered_iocs['Type'] == type_filter]
        if threat_filter != 'Tous':
            filtered_iocs = filtered_iocs[filtered_iocs['Threat'] == threat_filter]
        
        st.dataframe(filtered_iocs, use_container_width=True)
    
    with tabs[1]:
        st.subheader("Tactiques, Techniques et Procédures")
        
        # MITRE ATT&CK mapping
        ttps = pd.DataFrame({
            'Technique': ['T1566.001', 'T1059.001', 'T1055', 'T1083'],
            'Nom': ['Spearphishing Attachment', 'PowerShell', 'Process Injection', 'File Discovery'],
            'Tactique': ['Initial Access', 'Execution', 'Defense Evasion', 'Discovery'],
            'Détections': [15, 8, 3, 12],
            'Dernière': ['2025-01-14', '2025-01-15', '2025-01-13', '2025-01-15']
        })
        
        st.dataframe(ttps, use_container_width=True)
        
        # Heatmap MITRE ATT&CK
        st.subheader("Heatmap MITRE ATT&CK")
        
        tactics = ['Initial Access', 'Execution', 'Persistence', 'Privilege Escalation', 'Defense Evasion']
        techniques_count = np.random.randint(0, 10, len(tactics))
        
        fig = px.bar(x=tactics, y=techniques_count, 
                    title="Techniques Détectées par Tactique")
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        st.subheader("Campagnes Actives")
        
        campaigns = pd.DataFrame({
            'Nom': ['Operation Ghost', 'Silent Phoenix', 'Dark Nexus'],
            'Groupe': ['APT29', 'Lazarus', 'FIN7'],
            'Début': ['2025-01-10', '2025-01-12', '2025-01-14'],
            'Cibles': ['Gouvernement', 'Finance', 'Healthcare'],
            'Statut': ['Active', 'Monitoring', 'Active']
        })
        
        st.dataframe(campaigns, use_container_width=True)
    
    with tabs[3]:
        st.subheader("Feeds de Threat Intelligence")
        
        feeds = pd.DataFrame({
            'Source': ['AlienVault OTX', 'MISP', 'VirusTotal', 'Shodan'],
            'Type': ['IOCs', 'Malware', 'Hashes', 'Network'],
            'Dernière Sync': pd.date_range(start='2025-01-15', periods=4, freq='H'),
            'Statut': ['✅ Actif', '✅ Actif', '⚠️ Erreur', '✅ Actif'],
            'Nouveaux IOCs': [156, 89, 0, 234]
        })
        
        st.dataframe(feeds, use_container_width=True)

def show_reporting():
    """Page de reporting avancé"""
    st.header("📊 Reporting Avancé")
    
    # Types de rapports
    report_types = {
        'Exécutif': 'Résumé pour la direction',
        'Technique': 'Détails techniques pour les équipes',
        'Conformité': 'Rapport de conformité réglementaire',
        'Incident': 'Rapport post-incident détaillé'
    }
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Génération de Rapports")
        
        report_type = st.selectbox("Type de rapport", list(report_types.keys()))
        st.info(report_types[report_type])
        
        date_range = st.date_input("Période", value=[datetime.now().date() - timedelta(days=30), datetime.now().date()])
        
        format_type = st.selectbox("Format", ["PDF", "Excel", "PowerPoint"])
        
        if st.button("Générer Rapport", type="primary"):
            with st.spinner("Génération en cours..."):
                st.success(f"Rapport {report_type} généré en {format_type}")
    
    with col2:
        st.subheader("Aperçu du Rapport")
        
        if report_type == "Exécutif":
            st.markdown("""
            ### Résumé Exécutif - Sécurité IT
            
            **Période**: Janvier 2025
            
            **Points Clés**:
            - 🔴 3 incidents critiques résolus
            - 🟡 Augmentation de 15% des tentatives d'intrusion
            - 🟢 Temps de réponse amélioré de 20%
            
            **Recommandations**:
            1. Renforcer la surveillance des endpoints
            2. Mettre à jour les signatures de détection
            3. Former les utilisateurs sur le phishing
            """)
        
        elif report_type == "Technique":
            st.markdown("""
            ### Rapport Technique Détaillé
            
            **Incidents Analysés**: 156
            **Faux Positifs**: 23 (14.7%)
            **Temps Moyen de Résolution**: 2.3 heures
            
            **Top Menaces**:
            - Malware: 45%
            - Phishing: 30%
            - Intrusion: 25%
            """)

# Fonction principale pour les fonctionnalités avancées
def show_advanced_features():
    """Affiche les fonctionnalités avancées"""
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Fonctionnalités Avancées")
    
    advanced_pages = {
        "🎯 Threat Hunting": show_threat_hunting,
        "🔬 Forensique": show_forensics,
        "📋 Conformité": show_compliance,
        "🧠 Threat Intel": show_threat_intelligence,
        "📊 Reporting": show_reporting
    }
    
    selected_advanced = st.sidebar.selectbox("Sélectionner", list(advanced_pages.keys()))
    
    if selected_advanced:
        advanced_pages[selected_advanced]()
        return True
    
    return False