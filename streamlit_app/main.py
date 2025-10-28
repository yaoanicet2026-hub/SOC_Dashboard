"""
SOC Dashboard - Point d'entrée principal
Auteur: Yao Kouakou Luc Anicet Béranger
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

# Initialisation cloud
try:
    from utils.cloud_init import init_cloud_environment
    init_cloud_environment()
except:
    pass

from utils.data_loader import DataLoader
from utils.ai_detector import AIDetector
from utils.alert_manager import AlertManager
from auth import AuthManager
from config import Config

# Configuration de la page
st.set_page_config(
    page_title="SOC Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
def load_css():
    css_path = Path(__file__).parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialisation des composants
@st.cache_resource
def init_components():
    data_loader = DataLoader()
    ai_detector = AIDetector()
    alert_manager = AlertManager()
    return data_loader, ai_detector, alert_manager

def main():
    # Authentification
    auth = AuthManager()
    
    if not auth.is_authenticated():
        auth.login_form()
        return
    
    st.title("🛡️ SOC Dashboard")
    st.markdown("**Auteur**: Yao Kouakou Luc Anicet Béranger")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Bouton déconnexion
    if st.sidebar.button("🚪 Déconnexion"):
        auth.logout()
    
    pages = {
        "🏠 Dashboard": "dashboard",
        "⚠️ Menaces & Anomalies": "threats", 
        "🌐 Réseau & Trafic": "network",
        "🔍 Vulnérabilités": "vulns",
        "📋 Incidents": "incidents",
        "📊 Logs": "logs",
        "⚙️ Administration": "admin"
    }
    
    selected_page = st.sidebar.selectbox("Sélectionner une page", list(pages.keys()))
    
    # Initialiser les composants
    data_loader, ai_detector, alert_manager = init_components()
    
    # Stocker dans session state
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = data_loader
    if 'ai_detector' not in st.session_state:
        st.session_state.ai_detector = ai_detector
    if 'alert_manager' not in st.session_state:
        st.session_state.alert_manager = alert_manager
    
    # Router vers la page sélectionnée
    page_name = pages[selected_page]
    
    if page_name == "dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif page_name == "threats":
        from pages.threats import show_threats
        show_threats()
    elif page_name == "network":
        from pages.network import show_network
        show_network()
    elif page_name == "vulns":
        from pages.vulns import show_vulns
        show_vulns()
    elif page_name == "incidents":
        from pages.incidents import show_incidents
        show_incidents()
    elif page_name == "logs":
        from components.log_viewer import show_log_viewer
        show_log_viewer()
    elif page_name == "admin":
        from pages.admin import show_admin
        show_admin()

if __name__ == "__main__":
    main()