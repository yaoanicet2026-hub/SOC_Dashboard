# SOC Dashboard Makefile

.PHONY: help install run test clean lint format docker

# Variables
PYTHON := python3
PIP := pip3
STREAMLIT := streamlit
PYTEST := pytest

help: ## Affiche l'aide
	@echo "SOC Dashboard - Commandes disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installation complète
	@echo "🔧 Installation des dépendances..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "📝 Création du fichier .env..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "📊 Initialisation des données..."
	$(PYTHON) seed_data.py
	@echo "✅ Installation terminée!"

install-dev: install ## Installation avec dépendances de développement
	$(PIP) install pytest pytest-cov black flake8 mypy

run: ## Lance l'application Streamlit
	@echo "🚀 Lancement du SOC Dashboard..."
	$(STREAMLIT) run streamlit_app/main.py --server.port 8501

run-debug: ## Lance en mode debug
	@echo "🐛 Lancement en mode debug..."
	$(STREAMLIT) run streamlit_app/main.py --server.port 8501 --logger.level debug

test: ## Lance les tests unitaires
	@echo "🧪 Exécution des tests..."
	$(PYTEST) tests/ -v --tb=short

test-coverage: ## Tests avec couverture de code
	@echo "📊 Tests avec couverture..."
	$(PYTEST) tests/ --cov=utils --cov=services --cov-report=html --cov-report=term

lint: ## Vérification du code avec flake8
	@echo "🔍 Vérification du code..."
	flake8 utils/ services/ streamlit_app/ --max-line-length=100 --ignore=E203,W503

format: ## Formatage du code avec black
	@echo "✨ Formatage du code..."
	black utils/ services/ streamlit_app/ tests/ --line-length=100

type-check: ## Vérification des types avec mypy
	@echo "🔍 Vérification des types..."
	mypy utils/ services/ --ignore-missing-imports

clean: ## Nettoyage des fichiers temporaires
	@echo "🧹 Nettoyage..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/

seed-data: ## Régénère les données de test
	@echo "📊 Génération des données..."
	$(PYTHON) seed_data.py

train-model: ## Entraîne le modèle ML
	@echo "🤖 Entraînement du modèle..."
	$(PYTHON) -c "from utils.ai_detector import AIDetector; from utils.data_loader import DataLoader; d=DataLoader(); a=AIDetector(); print(a.train_model(d.load_logs()))"

backup: ## Sauvegarde des données et modèles
	@echo "💾 Sauvegarde..."
	mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	cp -r data/ backups/$(shell date +%Y%m%d_%H%M%S)/
	cp -r models/ backups/$(shell date +%Y%m%d_%H%M%S)/
	cp .env backups/$(shell date +%Y%m%d_%H%M%S)/ 2>/dev/null || true

docker-build: ## Construction de l'image Docker
	@echo "🐳 Construction Docker..."
	docker build -t soc-dashboard:latest .

docker-run: ## Lance le container Docker
	@echo "🐳 Lancement Docker..."
	docker run -p 8501:8501 -v $(PWD)/data:/app/data soc-dashboard:latest

docker-compose: ## Lance avec docker-compose
	@echo "🐳 Lancement docker-compose..."
	docker-compose up -d

security-scan: ## Scan de sécurité des dépendances
	@echo "🔒 Scan de sécurité..."
	$(PIP) install safety
	safety check

performance-test: ## Test de performance
	@echo "⚡ Test de performance..."
	$(PYTHON) -c "
import time
from utils.data_loader import DataLoader
from utils.ai_detector import AIDetector

print('Test de performance...')
start = time.time()

# Test DataLoader
dl = DataLoader()
logs = dl.load_logs()
print(f'DataLoader: {len(logs)} logs en {time.time()-start:.2f}s')

# Test AIDetector
if not logs.empty:
    ai = AIDetector()
    start_ai = time.time()
    result = ai.train_model(logs)
    print(f'AIDetector: Entraînement en {time.time()-start_ai:.2f}s')

print(f'Total: {time.time()-start:.2f}s')
"

docs: ## Génère la documentation
	@echo "📚 Génération de la documentation..."
	@echo "Architecture: docs/architecture.md"
	@echo "Intégration ELK: docs/how_to_connect_elk.md"
	@echo "README: README.md"

check-deps: ## Vérifie les dépendances
	@echo "📦 Vérification des dépendances..."
	$(PIP) check
	$(PIP) list --outdated

update-deps: ## Met à jour les dépendances
	@echo "⬆️ Mise à jour des dépendances..."
	$(PIP) list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 $(PIP) install -U

dev-setup: install-dev ## Configuration complète pour développement
	@echo "🛠️ Configuration développement..."
	pre-commit install 2>/dev/null || echo "pre-commit non disponible"
	@echo "✅ Environnement de développement prêt!"

prod-check: lint test security-scan ## Vérifications avant production
	@echo "🚀 Vérifications production..."
	@echo "✅ Code vérifié, tests passés, sécurité OK"

status: ## Affiche le statut du projet
	@echo "📊 Statut du projet SOC Dashboard:"
	@echo ""
	@echo "📁 Fichiers de données:"
	@ls -la data/ 2>/dev/null || echo "  Aucun fichier de données"
	@echo ""
	@echo "🤖 Modèles ML:"
	@ls -la models/ 2>/dev/null || echo "  Aucun modèle entraîné"
	@echo ""
	@echo "📋 Tests:"
	@$(PYTEST) tests/ --tb=no -q 2>/dev/null || echo "  Tests non exécutés"
	@echo ""
	@echo "🔧 Configuration:"
	@if [ -f .env ]; then echo "  ✅ Fichier .env présent"; else echo "  ❌ Fichier .env manquant"; fi

# Commandes de développement rapide
dev: install-dev run-debug ## Installation dev + lancement debug

quick-test: ## Tests rapides (sans couverture)
	$(PYTEST) tests/ -x --tb=short

# Commandes de déploiement
deploy-prep: clean lint test ## Préparation pour déploiement
	@echo "📦 Préparation déploiement..."
	@echo "✅ Prêt pour déploiement"

# Aide détaillée
help-detailed: ## Aide détaillée avec exemples
	@echo "SOC Dashboard - Guide d'utilisation détaillé"
	@echo ""
	@echo "🚀 Démarrage rapide:"
	@echo "  make install    # Installation complète"
	@echo "  make run        # Lancement de l'application"
	@echo ""
	@echo "🛠️ Développement:"
	@echo "  make dev        # Setup développement + debug"
	@echo "  make test       # Tests unitaires"
	@echo "  make lint       # Vérification code"
	@echo ""
	@echo "📊 Données:"
	@echo "  make seed-data  # Régénérer données test"
	@echo "  make train-model # Entraîner modèle ML"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build # Construire image"
	@echo "  make docker-run   # Lancer container"