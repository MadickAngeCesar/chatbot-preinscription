# 🚀 Démarrage Rapide - Nouvelle Architecture

## ⏱️ En 5 minutes

### 1. Vérifier l'installation

```powershell
# Vérifier Python (3.8+)
python --version

# Vérifier les dépendances
pip install -r requirements.txt
```

### 2. Lancer l'application

```powershell
# Lancer la NOUVELLE version
python app_new.py
```

Vous devriez voir :

```
🚀 Chatbot de Préinscription Universitaire v3.0
============================================================
📊 Base de données: OK
🔐 Middlewares: OK
📋 Routes: OK
🌐 Serveur: http://127.0.0.1:5000
💬 Chat: http://127.0.0.1:5000/chat
📝 Formulaire: http://127.0.0.1:5000/preinscription
============================================================

✨ Application prête ! Architecture MVC avec Controllers
```

### 3. Tester l'API

Ouvrez un autre terminal PowerShell :

```powershell
# Test 1: Health check
curl http://localhost:5000/api/health

# Test 2: Liste des établissements
curl http://localhost:5000/api/etablissements

# Test 3: Liste des filières
curl http://localhost:5000/api/filieres
```

### 4. Tester l'interface web

Ouvrez votre navigateur :

- **Page d'accueil** : http://localhost:5000/
- **Inscription** : http://localhost:5000/register
- **Connexion** : http://localhost:5000/login
- **Chat** : http://localhost:5000/chat (après connexion)

---

## 📖 Tester les fonctionnalités

### 1. Créer un compte

**Via l'interface web :**
1. Aller sur http://localhost:5000/register
2. Remplir le formulaire
3. Cliquer sur "S'inscrire"

**Via l'API :**
```powershell
$body = @{
    nom = "Doe"
    prenom = "John"
    email = "john@example.com"
    password = "Secure123"
    telephone = "+237 6XX XXX XXX"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/register" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

### 2. Se connecter

**Via l'API :**
```powershell
$body = @{
    email = "john@example.com"
    password = "Secure123"
} | ConvertTo-Json

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
  -Method Post `
  -Body $body `
  -ContentType "application/json" `
  -WebSession $session
```

### 3. Envoyer un message au chatbot

```powershell
$body = @{
    message = "Quels sont les programmes disponibles ?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/message" `
  -Method Post `
  -Body $body `
  -ContentType "application/json" `
  -WebSession $session
```

---

## 📊 Consulter les logs

```powershell
# Voir les logs en temps réel
Get-Content logs\app.log -Wait -Tail 50

# Filtrer les erreurs
Select-String -Path logs\app.log -Pattern "ERROR"

# Filtrer les actions utilisateur
Select-String -Path logs\app.log -Pattern "USER_ACTION"

# Filtrer les tentatives d'authentification
Select-String -Path logs\app.log -Pattern "AUTH_ATTEMPT"
```

---

## 🔍 Comparer avec l'ancienne version

### Lancer l'ancienne version

```powershell
# Lancer l'ANCIENNE version
python app.py
```

### Comparer les endpoints

Les endpoints sont **IDENTIQUES** entre les deux versions :

| Endpoint | Ancienne | Nouvelle | Compatible |
|----------|----------|----------|------------|
| `POST /api/auth/register` | ✅ | ✅ | 100% |
| `POST /api/auth/login` | ✅ | ✅ | 100% |
| `POST /api/message` | ✅ | ✅ | 100% |
| `POST /api/preinscription` | ✅ | ✅ | 100% |
| `GET /api/etablissements` | ✅ | ✅ | 100% |
| `GET /api/filieres` | ✅ | ✅ | 100% |

**Format des réponses identique :**
```json
{
  "success": true,
  "message": "...",
  "data": {...}
}
```

---

## 🎯 Checklist de migration

### Avant de migrer en production

- [ ] Tester tous les endpoints avec l'ancienne version
- [ ] Tester tous les endpoints avec la nouvelle version
- [ ] Comparer les réponses (doivent être identiques)
- [ ] Tester l'interface web complètement
- [ ] Vérifier les logs (aucune erreur)
- [ ] Tester l'upload de fichiers
- [ ] Tester le chatbot
- [ ] Tester les permissions (admin, étudiant, visiteur)

### Migration

- [ ] Sauvegarder `app.py` → `app_old.py`
- [ ] Sauvegarder la base de données
- [ ] Renommer `app_new.py` → `app.py`
- [ ] Supprimer `route/api.py` et `route/auth_api.py`
- [ ] Lancer `python app.py`
- [ ] Vérifier les logs
- [ ] Tester les fonctionnalités critiques

---

## ⚡ Commandes utiles

```powershell
# Lancer l'application
python app_new.py

# Lancer en mode développement avec rechargement auto
$env:FLASK_ENV="development"; python app_new.py

# Tester tous les endpoints
.\test_all_endpoints.ps1  # Si créé

# Nettoyer les logs
Remove-Item logs\*.log

# Nettoyer les uploads de test
Remove-Item uploads\* -Exclude .gitkeep

# Installer les dépendances
pip install -r requirements.txt

# Mettre à jour les dépendances
pip install --upgrade -r requirements.txt

# Créer un environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🐛 Troubleshooting

### Erreur : "Module not found"

```powershell
# Vérifier les dépendances
pip list

# Réinstaller
pip install -r requirements.txt
```

### Erreur : "Address already in use"

```powershell
# Trouver le processus sur le port 5000
netstat -ano | findstr :5000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

### Erreur : "Database is locked"

```powershell
# Fermer toutes les connexions
# Redémarrer l'application
```

### Les logs ne s'affichent pas

```powershell
# Vérifier que le dossier existe
Test-Path logs

# Créer le dossier si nécessaire
New-Item -ItemType Directory -Path logs -Force
```

### L'authentification ne fonctionne pas

```powershell
# Vérifier les cookies dans le navigateur
# Vider le cache et les cookies
# Redémarrer le navigateur
```

---

## 📚 Documentation complète

| Document | Description |
|----------|-------------|
| `ARCHITECTURE-SUMMARY.md` | ⭐ Résumé complet du travail |
| `doc/API-ARCHITECTURE.md` | Architecture détaillée avec exemples |
| `MIGRATION-NEW-ARCHITECTURE.md` | Guide de migration et FAQ |
| `doc/diagram/architecture-new.mmd` | Diagramme d'architecture |
| `doc/diagram/request-flow.mmd` | Flux de requête |

---

## ✅ Tout fonctionne ?

Si vous voyez :

```
✅ Base de données initialisée avec succès!
✅ Middleware d'authentification initialisé
✅ Middleware de validation initialisé
✅ Middleware de logging initialisé
✅ Gestionnaires d'erreurs initialisés
✅ Routes enregistrées avec succès

✨ Application prête ! Architecture MVC avec Controllers
```

**Félicitations ! 🎉 L'application fonctionne parfaitement.**

---

## 🚀 Prochaines étapes

1. **Tester l'application** : Créer un compte, chat, préinscription
2. **Consulter la documentation** : `doc/API-ARCHITECTURE.md`
3. **Migrer en production** : Suivre `MIGRATION-NEW-ARCHITECTURE.md`
4. **Ajouter des tests** : Créer des tests unitaires
5. **Monitoring** : Configurer un système de monitoring des logs

---

**Bon développement ! 💻**
