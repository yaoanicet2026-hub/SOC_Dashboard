"""
AI Detector - Détection d'anomalies avec Machine Learning
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import logging

class AIDetector:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = Path(__file__).parent.parent / "models" / "anomaly_model.pkl"
        self.scaler_path = Path(__file__).parent.parent / "models" / "scaler.pkl"
        self.features = ['bytes_in', 'bytes_out', 'duration', 'src_port', 'dst_port']
        self.load_model()
    
    def prepare_features(self, df):
        """Prépare les features pour le ML"""
        if df.empty:
            return np.array([]).reshape(0, len(self.features))
        
        # Sélectionner et nettoyer les features
        feature_df = df[self.features].copy()
        
        # Remplacer les valeurs manquantes
        feature_df = feature_df.fillna(0)
        
        # Convertir en numérique
        for col in self.features:
            feature_df[col] = pd.to_numeric(feature_df[col], errors='coerce').fillna(0)
        
        return feature_df.values
    
    def train_model(self, df, contamination=0.1):
        """Entraîne le modèle IsolationForest"""
        try:
            features = self.prepare_features(df)
            
            if features.shape[0] < 10:
                raise ValueError("Pas assez de données pour l'entraînement")
            
            # Normalisation
            features_scaled = self.scaler.fit_transform(features)
            
            # Entraînement
            self.model = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )
            self.model.fit(features_scaled)
            
            # Sauvegarde
            self.save_model()
            
            # Métriques d'évaluation
            predictions = self.model.predict(features_scaled)
            anomaly_count = np.sum(predictions == -1)
            
            return {
                'success': True,
                'samples_trained': features.shape[0],
                'anomalies_detected': anomaly_count,
                'anomaly_rate': (anomaly_count / features.shape[0]) * 100
            }
            
        except Exception as e:
            logging.error(f"Erreur entraînement: {e}")
            return {'success': False, 'error': str(e)}
    
    def predict_anomalies(self, df):
        """Prédit les anomalies sur nouvelles données"""
        if self.model is None:
            return np.array([])
        
        try:
            features = self.prepare_features(df)
            if features.shape[0] == 0:
                return np.array([])
            
            features_scaled = self.scaler.transform(features)
            predictions = self.model.predict(features_scaled)
            scores = self.model.decision_function(features_scaled)
            
            # Convertir en scores de risque (0-100)
            risk_scores = ((1 - scores) * 50).clip(0, 100)
            
            return {
                'predictions': predictions,
                'risk_scores': risk_scores,
                'anomalies': predictions == -1
            }
            
        except Exception as e:
            logging.error(f"Erreur prédiction: {e}")
            return {'predictions': np.array([]), 'risk_scores': np.array([]), 'anomalies': np.array([])}
    
    def save_model(self):
        """Sauvegarde le modèle et le scaler"""
        try:
            self.model_path.parent.mkdir(exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            return True
        except Exception as e:
            logging.error(f"Erreur sauvegarde: {e}")
            return False
    
    def load_model(self):
        """Charge le modèle existant"""
        try:
            if self.model_path.exists() and self.scaler_path.exists():
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                return True
        except Exception as e:
            logging.error(f"Erreur chargement: {e}")
        return False
    
    def is_model_trained(self):
        """Vérifie si le modèle est entraîné"""
        return self.model is not None
    
    def get_model_info(self):
        """Informations sur le modèle"""
        if not self.is_model_trained():
            return {'trained': False}
        
        return {
            'trained': True,
            'algorithm': 'IsolationForest',
            'features': self.features,
            'model_file': str(self.model_path)
        }