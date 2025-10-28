"""
Script de déploiement automatisé pour SOC Dashboard
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse
import json
from datetime import datetime

class SOCDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "deploy_config.json"
        self.load_config()
    
    def load_config(self):
        """Charge la configuration de déploiement"""
        default_config = {
            "environments": {
                "development": {
                    "host": "localhost",
                    "port": 8501,
                    "debug": True,
                    "auto_reload": True
                },
                "staging": {
                    "host": "0.0.0.0",
                    "port": 8501,
                    "debug": False,
                    "auto_reload": False
                },
                "production": {
                    "host": "0.0.0.0", 
                    "port": 8501,
                    "debug": False,
                    "auto_reload": False,
                    "ssl_cert": "/path/to/cert.pem",
                    "ssl_key": "/path/to/key.pem"
                }
            },
            "docker": {
                "image_name": "soc-dashboard",
                "container_name": "soc-dashboard-app",
                "network": "soc-network"
            },
            "backup": {
                "enabled": True,
                "retention_days": 30,
                "s3_bucket": "soc-dashboard-backups"
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_requirements(self):
        """Vérifie les prérequis"""
        print("🔍 Vérification des prérequis...")
        
        # Python version
        if sys.version_info < (3, 10):
            print("❌ Python 3.10+ requis")
            return False
        
        # Docker (optionnel)
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            print("✅ Docker disponible")
        except:
            print("⚠️ Docker non disponible (optionnel)")
        
        # Répertoires requis
        required_dirs = ["data", "models", "logs", "exports"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(exist_ok=True)
                print(f"📁 Créé: {dir_name}/")
        
        print("✅ Prérequis vérifiés")
        return True
    
    def install_dependencies(self, env="development"):
        """Installe les dépendances"""
        print("📦 Installation des dépendances...")
        
        try:
            # Créer environnement virtuel si nécessaire
            venv_path = self.project_root / "venv"
            if not venv_path.exists():
                subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
                print("✅ Environnement virtuel créé")
            
            # Activer et installer
            if os.name == 'nt':  # Windows
                pip_path = venv_path / "Scripts" / "pip"
            else:  # Unix/Linux
                pip_path = venv_path / "bin" / "pip"
            
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
            subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
            
            # Dépendances de développement
            if env == "development":
                dev_packages = ["pytest", "black", "flake8", "mypy"]
                subprocess.run([str(pip_path), "install"] + dev_packages, check=True)
            
            print("✅ Dépendances installées")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur installation: {e}")
            return False
    
    def setup_environment(self, env="development"):
        """Configure l'environnement"""
        print(f"⚙️ Configuration environnement: {env}")
        
        # Copier .env.example vers .env si nécessaire
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_file.exists() and env_example.exists():
            shutil.copy2(env_example, env_file)
            print("✅ Fichier .env créé depuis .env.example")
        
        # Initialiser les données si nécessaire
        data_dir = self.project_root / "data"
        if not (data_dir / "logs.csv").exists():
            print("📊 Initialisation des données...")
            try:
                subprocess.run([sys.executable, "seed_data.py"], check=True)
                print("✅ Données initialisées")
            except subprocess.CalledProcessError:
                print("⚠️ Erreur initialisation données")
        
        print(f"✅ Environnement {env} configuré")
    
    def deploy_local(self, env="development"):
        """Déploiement local"""
        print(f"🚀 Déploiement local ({env})...")
        
        if not self.check_requirements():
            return False
        
        if not self.install_dependencies(env):
            return False
        
        self.setup_environment(env)
        
        # Configuration Streamlit
        config = self.config["environments"][env]
        
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "streamlit_app/main.py",
            f"--server.port={config['port']}",
            f"--server.address={config['host']}"
        ]
        
        if not config.get("debug", False):
            cmd.extend(["--logger.level", "warning"])
        
        if not config.get("auto_reload", True):
            cmd.append("--server.fileWatcherType=none")
        
        print(f"🌐 Lancement sur http://{config['host']}:{config['port']}")
        print("Commande:", " ".join(cmd))
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n👋 Arrêt de l'application")
        
        return True
    
    def deploy_docker(self, env="production"):
        """Déploiement Docker"""
        print(f"🐳 Déploiement Docker ({env})...")
        
        docker_config = self.config["docker"]
        
        try:
            # Build de l'image
            print("🔨 Construction de l'image Docker...")
            subprocess.run([
                "docker", "build", 
                "-t", f"{docker_config['image_name']}:latest",
                "."
            ], check=True)
            
            # Arrêter le container existant
            try:
                subprocess.run([
                    "docker", "stop", docker_config['container_name']
                ], capture_output=True)
                subprocess.run([
                    "docker", "rm", docker_config['container_name']
                ], capture_output=True)
            except:
                pass
            
            # Lancer le nouveau container
            print("🚀 Lancement du container...")
            env_config = self.config["environments"][env]
            
            cmd = [
                "docker", "run", "-d",
                "--name", docker_config['container_name'],
                "-p", f"{env_config['port']}:8501",
                "-v", f"{self.project_root}/data:/app/data",
                "-v", f"{self.project_root}/models:/app/models",
                "-v", f"{self.project_root}/logs:/app/logs",
                "--network", docker_config['network'],
                f"{docker_config['image_name']}:latest"
            ]
            
            subprocess.run(cmd, check=True)
            
            print(f"✅ Container déployé sur port {env_config['port']}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur déploiement Docker: {e}")
            return False
    
    def deploy_compose(self):
        """Déploiement avec docker-compose"""
        print("🐳 Déploiement docker-compose...")
        
        try:
            # Arrêter les services existants
            subprocess.run(["docker-compose", "down"], capture_output=True)
            
            # Lancer les services
            subprocess.run(["docker-compose", "up", "-d", "--build"], check=True)
            
            print("✅ Stack déployée avec docker-compose")
            print("🌐 Services disponibles:")
            print("  - SOC Dashboard: http://localhost:8501")
            print("  - Elasticsearch: http://localhost:9200")
            print("  - Kibana: http://localhost:5601")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur docker-compose: {e}")
            return False
    
    def backup_data(self):
        """Sauvegarde les données"""
        print("💾 Sauvegarde des données...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / "backups" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers à sauvegarder
        files_to_backup = [
            "data/",
            "models/",
            ".env"
        ]
        
        try:
            for item in files_to_backup:
                source = self.project_root / item
                if source.exists():
                    if source.is_dir():
                        shutil.copytree(source, backup_dir / item)
                    else:
                        shutil.copy2(source, backup_dir)
            
            print(f"✅ Sauvegarde créée: {backup_dir}")
            return str(backup_dir)
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return None
    
    def run_tests(self):
        """Exécute les tests"""
        print("🧪 Exécution des tests...")
        
        try:
            # Tests unitaires
            result = subprocess.run(["python", "-m", "pytest", "tests/", "-v"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Tests réussis")
                return True
            else:
                print("❌ Tests échoués")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Erreur tests: {e}")
            return False
    
    def health_check(self, host="localhost", port=8501):
        """Vérifie la santé de l'application"""
        print("🏥 Vérification de santé...")
        
        try:
            import requests
            
            # Test de l'endpoint de santé
            response = requests.get(f"http://{host}:{port}/_stcore/health", timeout=10)
            
            if response.status_code == 200:
                print("✅ Application en bonne santé")
                return True
            else:
                print(f"❌ Problème de santé: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur health check: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Déploiement SOC Dashboard")
    parser.add_argument("action", choices=[
        "local", "docker", "compose", "backup", "test", "health"
    ], help="Action à exécuter")
    parser.add_argument("--env", default="development", 
                       choices=["development", "staging", "production"],
                       help="Environnement cible")
    parser.add_argument("--host", default="localhost", help="Host pour health check")
    parser.add_argument("--port", type=int, default=8501, help="Port pour health check")
    
    args = parser.parse_args()
    
    deployer = SOCDeployer()
    
    if args.action == "local":
        success = deployer.deploy_local(args.env)
    elif args.action == "docker":
        success = deployer.deploy_docker(args.env)
    elif args.action == "compose":
        success = deployer.deploy_compose()
    elif args.action == "backup":
        success = deployer.backup_data() is not None
    elif args.action == "test":
        success = deployer.run_tests()
    elif args.action == "health":
        success = deployer.health_check(args.host, args.port)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()