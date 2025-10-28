"""
KPI Card - Composant réutilisable pour afficher les métriques
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_kpi_card(title, value, delta=None, delta_color="normal", help_text=None, icon=None):
    """
    Affiche une carte KPI stylisée
    
    Args:
        title: Titre de la métrique
        value: Valeur principale
        delta: Variation (optionnel)
        delta_color: Couleur du delta ("normal", "inverse")
        help_text: Texte d'aide (optionnel)
        icon: Emoji ou icône (optionnel)
    """
    
    # Formatage de la valeur
    if isinstance(value, (int, float)):
        if value >= 1000000:
            formatted_value = f"{value/1000000:.1f}M"
        elif value >= 1000:
            formatted_value = f"{value/1000:.1f}K"
        else:
            formatted_value = str(value)
    else:
        formatted_value = str(value)
    
    # Affichage avec Streamlit
    if icon:
        display_title = f"{icon} {title}"
    else:
        display_title = title
    
    st.metric(
        label=display_title,
        value=formatted_value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )

def render_kpi_grid(kpis_data, columns=4):
    """
    Affiche une grille de KPIs
    
    Args:
        kpis_data: Liste de dictionnaires avec les données KPI
        columns: Nombre de colonnes
    """
    
    cols = st.columns(columns)
    
    for i, kpi in enumerate(kpis_data):
        with cols[i % columns]:
            render_kpi_card(
                title=kpi.get('title', ''),
                value=kpi.get('value', 0),
                delta=kpi.get('delta'),
                delta_color=kpi.get('delta_color', 'normal'),
                help_text=kpi.get('help'),
                icon=kpi.get('icon')
            )

def render_trend_kpi(title, current_value, historical_values, target_value=None):
    """
    Affiche un KPI avec graphique de tendance intégré
    
    Args:
        title: Titre de la métrique
        current_value: Valeur actuelle
        historical_values: Liste des valeurs historiques
        target_value: Valeur cible (optionnel)
    """
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Calcul du delta
        if len(historical_values) >= 2:
            delta = current_value - historical_values[-2]
            delta_percent = (delta / historical_values[-2]) * 100 if historical_values[-2] != 0 else 0
            delta_text = f"{delta:+.0f} ({delta_percent:+.1f}%)"
        else:
            delta_text = None
        
        st.metric(
            label=title,
            value=current_value,
            delta=delta_text
        )
    
    with col2:
        # Mini graphique de tendance
        fig = go.Figure()
        
        # Ligne de tendance
        fig.add_trace(go.Scatter(
            y=historical_values + [current_value],
            mode='lines+markers',
            line=dict(color='#00ff88', width=2),
            marker=dict(size=4),
            showlegend=False
        ))
        
        # Ligne cible si fournie
        if target_value:
            fig.add_hline(
                y=target_value,
                line_dash="dash",
                line_color="orange",
                annotation_text="Cible"
            )
        
        fig.update_layout(
            height=100,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_gauge_kpi(title, value, min_val=0, max_val=100, thresholds=None):
    """
    Affiche un KPI sous forme de jauge
    
    Args:
        title: Titre de la métrique
        value: Valeur actuelle
        min_val: Valeur minimale
        max_val: Valeur maximale
        thresholds: Dict avec seuils {'low': 30, 'medium': 70, 'high': 90}
    """
    
    # Couleurs par défaut
    if not thresholds:
        thresholds = {'low': max_val * 0.3, 'medium': max_val * 0.7, 'high': max_val * 0.9}
    
    # Déterminer la couleur
    if value <= thresholds['low']:
        color = '#44ff44'  # Vert
    elif value <= thresholds['medium']:
        color = '#ffcc00'  # Jaune
    elif value <= thresholds['high']:
        color = '#ff8800'  # Orange
    else:
        color = '#ff4444'  # Rouge
    
    # Créer la jauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'color': 'white'}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickcolor': 'white'},
            'bar': {'color': color},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 2,
            'bordercolor': 'white',
            'steps': [
                {'range': [min_val, thresholds['low']], 'color': 'rgba(68,255,68,0.3)'},
                {'range': [thresholds['low'], thresholds['medium']], 'color': 'rgba(255,204,0,0.3)'},
                {'range': [thresholds['medium'], thresholds['high']], 'color': 'rgba(255,136,0,0.3)'},
                {'range': [thresholds['high'], max_val], 'color': 'rgba(255,68,68,0.3)'}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': thresholds['high']
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_comparison_kpi(title, current_period, previous_period, period_labels=None):
    """
    Affiche un KPI de comparaison entre deux périodes
    
    Args:
        title: Titre de la métrique
        current_period: Valeur période actuelle
        previous_period: Valeur période précédente
        period_labels: Labels des périodes ['Cette semaine', 'Semaine dernière']
    """
    
    if not period_labels:
        period_labels = ['Actuel', 'Précédent']
    
    # Calcul de la variation
    if previous_period != 0:
        change_percent = ((current_period - previous_period) / previous_period) * 100
        change_abs = current_period - previous_period
    else:
        change_percent = 0
        change_abs = current_period
    
    # Déterminer la couleur
    if change_abs > 0:
        color = '#44ff44' if 'incident' not in title.lower() else '#ff4444'
        arrow = '↗'
    elif change_abs < 0:
        color = '#ff4444' if 'incident' not in title.lower() else '#44ff44'
        arrow = '↘'
    else:
        color = '#888888'
        arrow = '→'
    
    st.subheader(title)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(period_labels[0], current_period)
    
    with col2:
        st.metric(period_labels[1], previous_period)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px;">
            <div style="font-size: 24px; color: {color};">{arrow}</div>
            <div style="color: {color}; font-weight: bold;">
                {change_abs:+.0f} ({change_percent:+.1f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_status_kpi(title, status, status_config=None):
    """
    Affiche un KPI de statut avec couleurs
    
    Args:
        title: Titre de la métrique
        status: Statut actuel
        status_config: Configuration des statuts et couleurs
    """
    
    if not status_config:
        status_config = {
            'online': {'color': '#44ff44', 'icon': '🟢'},
            'offline': {'color': '#ff4444', 'icon': '🔴'},
            'warning': {'color': '#ffcc00', 'icon': '🟡'},
            'maintenance': {'color': '#888888', 'icon': '⚪'},
            'active': {'color': '#44ff44', 'icon': '✅'},
            'inactive': {'color': '#ff4444', 'icon': '❌'},
            'pending': {'color': '#ffcc00', 'icon': '⏳'}
        }
    
    config = status_config.get(status.lower(), {'color': '#888888', 'icon': '❓'})
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; border: 2px solid {config['color']}; border-radius: 10px;">
        <div style="font-size: 16px; color: white; margin-bottom: 10px;">{title}</div>
        <div style="font-size: 32px; margin-bottom: 10px;">{config['icon']}</div>
        <div style="font-size: 18px; color: {config['color']}; font-weight: bold; text-transform: uppercase;">
            {status}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_progress_kpi(title, current, target, unit=""):
    """
    Affiche un KPI avec barre de progression
    
    Args:
        title: Titre de la métrique
        current: Valeur actuelle
        target: Valeur cible
        unit: Unité de mesure
    """
    
    progress = min(current / target, 1.0) if target > 0 else 0
    percentage = progress * 100
    
    # Couleur basée sur le progrès
    if percentage >= 90:
        color = '#44ff44'
    elif percentage >= 70:
        color = '#ffcc00'
    elif percentage >= 50:
        color = '#ff8800'
    else:
        color = '#ff4444'
    
    st.subheader(title)
    
    # Barre de progression personnalisée
    st.markdown(f"""
    <div style="margin: 10px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>{current}{unit}</span>
            <span>{target}{unit}</span>
        </div>
        <div style="background-color: #333; height: 20px; border-radius: 10px; overflow: hidden;">
            <div style="background-color: {color}; height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
        </div>
        <div style="text-align: center; margin-top: 5px; color: {color}; font-weight: bold;">
            {percentage:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

# Exemples d'utilisation
def demo_kpi_cards():
    """Démonstration des différents types de cartes KPI"""
    
    st.title("Démonstration KPI Cards")
    
    # KPIs simples
    st.subheader("KPIs Simples")
    kpis_simple = [
        {'title': 'Total Alertes', 'value': 1234, 'delta': '+15%', 'icon': '🚨'},
        {'title': 'Incidents Critiques', 'value': 23, 'delta': '-5', 'delta_color': 'inverse', 'icon': '🔴'},
        {'title': 'MTTD', 'value': '15 min', 'delta': '-2 min', 'delta_color': 'inverse', 'icon': '⏱️'},
        {'title': 'Taux de Résolution', 'value': '94%', 'delta': '+3%', 'icon': '✅'}
    ]
    render_kpi_grid(kpis_simple)
    
    st.divider()
    
    # KPI avec tendance
    st.subheader("KPI avec Tendance")
    col1, col2 = st.columns(2)
    
    with col1:
        render_trend_kpi(
            "Alertes par Jour",
            current_value=45,
            historical_values=[38, 42, 35, 48, 41, 39],
            target_value=40
        )
    
    with col2:
        render_gauge_kpi(
            "Score de Sécurité",
            value=78,
            min_val=0,
            max_val=100,
            thresholds={'low': 40, 'medium': 70, 'high': 90}
        )
    
    st.divider()
    
    # Comparaison et statut
    col1, col2 = st.columns(2)
    
    with col1:
        render_comparison_kpi(
            "Incidents cette semaine",
            current_period=12,
            previous_period=18,
            period_labels=['Cette semaine', 'Semaine dernière']
        )
    
    with col2:
        render_status_kpi("Statut Système", "online")
    
    st.divider()
    
    # Barre de progression
    render_progress_kpi(
        "Objectif Patch Management",
        current=78,
        target=100,
        unit="%"
    )

if __name__ == "__main__":
    demo_kpi_cards()