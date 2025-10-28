# Runbook - Incident Response SOC

## Vue d'ensemble

Ce runbook définit les procédures standardisées de réponse aux incidents de sécurité pour l'équipe SOC. Il couvre la détection, l'analyse, la containment, l'éradication et la récupération.

## Classification des Incidents

### Niveaux de Sévérité

| Sévérité | Description | SLA Response | Escalation |
|----------|-------------|--------------|------------|
| **Critical** | Impact majeur sur les opérations, données sensibles compromises | 15 min | CISO + Management |
| **High** | Impact significatif, systèmes critiques affectés | 1 heure | Security Manager |
| **Medium** | Impact modéré, systèmes non-critiques | 4 heures | Team Lead |
| **Low** | Impact minimal, pas d'urgence | 24 heures | Analyst |

### Types d'Incidents

- **Malware/Ransomware**: Logiciels malveillants détectés
- **Data Breach**: Exfiltration ou exposition de données
- **Phishing**: Tentatives d'hameçonnage
- **DDoS**: Attaques par déni de service
- **Unauthorized Access**: Accès non autorisé aux systèmes
- **Insider Threat**: Menaces internes
- **System Compromise**: Compromission de systèmes

## Processus de Réponse aux Incidents

### Phase 1: Détection et Analyse

#### 1.1 Détection Initiale
```
□ Alerte reçue via SOC Dashboard
□ Vérification de la validité de l'alerte
□ Classification initiale (sévérité/type)
□ Création du ticket incident
□ Notification de l'équipe selon SLA
```

#### 1.2 Analyse Préliminaire
```
□ Collecte des logs pertinents
□ Identification des systèmes affectés
□ Évaluation de l'impact potentiel
□ Détermination de la portée
□ Documentation des observations initiales
```

#### 1.3 Escalation si Nécessaire
```
□ Évaluation du besoin d'escalation
□ Notification des parties prenantes
□ Activation de l'équipe de crise si critique
□ Communication avec le management
```

### Phase 2: Containment

#### 2.1 Containment Immédiat
```
□ Isolation des systèmes compromis
□ Blocage des adresses IP malveillantes
□ Désactivation des comptes compromis
□ Arrêt des processus malveillants
□ Sauvegarde des preuves
```

#### 2.2 Containment à Long Terme
```
□ Application de patches de sécurité
□ Renforcement des contrôles d'accès
□ Mise à jour des règles de firewall
□ Déploiement de signatures de détection
□ Monitoring renforcé
```

### Phase 3: Éradication

#### 3.1 Suppression de la Menace
```
□ Suppression des malwares
□ Fermeture des backdoors
□ Suppression des comptes non autorisés
□ Nettoyage des systèmes compromis
□ Validation de l'éradication
```

#### 3.2 Correction des Vulnérabilités
```
□ Identification des vulnérabilités exploitées
□ Application des correctifs
□ Renforcement de la configuration
□ Mise à jour des systèmes
□ Tests de validation
```

### Phase 4: Récupération

#### 4.1 Restauration des Services
```
□ Restauration depuis les sauvegardes
□ Redémarrage des services
□ Tests de fonctionnement
□ Monitoring intensif
□ Validation de l'intégrité
```

#### 4.2 Retour à la Normale
```
□ Surveillance continue
□ Tests de performance
□ Communication aux utilisateurs
□ Documentation des changements
□ Levée des restrictions temporaires
```

### Phase 5: Post-Incident

#### 5.1 Documentation
```
□ Rapport d'incident détaillé
□ Timeline des événements
□ Actions prises
□ Leçons apprises
□ Recommandations d'amélioration
```

#### 5.2 Amélioration Continue
```
□ Révision des procédures
□ Mise à jour des playbooks
□ Formation de l'équipe
□ Amélioration des outils
□ Tests des procédures
```

## Playbooks Spécifiques

### Playbook 1: Malware/Ransomware

#### Détection
- Alertes antivirus/EDR
- Comportement anormal des systèmes
- Chiffrement non autorisé de fichiers
- Communications vers des C&C

#### Actions Immédiates
1. **Isolation**: Déconnecter le système du réseau
2. **Identification**: Déterminer le type de malware
3. **Scope**: Identifier les autres systèmes affectés
4. **Containment**: Bloquer les communications malveillantes

#### Commandes Utiles
```bash
# Isolation réseau
netsh interface set interface "Ethernet" admin=disable

# Analyse des processus
tasklist /svc
wmic process list full

# Vérification des connexions
netstat -ano
```

### Playbook 2: Phishing

#### Détection
- Emails suspects signalés
- Clics sur liens malveillants
- Tentatives de credential harvesting
- Domaines suspects

#### Actions Immédiates
1. **Blocage**: Bloquer les URLs/domaines malveillants
2. **Quarantine**: Mettre en quarantaine les emails
3. **Reset**: Réinitialiser les mots de passe compromis
4. **Communication**: Alerter les utilisateurs

