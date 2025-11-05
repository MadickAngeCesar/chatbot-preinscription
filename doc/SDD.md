
# SDD — Software Design Document (Document de Conception)

Version: 1.0

Date: 2025-11-04

Projet: Chatbot de Préinscription Universitaire

Auteur: Madick Ange César

## 1. Introduction

### 1.1 Objectif
Ce document décrit l'architecture logicielle et la conception détaillée du système. Il sert de guide pour l'implémentation, les tests et le déploiement.

### 1.2 Portée
Couverture : architecture globale, composants backend et frontend, modèles de données, API, séquences d'interaction, sécurité, déploiement et tests.

## 2. Architecture globale

L'application suit une architecture client-serveur simple :

- Client : pages HTML/JS (templates `index.html`, `chat.html`, `preinscription.html`), fichiers statiques dans `static/`.
- Serveur : application Flask (fichier `app.py`) exposant endpoints REST et rendant les templates.
- Stockage : SQLite dans `database/`.
- Module IA : dossier `model/` contenant le modèle de réponse (ex: `chatbot_model.py`).

Diagramme (haut-niveau):

Client (browser) <--> Flask API endpoints <--> Model (local) + SQLite

## 3. Composants détaillés

### 3.1 Backend (Flask)

- `app.py` : point d'entrée. Configure routes et blueprints.
- Endpoints clés :
	- GET `/` -> page d'accueil
	- GET `/chat` -> interface chat
	- POST `/api/message` -> reçoit {message, session_id} retourne {response, meta}
	- POST `/api/preinscription` -> reçoit données du formulaire, valide, enregistre
	- GET `/api/preinscriptions` -> liste (admin)

Implémentation : chaque endpoint valide les entrées, appelle le module IA si nécessaire, et persiste les messages/données.

### 3.2 Module IA (`model/`)

- Composants :
	- `chatbot_model.py` : API interne exposant `respond(message, session_id)` ; peut encapsuler un modèle statistique, règle heuristique ou un appel vers un service local.
	- `nlp_utils.py` : utilitaires de prétraitement (tokenize, normaliser, détecter intent).

Comportement attendu : le module prend un message et retourne un texte, éventuellement un `intent` et des `entities`.

### 3.3 Base de données (SQLite)

Schéma proposé (SQL simplifié) :

Table `preinscriptions` (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	nom TEXT NOT NULL,
	prenom TEXT NOT NULL,
	email TEXT NOT NULL,
	telephone TEXT,
	programme TEXT NOT NULL,
	date_soumission DATETIME DEFAULT CURRENT_TIMESTAMP,
	statut TEXT DEFAULT 'nouveau',
	meta_json TEXT
)

Table `messages` (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	session_id TEXT,
	role TEXT CHECK(role IN ('user','bot')),
	contenu TEXT,
	timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)

Table `users` (optionnel) pour l'admin : id, username, password_hash, role

### 3.4 Frontend

- HTML templates : rendent l'interface et incluent `static/js/script.js` pour la logique client (AJAX vers `/api/message`).
- CSS : `static/css/style.css` pour le responsive.

## 4. Interfaces et API

### 4.1 POST /api/message
- Request JSON : { "session_id": "<id>", "message": "Bonjour" }
- Response JSON : { "response": "Bonjour, comment puis-je vous aider ?", "intent": "info_programme", "entities": {} }

Validation : le serveur vérifie la présence des champs et leur type.

### 4.2 POST /api/preinscription
- Request JSON form-data ou JSON contenant les champs du formulaire.
- Response : 200 OK + {"id": <preinscription_id>, "status":"saved"}

### 4.3 GET /api/preinscriptions
- Response : liste JSON des préinscriptions (protégée ou accessible localement selon configuration).

## 5. Séquences d'interaction

Scénario principal : conversation puis préinscription

1. L'utilisateur envoie un message via l'UI.
2. Le client JS envoie POST `/api/message`.
3. Le serveur enregistre l'entrée dans `messages` (role='user').
4. Le serveur appelle `model.respond()` et obtient une réponse.
5. Le serveur enregistre la réponse dans `messages` (role='bot') et renvoie la réponse au client.
6. Si l'intent est `preinscription`, le client propose d'ouvrir le formulaire.
7. L'utilisateur soumet `/api/preinscription` ; le serveur valide et insère en `preinscriptions`.

## 6. Conception détaillée et décisions

### 6.1 Gestion des sessions
- Utiliser `session` de Flask (cookie signé) pour stocker `session_id` côté client. Alternativement, générer un `uuid` côté client et le renvoyer avec chaque message.

### 6.2 Gestion des erreurs
- Tous les endpoints renvoient un code HTTP approprié (400, 401, 500) et un JSON {"error":"message"}.

### 6.3 Sécurité
- Input validation et sanitization ; utiliser des requêtes paramétrées pour SQLite (prévenir SQL injection).
- Stocker les mots de passe admin hachés (bcrypt) si on implémente `users`.
- Configurer `SECRET_KEY` Flask via variable d'environnement.

### 6.4 Logs et monitoring
- Logger Flask pour les erreurs et événements importants ; logs persistés localement.

## 7. Tests et validation

### 7.1 Tests unitaires
- Tester endpoints REST (happy path + erreurs) via pytest + flask test client.
- Tester validations du formulaire.

### 7.2 Tests d'intégration
- Scénario conversation complet : envoyer message, vérifier insertion dans `messages`, vérification réponse attendue.

### 7.3 Critères d'acceptation
- Les endpoints retournent les réponses attendues ; les données sont insérées en DB.

## 8. Déploiement

### 8.1 En local (développement)
- Créer venv, installer `pip install -r requirements.txt`, initialiser DB `python init_db.py`, lancer `flask run`.

### 8.2 En production (suggestion)
- Utiliser un WSGI server (gunicorn) derrière un reverse-proxy (nginx) ; déployer la base SQLite sur un stockage persistant ou migrer vers PostgreSQL si besoin de concurrence/scale.

## 9. Dépendances
- Python 3.8+
- Flask
- pytest (pour tests)
- sqlite3 (inclus dans Python)

## 10. Fichiers et structure attendus

- `app.py` — serveur Flask
- `init_db.py` — script de création du schéma
- `model/chatbot_model.py` — logique IA
- `templates/*.html` — interfaces
- `static/js/script.js`, `static/css/style.css`

## 11. Extensions futures
- Authentification complète, interface d'administration, stockage cloud, modèle IA distant, file attachments et validation avancée des pièces jointes.

---

Fin du SDD (v1.0)
