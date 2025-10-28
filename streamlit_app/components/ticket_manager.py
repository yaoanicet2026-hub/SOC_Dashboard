"""
Ticket Manager - Composant de gestion des tickets d'incidents
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

class TicketManager:
    def __init__(self, tickets_file=None):
        if tickets_file is None:
            self.tickets_file = Path(__file__).parent.parent.parent / "data" / "tickets.json"
        else:
            self.tickets_file = Path(tickets_file)
        
        self.severity_colors = {
            'critical': '#ff4444',
            'high': '#ff8800',
            'medium': '#ffcc00',
            'low': '#44ff44'
        }
        
        self.status_colors = {
            'open': '#ff6666',
            'in_progress': '#ffaa66',
            'resolved': '#66ff66',
            'closed': '#888888'
        }
    
    def load_tickets(self):
        """Charge les tickets depuis le fichier JSON"""
        if self.tickets_file.exists():
            try:
                with open(self.tickets_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_tickets(self, tickets):
        """Sauvegarde les tickets dans le fichier JSON"""
        try:
            self.tickets_file.parent.mkdir(exist_ok=True)
            with open(self.tickets_file, 'w') as f:
                json.dump(tickets, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Erreur sauvegarde: {e}")
            return False
    
    def create_ticket_form(self):
        """Affiche le formulaire de création de ticket"""
        st.subheader("Nouveau Ticket")
        
        with st.form("new_ticket_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Titre*", placeholder="Résumé de l'incident")
                severity = st.selectbox("Sévérité*", ['low', 'medium', 'high', 'critical'])
                incident_type = st.selectbox("Type*", ['security', 'network', 'system', 'application', 'other'])
            
            with col2:
                assignee = st.text_input("Assigné à", placeholder="analyst1")
                priority = st.selectbox("Priorité", ['P1', 'P2', 'P3', 'P4'])
                source = st.selectbox("Source", ['manual', 'alert', 'monitoring', 'user_report'])
            
            description = st.text_area("Description*", placeholder="Description détaillée de l'incident")
            
            # Champs additionnels
            with st.expander("Informations supplémentaires"):
                col1, col2 = st.columns(2)
                
                with col1:
                    affected_systems = st.text_input("Systèmes affectés", placeholder="host-01, host-02")
                    impact_level = st.selectbox("Niveau d'impact", ['low', 'medium', 'high', 'critical'])
                
                with col2:
                    category = st.selectbox("Catégorie", [
                        'malware', 'phishing', 'data_breach', 'dos_attack', 
                        'unauthorized_access', 'policy_violation', 'other'
                    ])
                    tags = st.text_input("Tags", placeholder="bruteforce, ssh, external")
            
            submitted = st.form_submit_button("Créer Ticket", type="primary")
            
            if submitted:
                if title and description:
                    tickets = self.load_tickets()
                    
                    new_ticket = {
                        'id': f"INC-{len(tickets)+1:04d}",
                        'title': title,
                        'description': description,
                        'severity': severity,
                        'type': incident_type,
                        'priority': priority,
                        'status': 'open',
                        'assignee': assignee or 'unassigned',
                        'source': source,
                        'affected_systems': affected_systems,
                        'impact_level': impact_level,
                        'category': category,
                        'tags': [tag.strip() for tag in tags.split(',') if tag.strip()],
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                        'created_by': 'soc_analyst',
                        'comments': [],
                        'attachments': [],
                        'sla_deadline': self._calculate_sla_deadline(severity),
                        'detection_time': None,
                        'resolution_time': None
                    }
                    
                    tickets.append(new_ticket)
                    
                    if self.save_tickets(tickets):
                        st.success(f"Ticket {new_ticket['id']} créé avec succès!")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la création du ticket")
                else:
                    st.error("Titre et description sont requis")
    
    def display_tickets_table(self, tickets, show_filters=True):
        """Affiche la table des tickets avec filtres"""
        if not tickets:
            st.info("Aucun ticket disponible")
            return []
        
        df = pd.DataFrame(tickets)
        
        if show_filters:
            # Filtres
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status_filter = st.selectbox(
                    "Statut",
                    ['Tous'] + list(df['status'].unique())
                )
            
            with col2:
                severity_filter = st.selectbox(
                    "Sévérité", 
                    ['Tous'] + list(df['severity'].unique())
                )
            
            with col3:
                assignee_filter = st.selectbox(
                    "Assigné",
                    ['Tous'] + list(df['assignee'].unique())
                )
            
            with col4:
                type_filter = st.selectbox(
                    "Type",
                    ['Tous'] + list(df['type'].unique())
                )
            
            # Appliquer les filtres
            filtered_df = df.copy()
            
            if status_filter != 'Tous':
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            if severity_filter != 'Tous':
                filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
            
            if assignee_filter != 'Tous':
                filtered_df = filtered_df[filtered_df['assignee'] == assignee_filter]
            
            if type_filter != 'Tous':
                filtered_df = filtered_df[filtered_df['type'] == type_filter]
        else:
            filtered_df = df
        
        # Affichage de la table
        if not filtered_df.empty:
            # Colonnes à afficher
            display_columns = ['id', 'title', 'severity', 'status', 'assignee', 'created_at', 'priority']
            display_df = filtered_df[display_columns].copy()
            
            # Formatage des dates
            display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
            
            # Affichage avec style
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "id": st.column_config.TextColumn("ID", width="small"),
                    "title": st.column_config.TextColumn("Titre", width="large"),
                    "severity": st.column_config.TextColumn("Sévérité", width="small"),
                    "status": st.column_config.TextColumn("Statut", width="small"),
                    "assignee": st.column_config.TextColumn("Assigné", width="medium"),
                    "created_at": st.column_config.TextColumn("Créé le", width="medium"),
                    "priority": st.column_config.TextColumn("Priorité", width="small")
                }
            )
            
            return filtered_df.to_dict('records')
        else:
            st.info("Aucun ticket ne correspond aux filtres")
            return []
    
    def display_ticket_details(self, ticket):
        """Affiche les détails d'un ticket"""
        st.subheader(f"Détails - {ticket['id']}")
        
        # Informations principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Titre:** {ticket['title']}")
            st.write(f"**Sévérité:** {ticket['severity']}")
            st.write(f"**Type:** {ticket['type']}")
        
        with col2:
            st.write(f"**Statut:** {ticket['status']}")
            st.write(f"**Priorité:** {ticket.get('priority', 'N/A')}")
            st.write(f"**Assigné:** {ticket['assignee']}")
        
        with col3:
            created_date = datetime.fromisoformat(ticket['created_at']).strftime('%d/%m/%Y %H:%M')
            st.write(f"**Créé:** {created_date}")
            
            if ticket.get('sla_deadline'):
                sla_date = datetime.fromisoformat(ticket['sla_deadline']).strftime('%d/%m/%Y %H:%M')
                st.write(f"**SLA:** {sla_date}")
            
            age = datetime.now() - datetime.fromisoformat(ticket['created_at'])
            st.write(f"**Âge:** {age.days}j {age.seconds//3600}h")
        
        # Description
        st.write("**Description:**")
        st.write(ticket['description'])
        
        # Informations supplémentaires
        if ticket.get('affected_systems'):
            st.write(f"**Systèmes affectés:** {ticket['affected_systems']}")
        
        if ticket.get('tags'):
            st.write(f"**Tags:** {', '.join(ticket['tags'])}")
        
        # Commentaires
        st.write("**Commentaires:**")
        comments = ticket.get('comments', [])
        
        if comments:
            for comment in comments:
                with st.expander(f"{comment['author']} - {comment['timestamp'][:16]}"):
                    st.write(comment['content'])
        else:
            st.info("Aucun commentaire")
        
        # Ajouter un commentaire
        with st.expander("Ajouter un commentaire"):
            comment_text = st.text_area("Commentaire")
            if st.button("Ajouter"):
                if comment_text:
                    new_comment = {
                        'author': 'current_user',
                        'timestamp': datetime.now().isoformat(),
                        'content': comment_text
                    }
                    ticket['comments'].append(new_comment)
                    ticket['updated_at'] = datetime.now().isoformat()
                    st.success("Commentaire ajouté!")
                    st.rerun()
    
    def ticket_actions(self, ticket):
        """Affiche les actions possibles sur un ticket"""
        st.subheader("Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if ticket['status'] != 'resolved':
                if st.button("✅ Résoudre", key=f"resolve_{ticket['id']}"):
                    ticket['status'] = 'resolved'
                    ticket['updated_at'] = datetime.now().isoformat()
                    ticket['resolution_time'] = datetime.now().isoformat()
                    st.success("Ticket résolu!")
                    st.rerun()
        
        with col2:
            if ticket['status'] == 'open':
                if st.button("🔄 En cours", key=f"progress_{ticket['id']}"):
                    ticket['status'] = 'in_progress'
                    ticket['updated_at'] = datetime.now().isoformat()
                    st.success("Ticket en cours de traitement!")
                    st.rerun()
        
        with col3:
            if st.button("📝 Éditer", key=f"edit_{ticket['id']}"):
                st.session_state[f"editing_{ticket['id']}"] = True
                st.rerun()
        
        with col4:
            if st.button("🗑️ Supprimer", key=f"delete_{ticket['id']}"):
                if st.session_state.get(f"confirm_delete_{ticket['id']}", False):
                    # Supprimer le ticket
                    tickets = self.load_tickets()
                    tickets = [t for t in tickets if t['id'] != ticket['id']]
                    self.save_tickets(tickets)
                    st.success("Ticket supprimé!")
                    st.rerun()
                else:
                    st.session_state[f"confirm_delete_{ticket['id']}"] = True
                    st.warning("Cliquez à nouveau pour confirmer la suppression")
    
    def edit_ticket_form(self, ticket):
        """Formulaire d'édition de ticket"""
        st.subheader(f"Édition - {ticket['id']}")
        
        with st.form(f"edit_ticket_{ticket['id']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_title = st.text_input("Titre", value=ticket['title'])
                new_severity = st.selectbox("Sévérité", 
                    ['low', 'medium', 'high', 'critical'],
                    index=['low', 'medium', 'high', 'critical'].index(ticket['severity'])
                )
                new_status = st.selectbox("Statut",
                    ['open', 'in_progress', 'resolved', 'closed'],
                    index=['open', 'in_progress', 'resolved', 'closed'].index(ticket['status'])
                )
            
            with col2:
                new_assignee = st.text_input("Assigné", value=ticket['assignee'])
                new_priority = st.selectbox("Priorité",
                    ['P1', 'P2', 'P3', 'P4'],
                    index=['P1', 'P2', 'P3', 'P4'].index(ticket.get('priority', 'P3'))
                )
                new_type = st.selectbox("Type",
                    ['security', 'network', 'system', 'application', 'other'],
                    index=['security', 'network', 'system', 'application', 'other'].index(ticket['type'])
                )
            
            new_description = st.text_area("Description", value=ticket['description'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("💾 Sauvegarder", type="primary"):
                    ticket.update({
                        'title': new_title,
                        'severity': new_severity,
                        'status': new_status,
                        'assignee': new_assignee,
                        'priority': new_priority,
                        'type': new_type,
                        'description': new_description,
                        'updated_at': datetime.now().isoformat()
                    })
                    
                    tickets = self.load_tickets()
                    for i, t in enumerate(tickets):
                        if t['id'] == ticket['id']:
                            tickets[i] = ticket
                            break
                    
                    if self.save_tickets(tickets):
                        st.success("Ticket mis à jour!")
                        del st.session_state[f"editing_{ticket['id']}"]
                        st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Annuler"):
                    del st.session_state[f"editing_{ticket['id']}"]
                    st.rerun()
    
    def get_ticket_statistics(self, tickets):
        """Calcule les statistiques des tickets"""
        if not tickets:
            return {}
        
        df = pd.DataFrame(tickets)
        
        # Statistiques de base
        stats = {
            'total': len(tickets),
            'open': len(df[df['status'] == 'open']),
            'in_progress': len(df[df['status'] == 'in_progress']),
            'resolved': len(df[df['status'] == 'resolved']),
            'by_severity': df['severity'].value_counts().to_dict(),
            'by_assignee': df['assignee'].value_counts().to_dict(),
            'by_type': df['type'].value_counts().to_dict()
        }
        
        # Calcul MTTD et MTTR
        resolved_tickets = df[df['status'] == 'resolved']
        if not resolved_tickets.empty:
            # MTTR simulé (en minutes)
            resolution_times = []
            for _, ticket in resolved_tickets.iterrows():
                created = datetime.fromisoformat(ticket['created_at'])
                if ticket.get('resolution_time'):
                    resolved = datetime.fromisoformat(ticket['resolution_time'])
                    resolution_times.append((resolved - created).total_seconds() / 60)
            
            if resolution_times:
                stats['mttr'] = sum(resolution_times) / len(resolution_times)
            else:
                stats['mttr'] = 0
        else:
            stats['mttr'] = 0
        
        # MTTD simulé
        stats['mttd'] = 15  # Minutes
        
        return stats
    
    def _calculate_sla_deadline(self, severity):
        """Calcule la deadline SLA basée sur la sévérité"""
        sla_hours = {
            'critical': 4,
            'high': 24,
            'medium': 72,
            'low': 168
        }
        
        hours = sla_hours.get(severity, 72)
        deadline = datetime.now() + timedelta(hours=hours)
        return deadline.isoformat()

# Fonctions utilitaires
def render_ticket_summary_cards(stats):
    """Affiche les cartes de résumé des tickets"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tickets", stats.get('total', 0))
    
    with col2:
        st.metric("Ouverts", stats.get('open', 0))
    
    with col3:
        st.metric("En Cours", stats.get('in_progress', 0))
    
    with col4:
        st.metric("Résolus", stats.get('resolved', 0))

def export_tickets_csv(tickets):
    """Exporte les tickets en CSV"""
    if tickets:
        df = pd.DataFrame(tickets)
        csv = df.to_csv(index=False)
        return csv
    return None

if __name__ == "__main__":
    # Test du composant
    st.title("Test Ticket Manager")
    
    tm = TicketManager()
    
    # Créer quelques tickets de test si aucun n'existe
    tickets = tm.load_tickets()
    if not tickets:
        test_tickets = [
            {
                'id': 'INC-0001',
                'title': 'Test Incident 1',
                'description': 'Description test',
                'severity': 'high',
                'status': 'open',
                'type': 'security',
                'assignee': 'analyst1',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'comments': []
            }
        ]
        tm.save_tickets(test_tickets)
        tickets = test_tickets
    
    # Afficher les statistiques
    stats = tm.get_ticket_statistics(tickets)
    render_ticket_summary_cards(stats)
    
    # Afficher la table
    tm.display_tickets_table(tickets)
    
    # Formulaire de création
    tm.create_ticket_form()