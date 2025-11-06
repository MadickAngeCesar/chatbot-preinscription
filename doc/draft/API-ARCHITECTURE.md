# Architecture API - Chatbot de Préinscription

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Structure des dossiers](#structure-des-dossiers)
3. [Architecture MVC + Controllers](#architecture-mvc--controllers)
4. [Middlewares](#middlewares)
5. [Contrôleurs](#contrôleurs)
6. [Routes](#routes)
7. [Flux de requête](#flux-de-requête)
8. [Exemples d'utilisation](#exemples-dutilisation)
9. [Bonnes pratiques](#bonnes-pratiques)

---

## Vue d'ensemble

L'application utilise une **architecture MVC (Model-View-Controller) améliorée** avec une couche de **contrôleurs séparés** et des **middlewares** pour une séparation claire des responsabilités.

### Principes architecturaux

- **Separation of Concerns** : Chaque composant a une responsabilité unique
- **DRY (Don't Repeat Yourself)** : Code réutilisable via les middlewares et contrôleurs
- **Single Responsibility Principle** : Une fonction = une tâche
- **Dependency Injection** : Les dépendances sont injectées, pas créées
- **Testabilité** : Chaque couche peut être testée indépendamment

---

## Structure des dossiers

```
chatbot-preinscription/
│
├── app_new.py                    # Point d'entrée de l'application
├── requirements.txt              # Dépendances Python
│
├── middleware/                   # 🛡️ MIDDLEWARES
│   ├── __init__.py              # Exports des middlewares
│   ├── auth_middleware.py       # Authentification et sessions
│   ├── validation_middleware.py # Validation des données
│   ├── logging_middleware.py    # Logging et monitoring
│   └── error_handler.py         # Gestion centralisée des erreurs
│
├── controllers/                  # 🎮 CONTRÔLEURS (Business Logic)
│   ├── __init__.py
│   ├── auth_controller.py       # Logique d'authentification
│   ├── chat_controller.py       # Logique du chatbot
│   ├── preinscription_controller.py  # Logique préinscriptions
│   ├── etablissement_controller.py   # Logique établissements
│   └── filiere_controller.py    # Logique filières
│
├── route/                        # 🚦 ROUTES (HTTP Routing)
│   ├── __init__.py
│   ├── auth_routes.py           # Routes d'authentification
│   └── api_routes.py            # Routes API principales
│
├── model/                        # 🤖 MODÈLES (IA et Data)
│   ├── gemini_chatbot.py        # Intégration Gemini AI
│   └── gemini_config.py         # Configuration Gemini
│
├── services/                     # 🔧 SERVICES (couche existante MVC)
│   ├── auth_service.py
│   ├── user_service.py
│   └── ...
│
├── utils/                        # 🛠️ UTILITAIRES
│   ├── database.py
│   ├── validators.py
│   └── ...
│
├── templates/                    # 📄 VUES (HTML)
│   ├── index.html
│   ├── chat.html
│   └── ...
│
├── static/                       # 🎨 ASSETS
│   ├── css/
│   ├── js/
│   └── img/
│
├── database/                     # 💾 BASE DE DONNÉES
│   └── chatbot.db
│
├── uploads/                      # 📁 FICHIERS UPLOADÉS
│
└── logs/                         # 📝 LOGS
    └── app.log
```

---

## Architecture MVC + Controllers

### Schéma de l'architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                               │
│              (Browser, Mobile App, API Client)               │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Request
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK APP                               │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              🛡️ MIDDLEWARES                        │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │  1. Logging Middleware                       │  │    │
│  │  │     ↓ Log request info                       │  │    │
│  │  │  2. Authentication Middleware                │  │    │
│  │  │     ↓ Check session, load user context       │  │    │
│  │  │  3. Validation Middleware                    │  │    │
│  │  │     ↓ Validate request size, content-type    │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────┘    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │                 🚦 ROUTES                          │    │
│  │  • auth_routes.py                                  │    │
│  │    - /api/auth/register                            │    │
│  │    - /api/auth/login                               │    │
│  │    - /api/auth/profile                             │    │
│  │                                                     │    │
│  │  • api_routes.py                                   │    │
│  │    - /api/message                                  │    │
│  │    - /api/preinscriptions                          │    │
│  │    - /api/etablissements                           │    │
│  │    - /api/filieres                                 │    │
│  │                                                     │    │
│  │  ✅ Thin layer: HTTP routing only                 │    │
│  │  ✅ Applies decorators (@login_required, etc.)    │    │
│  │  ✅ Delegates to controllers                      │    │
│  └────────────────────────────────────────────────────┘    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │              🎮 CONTROLLERS                        │    │
│  │  • auth_controller.py                              │    │
│  │    - register_user()                               │    │
│  │    - login_user()                                  │    │
│  │    - logout_user()                                 │    │
│  │    - get_user_profile()                            │    │
│  │                                                     │    │
│  │  • chat_controller.py                              │    │
│  │    - send_message()                                │    │
│  │    - get_message_history()                         │    │
│  │                                                     │    │
│  │  • preinscription_controller.py                    │    │
│  │    - create_preinscription()                       │    │
│  │    - get_preinscriptions()                         │    │
│  │                                                     │    │
│  │  ✅ Business logic layer                          │    │
│  │  ✅ Data validation and transformation             │    │
│  │  ✅ Calls services/models                          │    │
│  │  ✅ Returns (response_dict, status_code)           │    │
│  └────────────────────────────────────────────────────┘    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │           🔧 SERVICES / MODELS                     │    │
│  │  • Database access                                  │    │
│  │  • External API calls (Gemini AI)                  │    │
│  │  • File operations                                  │    │
│  │  • Complex business rules                          │    │
│  └────────────────────────────────────────────────────┘    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │              🛡️ ERROR HANDLERS                     │    │
│  │  • APIError → JSON response                        │    │
│  │  • 404, 500 → Error templates                      │    │
│  │  • Logging errors                                   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                         │ HTTP Response
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Middlewares

### 1. Auth Middleware (`middleware/auth_middleware.py`)

**Responsabilités :**
- Vérifier l'authentification des utilisateurs
- Gérer les sessions et leur validité
- Charger le contexte utilisateur dans `g`
- Protéger les routes via décorateurs

**Décorateurs disponibles :**

```python
from middleware import login_required, admin_required, role_required, optional_auth

@login_required
def protected_route():
    # g.user_id, g.user_email, g.user_role sont disponibles
    pass

@admin_required
def admin_only_route():
    # Vérifie role == 'admin'
    pass

@role_required('admin', 'etudiant')
def multi_role_route():
    # Accessible aux admins ET étudiants
    pass

@optional_auth
def public_route_with_optional_auth():
    # g.authenticated == True si connecté, False sinon
    pass
```

**Fonctionnalités :**
- Vérification automatique de l'expiration de session (24h)
- Mise à jour de `last_activity` après chaque requête
- Routes publiques exclues : `/static`, `/api/auth/login`, `/api/auth/register`, etc.

### 2. Validation Middleware (`middleware/validation_middleware.py`)

**Responsabilités :**
- Valider les données JSON entrantes
- Valider les paramètres de requête
- Valider les fichiers uploadés
- Nettoyer et assainir les données

**Décorateurs disponibles :**

```python
from middleware import validate_json, validate_query_params, validate_file_upload

@validate_json('email', 'password')
def register():
    # Vérifie que email et password sont présents dans le JSON
    data = request.get_json()
    pass

@validate_query_params('page', 'per_page')
def get_list():
    # Vérifie que page et per_page sont présents dans query params
    page = request.args.get('page', type=int)
    pass

@validate_file_upload(allowed_extensions={'pdf', 'jpg'}, max_size_mb=5)
def upload_document():
    # Vérifie extension et taille des fichiers
    files = request.files
    pass
```

**Fonctions utilitaires :**

```python
from middleware import validate_email, validate_password, validate_phone, sanitize_string

# Validation d'email (RFC 5322)
is_valid = validate_email("test@example.com")

# Validation de mot de passe (8+ chars, 1 maj, 1 min, 1 chiffre)
is_valid, message = validate_password("Secure123")

# Validation de téléphone camerounais
is_valid = validate_phone("+237 6XX XXX XXX")

# Nettoyage de chaîne
clean_text = sanitize_string("  test  ", max_length=100)
```

### 3. Logging Middleware (`middleware/logging_middleware.py`)

**Responsabilités :**
- Logger toutes les requêtes et réponses
- Masquer les données sensibles (passwords, tokens)
- Calculer le temps de traitement
- Logger les événements de sécurité

**Fonctions utilitaires :**

```python
from middleware import log_auth_attempt, log_user_action, log_security_event, log_database_error

# Logger une tentative d'authentification
log_auth_attempt(email="test@example.com", success=True)
log_auth_attempt(email="test@example.com", success=False, reason="Password incorrect")

# Logger une action utilisateur
log_user_action(action="CREATE_PREINSCRIPTION", user_id=123, details={'programme': 'L-INFO'})

# Logger un événement de sécurité
log_security_event(event_type="BRUTE_FORCE_ATTEMPT", severity="WARNING", details={...})

# Logger une erreur de base de données
log_database_error(operation="INSERT", error=e, query="INSERT INTO users...")
```

**Logs générés :**
- `logs/app.log` : Tous les logs de l'application
- Format JSON pour faciliter l'analyse
- Niveaux : DEBUG, INFO, WARNING, ERROR, CRITICAL

### 4. Error Handler (`middleware/error_handler.py`)

**Responsabilités :**
- Gérer toutes les erreurs de l'application
- Renvoyer des réponses JSON cohérentes pour les API
- Renvoyer des templates HTML pour les pages web
- Logger les erreurs

**Classes d'erreurs personnalisées :**

```python
from middleware import APIError, ValidationError, AuthenticationError, AuthorizationError, NotFoundError

# Lever une erreur de validation
raise ValidationError("Email invalide", details={'field': 'email'})

# Lever une erreur d'authentification
raise AuthenticationError("Mot de passe incorrect")

# Lever une erreur d'autorisation
raise AuthorizationError("Accès réservé aux administrateurs")

# Lever une erreur 404
raise NotFoundError("Utilisateur non trouvé")
```

**Codes d'erreur HTTP gérés :**
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 405 Method Not Allowed
- 413 Request Entity Too Large
- 429 Too Many Requests
- 500 Internal Server Error
- 503 Service Unavailable

---

## Contrôleurs

Les contrôleurs contiennent toute la **logique métier** de l'application. Ils sont appelés par les routes et retournent des tuples `(response_dict, status_code)`.

### Structure d'un contrôleur

```python
def controller_function():
    """
    Description de la fonction
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        # 1. Récupérer les données de la requête
        data = request.get_json()
        user_id = g.user_id
        
        # 2. Validation des données
        if not data.get('field'):
            raise ValidationError('Champ requis manquant')
        
        # 3. Logique métier
        # ... traitement ...
        
        # 4. Interaction avec la base de données
        conn = get_db_connection()
        # ... requêtes SQL ...
        conn.commit()
        conn.close()
        
        # 5. Logging
        log_user_action('ACTION_NAME', user_id, details={...})
        
        # 6. Retour de la réponse
        return {
            'success': True,
            'message': '...',
            'data': {...}
        }, 200
        
    except ValidationError as e:
        return {
            'success': False,
            'error': e.message,
            'code': e.code
        }, e.status_code
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return {
            'success': False,
            'error': 'Erreur serveur',
            'code': 'INTERNAL_ERROR'
        }, 500
```

### Contrôleurs disponibles

1. **`auth_controller.py`**
   - `register_user()` : Inscription
   - `login_user()` : Connexion
   - `logout_user()` : Déconnexion
   - `get_user_profile()` : Récupérer le profil
   - `update_user_profile()` : Mettre à jour le profil
   - `change_password()` : Changer le mot de passe

2. **`chat_controller.py`**
   - `send_message()` : Envoyer un message au chatbot
   - `get_message_history(session_id)` : Historique d'une session
   - `get_user_chat_sessions()` : Liste des sessions utilisateur
   - `delete_chat_session(session_id)` : Supprimer une session

3. **`preinscription_controller.py`**
   - `create_preinscription()` : Créer une préinscription
   - `get_preinscriptions()` : Liste des préinscriptions
   - `get_preinscription_detail(id)` : Détails d'une préinscription
   - `update_preinscription_status(id)` : Mettre à jour le statut (admin)

4. **`etablissement_controller.py`**
   - `get_etablissements()` : Liste des établissements
   - `get_etablissement_detail(id)` : Détails d'un établissement
   - `get_etablissement_stats(id)` : Statistiques (admin)

5. **`filiere_controller.py`**
   - `get_filieres()` : Liste des filières
   - `get_filiere_detail(id)` : Détails d'une filière
   - `get_filieres_by_niveau()` : Filières groupées par niveau

---

## Routes

Les routes sont des **couches minces** qui font le lien entre les requêtes HTTP et les contrôleurs.

### Structure d'une route

```python
from flask import Blueprint, jsonify
from controllers import auth_controller
from middleware import validate_json, login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
@validate_json('nom', 'prenom', 'email', 'password')
def register():
    """
    POST /api/auth/register
    Documentation...
    """
    response_data, status_code = auth_controller.register_user()
    return jsonify(response_data), status_code
```

**Responsabilités des routes :**
- ✅ Définir le chemin HTTP
- ✅ Appliquer les décorateurs de middleware
- ✅ Déléguer au contrôleur
- ✅ Retourner la réponse JSON

**Ce que les routes NE font PAS :**
- ❌ Validation métier (fait par contrôleurs)
- ❌ Accès base de données (fait par contrôleurs)
- ❌ Logique métier (fait par contrôleurs)

---

## Flux de requête

### Exemple : Inscription d'un utilisateur

```
1. CLIENT
   POST /api/auth/register
   Body: {"nom": "Doe", "prenom": "John", "email": "john@example.com", "password": "Secure123"}
   
   ↓

2. FLASK APP - Logging Middleware
   → Log: "API Request: POST /api/auth/register from IP xxx.xxx.xxx.xxx"
   
   ↓

3. FLASK APP - Validation Middleware
   → Check: Content-Type = application/json ✓
   → Check: Request size < 5MB ✓
   
   ↓

4. ROUTE - auth_routes.py
   → @validate_json('nom', 'prenom', 'email', 'password')
   → Check: All required fields present ✓
   → Delegate to: auth_controller.register_user()
   
   ↓

5. CONTROLLER - auth_controller.py
   → Extract data from request.get_json()
   → Validate email format using middleware.validate_email()
   → Validate password strength using middleware.validate_password()
   → Check if email already exists in database
   → Hash password with SHA-256
   → Insert user into database
   → Create session
   → Log: log_user_action('REGISTER', user_id, ...)
   → Return: ({"success": True, "user": {...}}, 201)
   
   ↓

6. ROUTE - auth_routes.py
   → Convert to JSON response
   → Return jsonify(response_data), 201
   
   ↓

7. FLASK APP - Logging Middleware
   → Log: "Response: 201 Created, elapsed_time: 45ms"
   
   ↓

8. CLIENT
   Response: 201 Created
   Body: {"success": true, "message": "Inscription réussie", "user": {...}}
```

---

## Exemples d'utilisation

### 1. Créer une nouvelle route avec contrôleur

**Étape 1 : Créer le contrôleur**

```python
# controllers/example_controller.py

from flask import request, g
from middleware import ValidationError, log_user_action

DATABASE = 'database/chatbot.db'

def create_example():
    """
    Crée un nouvel exemple
    
    Returns:
        tuple: (response_dict, status_code)
    """
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            raise ValidationError('Le nom est requis')
        
        # Logique métier ici
        # ...
        
        log_user_action('CREATE_EXAMPLE', g.user_id, {'name': name})
        
        return {
            'success': True,
            'message': 'Exemple créé',
            'data': {'name': name}
        }, 201
        
    except ValidationError as e:
        return {
            'success': False,
            'error': e.message,
            'code': e.code
        }, e.status_code
    
    except Exception as e:
        return {
            'success': False,
            'error': 'Erreur serveur',
            'code': 'INTERNAL_ERROR'
        }, 500
```

**Étape 2 : Créer la route**

```python
# route/api_routes.py

from controllers import example_controller

@api_bp.route('/examples', methods=['POST'])
@login_required
@validate_json('name')
def create_example():
    """POST /api/examples - Crée un exemple"""
    response_data, status_code = example_controller.create_example()
    return jsonify(response_data), status_code
```

### 2. Utiliser les middlewares personnalisés

```python
from middleware import login_required, admin_required, validate_json, log_user_action

# Route protégée pour utilisateurs authentifiés
@api_bp.route('/protected', methods=['GET'])
@login_required
def protected_route():
    user_id = g.user_id  # Disponible grâce au middleware
    user_role = g.user_role
    return jsonify({'message': f'Hello user {user_id}'}), 200

# Route réservée aux admins
@api_bp.route('/admin-only', methods=['GET'])
@admin_required
def admin_only_route():
    return jsonify({'message': 'Admin access granted'}), 200

# Route avec validation JSON
@api_bp.route('/submit', methods=['POST'])
@validate_json('field1', 'field2')
def submit_data():
    data = request.get_json()
    # field1 et field2 sont garantis d'exister
    pass
```

### 3. Gérer les erreurs proprement

```python
from middleware import ValidationError, AuthenticationError, NotFoundError

def my_controller():
    try:
        # Lever une erreur de validation
        if not valid_data:
            raise ValidationError('Données invalides', details={'field': 'email'})
        
        # Lever une erreur d'authentification
        if not authenticated:
            raise AuthenticationError('Authentification requise')
        
        # Lever une erreur 404
        if not found:
            raise NotFoundError('Ressource non trouvée')
        
        return {'success': True}, 200
        
    except (ValidationError, AuthenticationError, NotFoundError) as e:
        return {'success': False, 'error': e.message, 'code': e.code}, e.status_code
```

---

## Bonnes pratiques

### 1. Contrôleurs

✅ **DO:**
- Une fonction = une responsabilité
- Retourner `(response_dict, status_code)`
- Utiliser `try-except` pour gérer les erreurs
- Logger les actions importantes
- Valider les données avant traitement

❌ **DON'T:**
- Accéder directement à `request` dans les services
- Mélanger logique métier et routing
- Oublier de fermer les connexions DB
- Exposer des détails d'erreurs sensibles en production

### 2. Routes

✅ **DO:**
- Garder les routes minces (2-5 lignes)
- Appliquer les décorateurs de middleware
- Documenter avec docstrings
- Utiliser les bons verbes HTTP (GET, POST, PUT, DELETE)

❌ **DON'T:**
- Mettre de la logique métier dans les routes
- Oublier `@login_required` sur les routes protégées
- Mélanger routes API et routes HTML

### 3. Middlewares

✅ **DO:**
- Créer des décorateurs réutilisables
- Logger les événements importants
- Valider tôt dans le pipeline
- Renvoyer des erreurs claires

❌ **DON'T:**
- Faire de la logique métier dans les middlewares
- Bloquer les requêtes inutilement
- Oublier de gérer les exceptions

### 4. Sécurité

✅ **DO:**
- Toujours valider les entrées utilisateur
- Utiliser `@login_required` et `@admin_required`
- Masquer les données sensibles dans les logs
- Hasher les mots de passe (SHA-256 ou mieux)
- Limiter la taille des fichiers uploadés

❌ **DON'T:**
- Stocker des mots de passe en clair
- Exposer des stack traces en production
- Accepter des fichiers sans validation
- Oublier la validation côté serveur

---

## Migration depuis l'ancienne architecture

### Avant (app.py monolithique)

```python
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Validation
    if not email or not password:
        return jsonify({'error': 'Missing fields'}), 400
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Insert in DB
    conn = sqlite3.connect('database/chatbot.db')
    conn.execute('INSERT INTO users (...) VALUES (...)')
    conn.commit()
    conn.close()
    
    return jsonify({'success': True}), 201
```

### Après (Architecture MVC + Controllers)

```python
# route/auth_routes.py
@auth_bp.route('/register', methods=['POST'])
@validate_json('email', 'password')
def register():
    response_data, status_code = auth_controller.register_user()
    return jsonify(response_data), status_code

# controllers/auth_controller.py
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Validation with middleware
    if not validate_email(email):
        raise ValidationError('Email invalide')
    
    is_valid, message = validate_password(password)
    if not is_valid:
        raise ValidationError(message)
    
    # Business logic
    password_hash = hash_password(password)
    
    conn = get_db_connection()
    conn.execute('INSERT INTO users (...) VALUES (...)')
    conn.commit()
    conn.close()
    
    log_user_action('REGISTER', user_id, {'email': email})
    
    return {'success': True}, 201
```

**Avantages :**
- ✅ Code plus lisible et maintenable
- ✅ Réutilisabilité des middlewares
- ✅ Testabilité accrue
- ✅ Séparation des responsabilités
- ✅ Gestion centralisée des erreurs
- ✅ Logging automatique

---

## Conclusion

Cette architecture offre :

1. **Maintenabilité** : Code organisé, facile à comprendre et modifier
2. **Scalabilité** : Facile d'ajouter de nouvelles fonctionnalités
3. **Testabilité** : Chaque couche peut être testée indépendamment
4. **Sécurité** : Middlewares centralisés pour authentification et validation
5. **Monitoring** : Logging automatique de toutes les requêtes et erreurs
6. **Performance** : Gestion optimisée des connexions et ressources

Pour plus d'informations, consultez :
- `middleware/` : Code source des middlewares
- `controllers/` : Code source des contrôleurs
- `route/` : Code source des routes
- `app_new.py` : Point d'entrée de l'application

---

**Auteur :** Madick Ange César  
**Version :** 3.0  
**Date :** Novembre 2025
