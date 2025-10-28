"""
Exporters - Modules d'export CSV/PDF
"""

import pandas as pd
from datetime import datetime
import json
from pathlib import Path
import logging

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab non disponible - export PDF désactivé")

class DataExporter:
    def __init__(self):
        self.export_dir = Path(__file__).parent.parent / "exports"
        self.export_dir.mkdir(exist_ok=True)
    
    def export_csv(self, data, filename, include_timestamp=True):
        """Export générique en CSV"""
        try:
            if include_timestamp:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{filename}_{timestamp}.csv"
            
            filepath = self.export_dir / filename
            
            if isinstance(data, pd.DataFrame):
                data.to_csv(filepath, index=False, encoding='utf-8')
            elif isinstance(data, list):
                pd.DataFrame(data).to_csv(filepath, index=False, encoding='utf-8')
            else:
                raise ValueError("Format de données non supporté")
            
            return str(filepath)
        
        except Exception as e:
            logging.error(f"Erreur export CSV: {e}")
            return None
    
    def export_json(self, data, filename, include_timestamp=True):
        """Export générique en JSON"""
        try:
            if include_timestamp:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{filename}_{timestamp}.json"
            
            filepath = self.export_dir / filename
            
            if isinstance(data, pd.DataFrame):
                data_dict = data.to_dict('records')
            else:
                data_dict = data
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)
            
            return str(filepath)
        
        except Exception as e:
            logging.error(f"Erreur export JSON: {e}")
            return None

