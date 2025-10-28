"""
Tests unitaires pour AIDetector
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

# Import du module à tester
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.ai_detector import AIDetector

class TestAIDetector:
    
    @pytest.fixture
    def temp_models_dir(self):
        """Crée un répertoire temporaire pour les modèles"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_data(self):
        """Crée des données d'exemple pour les tests"""
        np.random.seed(42)  # Pour la reproductibilité
        
        data = []
        for i in range(100):
            # Données normales
            if i < 80:
                bytes_in = np.random.normal(5000, 1000)
                bytes_out = np.random.normal(2000, 500)
                duration = np.random.normal(30, 10)
                src_port = np.random.randint(1024, 65535)
                dst_port = np.random.choice([80, 443, 22, 53])
            # Données anormales
            else:
                bytes_in = np.random.normal(50000, 10000)  # Beaucoup plus élevé
                bytes_out = np.random.normal(20000, 5000)
                duration = np.random.normal(300, 50)
                src_port = np.random.randint(1024, 65535)
                dst_port = np.random.randint(1, 1024)  # Ports inhabituels
            
            data.append({
                'bytes_in': max(0, bytes_in),
                'bytes_out': max(0, bytes_out),
                'duration': max(1, duration),
                'src_port': src_port,
                'dst_port': dst_port,
                'timestamp': f'2025-01-15 10:{i:02d}:00',
                'src_ip': f'192.168.1.{i%254+1}',
                'dst_ip': '10.0.0.1',
                'protocol': 'TCP',
                'event_type': 'test_event',
                'severity': 'low'
            })
        
        return pd.DataFrame(data)
    
    @pytest.fixture
    def ai_detector(self, temp_models_dir):
        """Crée une instance AIDetector avec répertoire temporaire"""
        detector = AIDetector()
        detector.model_path = temp_models_dir / "anomaly_model.pkl"
        detector.scaler_path = temp_models_dir / "scaler.pkl"
        return detector
    
    def test_prepare_features(self, ai_detector, sample_data):
        """Test de préparation des features"""
        features = ai_detector.prepare_features(sample_data)
        
        assert features.shape[0] == len(sample_data)
        assert features.shape[1] == len(ai_detector.features)
        assert not np.isnan(features).any()
    
    def test_prepare_features_empty_data(self, ai_detector):
        """Test de préparation avec données vides"""
        empty_df = pd.DataFrame()
        features = ai_detector.prepare_features(empty_df)
        
        assert features.shape[0] == 0
        assert features.shape[1] == len(ai_detector.features)
    
    def test_prepare_features_missing_columns(self, ai_detector):
        """Test avec colonnes manquantes"""
        incomplete_data = pd.DataFrame({
            'bytes_in': [1000, 2000],
            'bytes_out': [500, 1000]
            # Colonnes manquantes: duration, src_port, dst_port
        })
        
        # Devrait lever une exception ou gérer gracieusement
        try:
            features = ai_detector.prepare_features(incomplete_data)
            # Si pas d'exception, vérifier que les valeurs manquantes sont gérées
            assert features.shape[0] == 2
        except KeyError:
            # C'est acceptable si le code lève une exception pour colonnes manquantes
            pass
    
    def test_train_model_success(self, ai_detector, sample_data):
        """Test d'entraînement réussi du modèle"""
        result = ai_detector.train_model(sample_data, contamination=0.2)
        
        assert result['success'] is True
        assert result['samples_trained'] == len(sample_data)
        assert result['anomalies_detected'] > 0
        assert 0 <= result['anomaly_rate'] <= 100
        assert ai_detector.is_model_trained()
    
    def test_train_model_insufficient_data(self, ai_detector):
        """Test d'entraînement avec données insuffisantes"""
        small_data = pd.DataFrame({
            'bytes_in': [1000],
            'bytes_out': [500],
            'duration': [30],
            'src_port': [12345],
            'dst_port': [80]
        })
        
        result = ai_detector.train_model(small_data)
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_predict_anomalies_without_model(self, ai_detector, sample_data):
        """Test de prédiction sans modèle entraîné"""
        predictions = ai_detector.predict_anomalies(sample_data)
        
        # Devrait retourner des arrays vides
        assert len(predictions.get('predictions', [])) == 0
        assert len(predictions.get('risk_scores', [])) == 0
        assert len(predictions.get('anomalies', [])) == 0
    
    def test_predict_anomalies_with_model(self, ai_detector, sample_data):
        """Test de prédiction avec modèle entraîné"""
        # D'abord entraîner le modèle
        train_result = ai_detector.train_model(sample_data, contamination=0.2)
        assert train_result['success']
        
        # Ensuite faire des prédictions
        predictions = ai_detector.predict_anomalies(sample_data)
        
        assert len(predictions['predictions']) == len(sample_data)
        assert len(predictions['risk_scores']) == len(sample_data)
        assert len(predictions['anomalies']) == len(sample_data)
        
        # Vérifier que les scores de risque sont dans la bonne plage
        risk_scores = predictions['risk_scores']
        assert all(0 <= score <= 100 for score in risk_scores)
        
        # Vérifier qu'il y a des anomalies détectées
        anomalies = predictions['anomalies']
        assert any(anomalies)  # Au moins une anomalie
    
    def test_save_and_load_model(self, ai_detector, sample_data):
        """Test de sauvegarde et chargement du modèle"""
        # Entraîner et sauvegarder
        train_result = ai_detector.train_model(sample_data)
        assert train_result['success']
        
        # Créer une nouvelle instance et charger
        new_detector = AIDetector()
        new_detector.model_path = ai_detector.model_path
        new_detector.scaler_path = ai_detector.scaler_path
        
        load_success = new_detector.load_model()
        assert load_success
        assert new_detector.is_model_trained()
        
        # Vérifier que les prédictions sont cohérentes
        pred1 = ai_detector.predict_anomalies(sample_data.head(10))
        pred2 = new_detector.predict_anomalies(sample_data.head(10))
        
        np.testing.assert_array_almost_equal(
            pred1['risk_scores'], 
            pred2['risk_scores'], 
            decimal=2
        )
    
    def test_get_model_info(self, ai_detector, sample_data):
        """Test des informations du modèle"""
        # Avant entraînement
        info_before = ai_detector.get_model_info()
        assert info_before['trained'] is False
        
        # Après entraînement
        ai_detector.train_model(sample_data)
        info_after = ai_detector.get_model_info()
        
        assert info_after['trained'] is True
        assert info_after['algorithm'] == 'IsolationForest'
        assert 'features' in info_after
        assert 'model_file' in info_after
    
    def test_predict_empty_data(self, ai_detector, sample_data):
        """Test de prédiction avec données vides"""
        # Entraîner d'abord
        ai_detector.train_model(sample_data)
        
        # Prédire sur données vides
        empty_df = pd.DataFrame()
        predictions = ai_detector.predict_anomalies(empty_df)
        
        assert len(predictions.get('predictions', [])) == 0
        assert len(predictions.get('risk_scores', [])) == 0
        assert len(predictions.get('anomalies', [])) == 0
    
    def test_contamination_parameter(self, ai_detector, sample_data):
        """Test de l'effet du paramètre contamination"""
        # Test avec contamination faible
        result_low = ai_detector.train_model(sample_data, contamination=0.05)
        predictions_low = ai_detector.predict_anomalies(sample_data)
        anomalies_low = np.sum(predictions_low['anomalies'])
        
        # Test avec contamination élevée
        result_high = ai_detector.train_model(sample_data, contamination=0.3)
        predictions_high = ai_detector.predict_anomalies(sample_data)
        anomalies_high = np.sum(predictions_high['anomalies'])
        
        # Plus de contamination devrait détecter plus d'anomalies
        assert anomalies_high >= anomalies_low

if __name__ == "__main__":
    pytest.main([__file__, "-v"])