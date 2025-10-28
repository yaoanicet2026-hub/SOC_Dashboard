"""
Page Incidents - Gestion des tickets et incident response
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

def show_incidents():
    st.header("📋 Gestion des Incidents")
    
    # Initialiser les tickets s'ils n'existent pas
    tickets_file = Path(__file__).parent.parent.parent / "data" / "tickets.json"
    
    if 'tickets' not in st.session_state:
        st.session_state.tickets = load_tickets(tickets_file)
    
    # KPIs incidents
    tickets = st.session_state.tickets
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tickets = len(tickets)
        st.metric("Total Incidents", total_tickets)
    
    with col2:
        open_tickets = len([t for t in tickets if t['status'] == 'open'])
        st.metric("Ouverts", open_tickets)
    
    with col3:
        # Calculer MTTD moyen (simulé)
        avg_mttd = 15  # minutes
        st.metric("MTTD Moyen", f"{avg_mttd} min")
    
    with col4:
        # Calculer MTTR moyen (simulé)
        resolved_tickets = [t for t in tickets if t['status'] == 'resolved']
        if resolved_tickets:
            avg_mttr = sum([t.get('resolution_time', 120) for t in resolved_tickets]) / len(resolved_tickets)
        else:
            avg_mttr = 0
        st.metric("MTTR Moyen", f"{int(avg_mttr)} min")
    
    st.divider()
    
    # Créer nouveau ticket
    st.subheader("➕ Nouveau Ticket")
    
    with st.expander("Créer un incident"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_title = st.text_input("Titre de l'incident")
            new_severity = st.selectbox("Sévérité", ['low', 'medium', 'high', 'critical'])
            new_type = st.selectbox("Type", ['security', 'network', 'system', 'application'])
        
        with col2:
            new_assignee = st.text_input("Assigné à", "analyst1")
            new_description = st.text_area("Description")
        
        if st.button("🎫 Créer Ticket"):
            if new_title and new_description:
                new_ticket = {
                    'id': f"INC-{len(tickets)+1:04d}",
                    'title': new_title,
                    'description': new_description,
                    'severity': new_severity,
                    'type': new_type,
                    'status': 'open',
                    'assignee': new_assignee,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'detection_time': 5,  # MTTD simulé
                    'resolution_time': None
                }
                
                st.session_state.tickets.append(new_ticket)
                save_tickets(tickets_file, st.session_state.tickets)
                st.success(f"✅ Ticket {new_ticket['id']} créé!")
                st.rerun()
            else:
                st.error("Titre et description requis")
    
    st.divider()
    
    # Liste des tickets
    st.subheader("🎫 Tickets Actifs")
    
    if tickets:
        # Filtres
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Filtrer par Status",
                ['Tous', 'open', 'in_progress', 'resolved']
            )
        
        with col2:
            severity_filter = st.selectbox(
                "Filtrer par Sévérité",
                ['Tous', 'critical', 'high', 'medium', 'low']
            )
        
        with col3:
            assignee_filter = st.selectbox(
                "Filtrer par Assigné",
                ['Tous'] + list(set([t['assignee'] for t in tickets]))
            )
        
        # Appliquer filtres
        filtered_tickets = tickets.copy()
        
        if status_filter != 'Tous':
            filtered_tickets = [t for t in filtered_tickets if t['status'] == status_filter]
        
        if severity_filter != 'Tous':
            filtered_tickets = [t for t in filtered_tickets if t['severity'] == severity_filter]
        
        if assignee_filter != 'Tous':
            filtered_tickets = [t for t in filtered_tickets if t['assignee'] == assignee_filter]
        
        # Afficher les tickets
        for ticket in filtered_tickets:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                
                with col1:
                    severity_emoji = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🟢'
                    }
                    
                    st.write(f"**{severity_emoji.get(ticket['severity'], '⚪')} {ticket['id']}** - {ticket['title']}")
                    st.caption(f"Assigné: {ticket['assignee']} | Type: {ticket['type']}")
                
                with col2:
                    status_color = {
                        'open': '🔴',
                        'in_progress': '🟡',
                        'resolved': '🟢'
                    }
                    st.write(f"{status_color.get(ticket['status'], '⚪')} {ticket['status']}")
                
                with col3:
                    created = datetime.fromisoformat(ticket['created_at'])
                    age = datetime.now() - created
                    st.write(f"⏱️ {age.days}j {age.seconds//3600}h")
                
                with col4:
                    # Actions rapides
                    action_col1, action_col2 = st.columns(2)
                    
                    with action_col1:
                        if ticket['status'] != 'resolved':
                            if st.button("✅", key=f"resolve_{ticket['id']}", help="Résoudre"):
                                ticket['status'] = 'resolved'
                                ticket['updated_at'] = datetime.now().isoformat()
                                ticket['resolution_time'] = 120  # Simulé
                                save_tickets(tickets_file, st.session_state.tickets)
                                st.rerun()
                    
                    with action_col2:
                        if st.button("📝", key=f"edit_{ticket['id']}", help="Éditer"):
                            st.session_state.editing_ticket = ticket['id']
                
                st.divider()
        
        # Édition de ticket
        if hasattr(st.session_state, 'editing_ticket'):
            ticket_to_edit = next((t for t in tickets if t['id'] == st.session_state.editing_ticket), None)
            
            if ticket_to_edit:
                st.subheader(f"✏️ Édition {ticket_to_edit['id']}")
                
                with st.form(f"edit_form_{ticket_to_edit['id']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_title = st.text_input("Titre", value=ticket_to_edit['title'])
                        edit_status = st.selectbox("Status", ['open', 'in_progress', 'resolved'], 
                                                 index=['open', 'in_progress', 'resolved'].index(ticket_to_edit['status']))
                        edit_severity = st.selectbox("Sévérité", ['low', 'medium', 'high', 'critical'],
                                                   index=['low', 'medium', 'high', 'critical'].index(ticket_to_edit['severity']))
                    
                    with col2:
                        edit_assignee = st.text_input("Assigné", value=ticket_to_edit['assignee'])
                        edit_type = st.selectbox("Type", ['security', 'network', 'system', 'application'],
                                               index=['security', 'network', 'system', 'application'].index(ticket_to_edit['type']))
                    
                    edit_description = st.text_area("Description", value=ticket_to_edit['description'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.form_submit_button("💾 Sauvegarder"):
                            ticket_to_edit.update({
                                'title': edit_title,
                                'status': edit_status,
                                'severity': edit_severity,
                                'assignee': edit_assignee,
                                'type': edit_type,
                                'description': edit_description,
                                'updated_at': datetime.now().isoformat()
                            })
                            save_tickets(tickets_file, st.session_state.tickets)
                            del st.session_state.editing_ticket
                            st.success("✅ Ticket mis à jour!")
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ Annuler"):
                            del st.session_state.editing_ticket
                            st.rerun()
    
    else:
        st.info("Aucun ticket d'incident")
    
    st.divider()
    
    # Export et rapports
    st.subheader("📊 Rapports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Exporter CSV"):
            if tickets:
                df = pd.DataFrame(tickets)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Télécharger CSV",
                    csv,
                    "incidents.csv",
                    "text/csv"
                )
            else:
                st.warning("Aucun ticket à exporter")
    
    with col2:
        if st.button("📄 Rapport PDF"):
            st.info("Génération PDF - Fonctionnalité à implémenter")
            # TODO: Implémenter génération PDF avec reportlab
    
    with col3:
        if st.button("📈 Métriques SLA"):
            st.info("Calcul des métriques SLA en cours...")
            # TODO: Implémenter calcul SLA détaillé

def load_tickets(file_path):
    """Charge les tickets depuis le fichier JSON"""
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Tickets par défaut
    return [
        {
            'id': 'INC-0001',
            'title': 'Tentative de bruteforce SSH détectée',
            'description': 'Multiples tentatives de connexion SSH échouées depuis 45.89.22.4',
            'severity': 'high',
            'type': 'security',
            'status': 'open',
            'assignee': 'analyst1',
            'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
            'updated_at': (datetime.now() - timedelta(hours=2)).isoformat(),
            'detection_time': 8,
            'resolution_time': None
        },
        {
            'id': 'INC-0002',
            'title': 'Scan de ports détecté',
            'description': 'Activité de scan de ports depuis 203.0.113.50',
            'severity': 'medium',
            'type': 'security',
            'status': 'in_progress',
            'assignee': 'analyst2',
            'created_at': (datetime.now() - timedelta(hours=4)).isoformat(),
            'updated_at': (datetime.now() - timedelta(hours=1)).isoformat(),
            'detection_time': 12,
            'resolution_time': None
        }
    ]

def save_tickets(file_path, tickets):
    """Sauvegarde les tickets dans le fichier JSON"""
    try:
        file_path.parent.mkdir(exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(tickets, f, indent=2)
    except Exception as e:
        st.error(f"Erreur sauvegarde: {e}")