class IncidentReporter:
    def __init__(self):
        self.exporter = DataExporter()
    
    def generate_incident_report(self, incidents_data, format='csv'):
        """Génère un rapport d'incidents"""
        
        if format.lower() == 'csv':
            return self.exporter.export_csv(
                incidents_data, 
                "incident_report"
            )
        elif format.lower() == 'json':
            return self.exporter.export_json(
                incidents_data,
                "incident_report"
            )
        elif format.lower() == 'pdf' and REPORTLAB_AVAILABLE:
            return self._generate_pdf_report(incidents_data)
        else:
            logging.error(f"Format {format} non supporté")
            return None
    
    def _generate_pdf_report(self, incidents_data):
        """Génère un rapport PDF (nécessite reportlab)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"incident_report_{timestamp}.pdf"
            filepath = self.exporter.export_dir / filename
            
            # Créer le document
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Centré
            )
            
            story.append(Paragraph("Rapport d'Incidents SOC", title_style))
            story.append(Spacer(1, 20))
            
            # Informations générales
            info_style = styles['Normal']
            story.append(Paragraph(f"<b>Date de génération:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", info_style))
            story.append(Paragraph(f"<b>Nombre d'incidents:</b> {len(incidents_data)}", info_style))
            story.append(Spacer(1, 20))
            
            # Tableau des incidents
            if incidents_data:
                # Préparer les données du tableau
                table_data = [['ID', 'Titre', 'Sévérité', 'Status', 'Assigné', 'Créé']]
                
                for incident in incidents_data:
                    row = [
                        incident.get('id', ''),
                        incident.get('title', '')[:30] + '...' if len(incident.get('title', '')) > 30 else incident.get('title', ''),
                        incident.get('severity', ''),
                        incident.get('status', ''),
                        incident.get('assignee', ''),
                        incident.get('created_at', '')[:10] if incident.get('created_at') else ''
                    ]
                    table_data.append(row)
                
                # Créer le tableau
                table = Table(table_data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
            
            # Construire le PDF
            doc.build(story)
            return str(filepath)
        
        except Exception as e:
            logging.error(f"Erreur génération PDF: {e}")
            return None

class VulnerabilityReporter:
    def __init__(self):
        self.exporter = DataExporter()
    
    def export_vulnerability_report(self, vulns_data, format='csv'):
        """Export rapport de vulnérabilités"""
        
        if isinstance(vulns_data, pd.DataFrame):
            # Ajouter des statistiques
            stats = {
                'total_vulns': len(vulns_data),
                'critical_vulns': len(vulns_data[vulns_data['severity'] == 'critical']),
                'high_vulns': len(vulns_data[vulns_data['severity'] == 'high']),
                'patched_vulns': len(vulns_data[vulns_data['status'] == 'patched']),
                'open_vulns': len(vulns_data[vulns_data['status'] == 'open']),
                'generated_at': datetime.now().isoformat()
            }
            
            if format.lower() == 'json':
                export_data = {
                    'statistics': stats,
                    'vulnerabilities': vulns_data.to_dict('records')
                }
                return self.exporter.export_json(export_data, "vulnerability_report")
            else:
                return self.exporter.export_csv(vulns_data, "vulnerability_report")
        
        return None

class NetworkReporter:
    def __init__(self):
        self.exporter = DataExporter()
    
    def export_network_analysis(self, network_data, stats, format='csv'):
        """Export analyse réseau"""
        
        if format.lower() == 'json':
            export_data = {
                'analysis_timestamp': datetime.now().isoformat(),
                'statistics': stats,
                'raw_data': network_data.to_dict('records') if isinstance(network_data, pd.DataFrame) else network_data
            }
            return self.exporter.export_json(export_data, "network_analysis")
        else:
            return self.exporter.export_csv(network_data, "network_analysis")

# Fonctions utilitaires
def export_logs_filtered(logs_df, filters, format='csv'):
    """Export de logs avec filtres appliqués"""
    exporter = DataExporter()
    
    # Appliquer les filtres
    filtered_logs = logs_df.copy()
    
    if filters.get('start_date'):
        filtered_logs = filtered_logs[filtered_logs['timestamp'] >= filters['start_date']]
    
    if filters.get('end_date'):
        filtered_logs = filtered_logs[filtered_logs['timestamp'] <= filters['end_date']]
    
    if filters.get('severity'):
        filtered_logs = filtered_logs[filtered_logs['severity'] == filters['severity']]
    
    if filters.get('event_type'):
        filtered_logs = filtered_logs[filtered_logs['event_type'] == filters['event_type']]
    
    # Export
    filename = f"logs_filtered_{len(filtered_logs)}_records"
    
    if format.lower() == 'csv':
        return exporter.export_csv(filtered_logs, filename)
    elif format.lower() == 'json':
        return exporter.export_json(filtered_logs, filename)
    
    return None

def create_executive_summary(kpis, alerts_stats, incidents_stats):
    """Crée un résumé exécutif"""
    
    summary = {
        'report_date': datetime.now().isoformat(),
        'executive_summary': {
            'total_alerts': kpis.get('total_alerts', 0),
            'critical_incidents': kpis.get('critical_alerts', 0),
            'mean_time_to_detect': f"{kpis.get('mttd', 0)} minutes",
            'mean_time_to_resolve': f"{kpis.get('mttr', 0)} minutes",
            'vulnerability_patch_rate': f"{kpis.get('patch_rate', 0)}%"
        },
        'key_metrics': {
            'alerts_by_severity': {
                'critical': kpis.get('critical_alerts', 0),
                'high': kpis.get('high_alerts', 0),
                'medium': kpis.get('medium_alerts', 0),
                'low': kpis.get('low_alerts', 0)
            },
            'incident_resolution': incidents_stats,
            'alert_trends': alerts_stats
        },
        'recommendations': [
            "Réviser les règles d'alerting pour réduire les faux positifs",
            "Améliorer les temps de réponse aux incidents critiques",
            "Prioriser le patching des vulnérabilités critiques",
            "Renforcer la surveillance des endpoints à haut risque"
        ]
    }
    
    exporter = DataExporter()
    return exporter.export_json(summary, "executive_summary")

# Configuration pour les exports
EXPORT_CONFIG = {
    'csv_encoding': 'utf-8',
    'json_indent': 2,
    'pdf_pagesize': A4,
    'max_records_per_export': 10000,
    'include_metadata': True
}

if __name__ == "__main__":
    # Test des exporters
    print("Test des modules d'export...")
    
    # Test données
    test_data = pd.DataFrame([
        {'id': 1, 'name': 'Test 1', 'value': 100},
        {'id': 2, 'name': 'Test 2', 'value': 200}
    ])
    
    exporter = DataExporter()
    
    # Test CSV
    csv_file = exporter.export_csv(test_data, "test_export", include_timestamp=False)
    print(f"Export CSV: {csv_file}")
    
    # Test JSON
    json_file = exporter.export_json(test_data, "test_export", include_timestamp=False)
    print(f"Export JSON: {json_file}")
    
    # Test rapport incidents
    incident_reporter = IncidentReporter()
    test_incidents = [
        {
            'id': 'INC-001',
            'title': 'Test Incident',
            'severity': 'high',
            'status': 'open',
            'assignee': 'analyst1',
            'created_at': datetime.now().isoformat()
        }
    ]
    
    report_file = incident_reporter.generate_incident_report(test_incidents, 'csv')
    print(f"Rapport incidents: {report_file}")
    
    if REPORTLAB_AVAILABLE:
        pdf_file = incident_reporter.generate_incident_report(test_incidents, 'pdf')
        print(f"Rapport PDF: {pdf_file}")
    else:
        print("ReportLab non disponible - pas de test PDF")