#### Outils
- Email Security Gateway
- URL Reputation Services
- Password Reset Tools
- User Communication Platform

### Playbook 3: Data Breach

#### Détection
- Accès non autorisé aux données
- Exfiltration de données détectée
- Alertes DLP (Data Loss Prevention)
- Activité anormale sur les bases de données

#### Actions Immédiates
1. **Assessment**: Évaluer la portée de la compromission
2. **Containment**: Stopper l'exfiltration
3. **Legal**: Notifier l'équipe juridique
4. **Compliance**: Préparer les notifications réglementaires

#### Timeline Critique
- **0-1h**: Containment et assessment initial
- **1-24h**: Investigation approfondie
- **24-72h**: Notification aux autorités (GDPR/CCPA)
- **72h+**: Communication publique si nécessaire

### Playbook 4: Compromission de Compte

#### Détection
- Connexions depuis des locations inhabituelles
- Activité en dehors des heures normales
- Échecs d'authentification multiples
- Changements de configuration non autorisés

#### Actions Immédiates
1. **Disable**: Désactiver le compte compromis
2. **Reset**: Réinitialiser les mots de passe
3. **Review**: Examiner l'activité du compte
4. **Audit**: Vérifier les accès et permissions

## Outils et Ressources

### Outils SOC Dashboard
- **Détection**: Alertes ML et règles
- **Investigation**: Log viewer et recherche
- **Containment**: Intégrations avec firewalls/EDR
- **Documentation**: Système de tickets

### Outils Externes
- **SIEM**: Elasticsearch/Splunk
- **EDR**: CrowdStrike/SentinelOne
- **Network**: Wireshark/tcpdump
- **Forensics**: Volatility/Autopsy
- **Threat Intel**: MISP/ThreatConnect

### Contacts d'Urgence

| Rôle | Contact | Disponibilité |
|------|---------|---------------|
| SOC Manager | +33-X-XX-XX-XX-XX | 24/7 |
| CISO | +33-X-XX-XX-XX-XX | Business hours |
| IT Manager | +33-X-XX-XX-XX-XX | 24/7 |
| Legal Team | legal@company.com | Business hours |
| PR Team | pr@company.com | On-call |

## Communication Templates

### Template: Incident Initial

```
OBJET: [URGENT] Incident de Sécurité - [ID_INCIDENT]

Équipe,

Un incident de sécurité a été détecté:

- ID Incident: [ID]
- Sévérité: [SEVERITE]
- Type: [TYPE]
- Systèmes Affectés: [SYSTEMES]
- Heure de Détection: [HEURE]
- Analyste Assigné: [ANALYSTE]

Actions en cours:
- [ACTION_1]
- [ACTION_2]

Prochaine mise à jour dans 30 minutes.

[SIGNATURE]
```

### Template: Mise à Jour

```
OBJET: [UPDATE] Incident [ID_INCIDENT] - [STATUT]

Mise à jour incident [ID]:

Statut: [STATUT]
Progression:
- [PROGRES_1]
- [PROGRES_2]

Actions suivantes:
- [ACTION_SUIVANTE_1]
- [ACTION_SUIVANTE_2]

ETA Résolution: [ETA]

[SIGNATURE]
```

### Template: Résolution

```
OBJET: [RESOLVED] Incident [ID_INCIDENT] - Résolu

L'incident [ID] a été résolu:

- Heure de Résolution: [HEURE]
- Durée Totale: [DUREE]
- Cause Racine: [CAUSE]
- Actions Correctives: [ACTIONS]

Rapport détaillé disponible: [LIEN]

Services restaurés normalement.

[SIGNATURE]
```

## Métriques et KPIs

### Métriques de Performance
- **MTTD** (Mean Time To Detect): < 15 minutes
- **MTTR** (Mean Time To Respond): < 1 heure (Critical)
- **MTTR** (Mean Time To Resolve): < 4 heures (Critical)
- **Taux de Faux Positifs**: < 5%

### Métriques de Qualité
- **Incidents Escaladés**: < 10%
- **SLA Respectés**: > 95%
- **Satisfaction Client**: > 4/5
- **Formation Équipe**: 100% certifiée

## Formation et Certification

### Formation Requise
- **Incident Response**: SANS FOR508
- **Digital Forensics**: SANS FOR500
- **Threat Hunting**: SANS FOR482
- **Malware Analysis**: SANS FOR610

### Exercices Réguliers
- **Tabletop Exercises**: Mensuel
- **Red Team Exercises**: Trimestriel
- **Disaster Recovery**: Semestriel
- **Phishing Simulations**: Mensuel

## Révision et Mise à Jour

Ce runbook doit être révisé:
- **Après chaque incident majeur**
- **Trimestriellement** pour les mises à jour
- **Annuellement** pour la révision complète
- **Lors de changements organisationnels**

---

**Version**: 1.0  
**Dernière Mise à Jour**: 2025-01-15  
**Prochaine Révision**: 2025-04-15  
**Propriétaire**: SOC Team  
**Approbation**: CISO