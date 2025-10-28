"""
Module d'authentification pour SOC Dashboard
"""

import streamlit as st
import bcrypt
import hashlib
from config import Config

class AuthManager:
    def __init__(self):
        self.config = Config()
    
    def hash_password(self, password):
        """Hash un mot de passe avec bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Vérifie un mot de passe"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            return False
    
    def login_form(self):
        """Affiche le formulaire de connexion"""
        st.title("🔐 Connexion SOC Dashboard")
        
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")
            
            if submitted:
                if self.authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Connexion réussie!")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
    
    def authenticate(self, username, password):
        """Authentifie un utilisateur"""
        # Mode développement simplifié
        return username == "admin" and password == "admin"
    
    def logout(self):
        """Déconnecte l'utilisateur"""
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    
    def is_authenticated(self):
        """Vérifie si l'utilisateur est authentifié"""
        return st.session_state.get('authenticated', False)
    
    def require_auth(self):
        """Décorateur pour pages nécessitant une authentification"""
        if not self.is_authenticated():
            self.login_form()
            st.stop()

def generate_password_hash(password):
    """Utilitaire pour générer un hash de mot de passe"""
    auth = AuthManager()
    return auth.hash_password(password)

if __name__ == "__main__":
    # Générer un hash pour le mot de passe admin
    password = "admin123"
    hash_value = generate_password_hash(password)
    print(f"Hash pour '{password}': {hash_value}")
    print(f"Ajouter dans .env: ADMIN_PASSWORD_HASH={hash_value}")