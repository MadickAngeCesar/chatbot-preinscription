# 🎓 Chatbot de Préinscription Universitaire

**Système intelligent de préinscription avec IA Google Gemini**

## 🧠 Description du Projet

Le **Chatbot de Préinscription Universitaire** est une application web intelligente qui assiste les étudiants dans leur processus de **préinscription en ligne** pour ICT University au Cameroun.

Propulsé par **Google Gemini AI**, ce chatbot offre des réponses contextuelles, personnalisées et précises sur les programmes, admissions, frais de scolarité et démarches d'inscription.

### ✨ Nouveauté: Intégration Gemini AI

Le système utilise désormais **Google Gemini 2.0 Flash Experimental** avec des prompts personnalisés pour:
- 🎯 **Comprendre l'intention** de l'utilisateur (programmes, admission, frais, etc.)
- 💬 **Répondre de façon contextuelle** en gardant l'historique de conversation
- 🎓 **Guider vers la préinscription** de manière proactive
- 👤 **Personnaliser** les réponses avec le nom de l'utilisateur
- 🔄 **Fallback intelligent** vers des réponses pré-définies en cas d'erreur API
- ⚡ **Réponses ultra-rapides** grâce au modèle Flash optimisé

### 🏗️ Architecture Complète

```
Frontend (HTML/CSS/JS)
         ↓
Flask REST API (15 endpoints business + 9 auth)
         ↓
Gemini AI Chatbot (Context + Intent Detection)
         ↓
Google Gemini Pro (Génération IA)
         ↓
SQLite Database (6 tables)
```

---

## 🧩 Fonctionnalités Principales

### 💬 Chatbot Intelligent (Gemini AI)
- ✅ Réponses contextuelles avec historique de conversation (10 derniers messages)
- ✅ Détection d'intention (8 catégories: programmes, frais, admission, etc.)
- ✅ Personnalisation avec nom d'utilisateur
- ✅ Prompts optimisés pour le domaine universitaire
- ✅ Fallback automatique en cas d'erreur API

### 🔐 Authentification & Autorisation
- ✅ Inscription/Connexion sécurisée (hash SHA-256)
- ✅ Sessions persistantes (24h)
- ✅ Contrôle d'accès par rôles (admin/etudiant/visiteur)
- ✅ Profil utilisateur avec édition
- ✅ Changement de mot de passe sécurisé

### 📊 Gestion des Préinscriptions
- ✅ Formulaire de préinscription complet avec auto-fill
- ✅ Upload de documents (PDF, JPG, PNG - max 5 Mo)
- ✅ Suivi du statut (en attente, validé, rejeté)
- ✅ Historique des préinscriptions
- ✅ Statistiques admin (dashboard)

### 🌐 Interface Moderne
- ✅ Design responsive (mobile-first)
- ✅ Gradient violet (#667eea → #764ba2)
- ✅ Animations fluides
- ✅ Navigation adaptative selon l'authentification
- ✅ Messages d'erreur contextuels

### 📈 API REST Complète
- ✅ 15 endpoints business (établissements, filières, préinscriptions, stats)
- ✅ 9 endpoints authentification
- ✅ Documentation OpenAPI (Swagger)
- ✅ Gestion d'erreurs standardisée
- ✅ CORS activé

---

## ⚙️ Technologies Utilisées

| Composant | Technologie | Version |
|-----------|-------------|---------|
| **Backend** | Flask | 3.1.2 |
| **IA** | Google Gemini 2.0 Flash | API |
| **SDK IA** | google-generativeai | 0.3.2 |
| **API** | Flask-CORS, REST | 6.0.1 |
| **Base de données** | SQLite3 | 3.x |
| **Auth** | SHA-256, Flask Sessions | - |
| **Frontend** | HTML5, CSS3, JavaScript | - |
| **Icons** | Font Awesome | 6.4.0 |
| **Config** | python-dotenv | 1.0.0 |

---

## 🧰 Installation et Configuration

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/<ton-utilisateur>/<chatbot-preinscription>.git
cd chatbot-preinscription
```

### 2️⃣ Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configuration Gemini AI

**a) Créer/Vérifier le fichier `.env`:**
```env
GEMINI_API_KEY=votre_cle_api_gemini_ici
DATABASE_PATH=database/chatbot.db
UPLOAD_FOLDER=uploads
SECRET_KEY=votre_cle_secrete_ici
FLASK_ENV=development
```

> ⚠️ **Important:** Remplacez `votre_cle_api_gemini_ici` par votre vraie clé API Gemini

**b) Obtenir une clé API Gemini (si besoin):**
1. Visitez: https://aistudio.google.com/app/apikey
2. Créez une nouvelle clé API
3. Copiez-la dans `.env`

**c) Tester Gemini:**
```bash
python test_gemini.py
```
Choisissez l'option **1** pour un test complet.

### 5️⃣ Initialiser la base de données

```bash
python init_db.py
```

### 6️⃣ Créer des utilisateurs de test (optionnel)

```bash
python create_test_user.py
```

Cela créera:
- **test@example.com** / `TestPass123` (étudiant)
- **admin@ict.sn** / `AdminPass123` (admin)

### 7️⃣ Lancer l'application

```bash
python app.py
```

L'application sera disponible sur :
👉 **http://127.0.0.1:5000**

### 8️⃣ Accéder aux différentes pages

- **Landing page**: http://localhost:5000/
- **Chatbot**: http://localhost:5000/chat (nécessite connexion)
- **Préinscription**: http://localhost:5000/preinscription (nécessite connexion)
- **Login**: http://localhost:5000/login
- **Register**: http://localhost:5000/register
- **Profile**: http://localhost:5000/profile (nécessite connexion)

---

## 🧬 Structure du Projet

```
chatbot-preinscription/
│
├── app.py                      # Application Flask principale
├── route/
│   ├── api.py                 # API REST (15 endpoints business)
│   └── auth_api.py            # API Authentification (9 endpoints)
├── gemini_chatbot.py          # Module Gemini AI ⭐ NOUVEAU
├── gemini_config.py           # Configuration Gemini ⭐ NOUVEAU
├── test_gemini.py             # Tests Gemini ⭐ NOUVEAU
├── init_db.py                 # Initialisation base de données
├── migrate_db.py              # Migration base de données
├── create_test_user.py        # Création utilisateurs test
├── requirements.txt           # Dépendances Python
├── .env                       # Variables d'environnement (SECRET)
│
├── database/
│   └── chatbot.db            # Base SQLite (6 tables)
│
├── templates/                # Pages HTML
│   ├── index.html           # Landing page
│   ├── chat.html            # Interface chatbot
│   ├── preinscription.html  # Formulaire préinscription
│   ├── login.html           # Connexion
│   ├── register.html        # Inscription
│   ├── profile.html         # Profil utilisateur
│   └── error.html           # Pages d'erreur
│
├── static/
│   ├── css/
│   │   └── style.css        # Styles CSS (3000+ lignes)
│   ├── js/
│   │   └── script.js        # JavaScript (930+ lignes)
│   │                       # - Fonctions chat globales
│   │                       # - Gestion événements
│   │                       # - Utils authentification
│   └── img/                 # Images et assets
│
├── doc/                      # Documentation
│   ├── GEMINI-INTEGRATION.md      # Doc Gemini complète ⭐
│   ├── QUICK-START-GEMINI.md      # Guide rapide Gemini ⭐
│   ├── SRS.md                     # Spécifications
│   ├── SDD.md                     # Design système
│   └── diagram/                   # Diagrammes Mermaid
│       ├── architecture.mmd
│       ├── sequence.mmd
│       ├── ER.mmd
│       ├── Class.mmd
│       └── use-case.mmd
│
└── uploads/                  # Fichiers uploadés (documents)
```

---

## 🤖 Fonctionnement du Chatbot Gemini

### Architecture du système IA

```
┌─────────────────────────────────────────────────────┐
│          1. MESSAGE UTILISATEUR                      │
│  "Quels sont les programmes en Licence ?"           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│     2. DÉTECTION D'INTENTION (Intent Detection)     │
│  → Analyse mots-clés: "programmes", "licence"       │
│  → Intention détectée: "programmes"                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│    3. ENRICHISSEMENT CONTEXTUEL                     │
│  → Nom utilisateur: "Jean Dupont"                   │
│  → Historique: derniers 10 messages                 │
│  → Directive: "Liste les programmes Licence"        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│    4. APPEL GEMINI API                              │
│  → Modèle: gemini-2.0-flash-exp                     │
│  → Temperature: 0.7 (créativité modérée)            │
│  → Max tokens: 500 (~150 mots)                      │
│  → Safety settings: MEDIUM_AND_ABOVE                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│    5. GÉNÉRATION RÉPONSE                            │
│  "Bonjour Jean ! Nous proposons 5 programmes        │
│   en Licence: Génie Logiciel, Réseaux..."          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│    6. SAUVEGARDE & RETOUR                           │
│  → Enregistrement dans base de données              │
│  → Affichage dans l'interface chat                  │
└─────────────────────────────────────────────────────┘
```

### Intents supportés (8 catégories)

| Intent | Mots-clés | Exemple |
|--------|-----------|---------|
| **preinscription** | inscription, m'inscrire, candidature | "Je veux m'inscrire" |
| **programmes** | programme, filière, licence, master | "Quels programmes en Master ?" |
| **frais** | frais, coût, prix, tarif | "Combien coûte la Licence ?" |
| **admission** | admission, condition, document | "Quels documents requis ?" |
| **calendrier** | date, quand, rentrée | "Quand est la rentrée ?" |
| **contact** | contact, email, téléphone | "Comment vous contacter ?" |
| **salutation** | bonjour, salut, hello | "Bonjour !" |
| **aide** | aide, comment, info | "Comment ça marche ?" |

### Exemple de conversation complète

**Tour 1:**
```
👤 Utilisateur: "Bonjour"
🤖 Chatbot: "Bonjour ! 👋 Je suis votre assistant virtuel pour ICT 
            University. Je peux vous aider avec:
            - 🎓 Informations sur nos programmes
            - 📝 Processus de préinscription
            - 💰 Frais et modalités
            Comment puis-je vous assister aujourd'hui ? 😊"
```

**Tour 2:**
```
👤 Utilisateur: "Quels programmes en Intelligence Artificielle ?"
🤖 Chatbot: "Excellent choix ! 🧠 Nous proposons 2 programmes en IA:
            
            📚 **Licence en IA** (3 ans):
            Machine Learning, Deep Learning, NLP
            Débouchés: Data Scientist, ML Engineer
            
            📚 **Master IA & Big Data** (2 ans):
            IA avancée, traitement massif de données
            Débouchés: Research Scientist, AI Architect
            
            Souhaitez-vous connaître les conditions d'admission ? 🎓"
```

**Tour 3:**
```
👤 Utilisateur: "Oui, quelles sont les conditions ?"
🤖 Chatbot: "📋 Conditions pour la **Licence en IA**:
            
            ✅ Baccalauréat (priorité C, D)
            ✅ Relevé de notes (moyenne ≥ 12/20 recommandé)
            ✅ Test d'entrée (Maths, Logique, Anglais)
            
            **Documents requis:**
            - Copie BAC certifiée
            - Acte de naissance
            - 4 photos d'identité
            
            Voulez-vous commencer votre préinscription ? ✅"
```

---

## 📊 Base de Données (6 Tables)

### Schéma relationnel

```sql
-- 1. Utilisateurs
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    telephone TEXT,
    role TEXT DEFAULT 'etudiant',  -- admin, etudiant, visiteur
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Établissements
CREATE TABLE etablissements (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    code TEXT UNIQUE,
    adresse TEXT,
    ville TEXT,
    pays TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Filières
CREATE TABLE filieres (
    id INTEGER PRIMARY KEY,
    etablissement_id INTEGER,
    nom TEXT NOT NULL,
    niveau TEXT,  -- licence, master, doctorat
    duree_annees INTEGER,
    description TEXT,
    FOREIGN KEY (etablissement_id) REFERENCES etablissements(id)
);

-- 4. Préinscriptions
CREATE TABLE preinscriptions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    filiere_id INTEGER,
    statut TEXT DEFAULT 'en_attente',  -- en_attente, validé, rejeté
    documents TEXT,  -- JSON: chemins des fichiers
    date_soumission TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (filiere_id) REFERENCES filieres(id)
);

-- 5. Sessions de chat
CREATE TABLE chat_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 6. Messages
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    role TEXT,  -- user, bot
    contenu TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);
```

---

## 🔒 Sécurité

### Authentification
- ✅ **Hashing de mots de passe**: SHA-256
- ✅ **Validation email**: Format RFC 5322
- ✅ **Force du mot de passe**: Min 8 caractères, majuscule, minuscule, chiffre
- ✅ **Sessions Flask**: Secret key cryptographique
- ✅ **Durée de session**: 24 heures

### Autorisation (RBAC)
```python
# Décorateurs de protection
@login_required          # Nécessite authentification
@admin_required          # Nécessite rôle admin

# Rôles disponibles
- admin      → Accès total (dashboard, gestion users, stats)
- etudiant   → Accès chatbot, préinscription, profil
- visiteur   → Accès limité (landing page, chatbot basique)
```

### Protection des données
- ✅ **Validation des entrées**: Sanitization côté serveur
- ✅ **Upload sécurisé**: Whitelist extensions (pdf, jpg, png), taille max 5 Mo
- ✅ **Paramètres SQL**: Requêtes paramétrées (injection SQL)
- ✅ **CORS**: Origines autorisées configurables
- ✅ **Secrets**: Variables d'environnement (.env)

---

## 📡 API REST

### Endpoints Authentification (9)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/auth/register` | Inscription utilisateur | ❌ |
| POST | `/api/auth/login` | Connexion utilisateur | ❌ |
| POST | `/api/auth/logout` | Déconnexion | ✅ |
| GET | `/api/auth/check` | Vérifier authentification | ✅ |
| GET | `/api/auth/profile` | Récupérer profil | ✅ |
| PUT | `/api/auth/profile` | Modifier profil | ✅ |
| POST | `/api/auth/change-password` | Changer mot de passe | ✅ |
| GET | `/api/auth/users` | Liste utilisateurs | 🔒 Admin |
| PUT | `/api/auth/users/<id>/role` | Changer rôle | 🔒 Admin |

### Endpoints Business (15)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/message` | Envoyer message chatbot | ✅ |
| GET | `/api/messages/history/<id>` | Historique conversation | ✅ |
| POST | `/api/preinscription` | Soumettre préinscription | ✅ |
| GET | `/api/preinscriptions` | Mes préinscriptions | ✅ |
| GET | `/api/preinscriptions/<id>` | Détails préinscription | ✅ |
| GET | `/api/etablissements` | Liste établissements | ❌ |
| GET | `/api/etablissements/<id>` | Détails établissement | ❌ |
| GET | `/api/filieres` | Liste filières | ❌ |
| GET | `/api/filieres/<id>` | Détails filière | ❌ |
| GET | `/api/filieres/etablissement/<id>` | Filières par établissement | ❌ |
| GET | `/api/search` | Recherche globale | ❌ |
| GET | `/api/stats/dashboard` | Statistiques dashboard | 🔒 Admin |
| PUT | `/api/preinscriptions/<id>/status` | Changer statut | 🔒 Admin |
| GET | `/api/preinscriptions/all` | Toutes préinscriptions | 🔒 Admin |
| DELETE | `/api/preinscriptions/<id>` | Supprimer préinscription | 🔒 Admin |

**Légende:** ❌ Public | ✅ Authentifié | 🔒 Admin uniquement

---

## 🧪 Tests

### Tester Gemini AI

```bash
# Test complet (conversation simulée)
python test_gemini.py
> Choix: 1

# Test détection d'intentions
python test_gemini.py
> Choix: 2

# Mode interactif (conversation réelle)
python test_gemini.py
> Choix: 4
```

### Tester les APIs

```bash
# Test avec curl
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Test",
    "prenom": "User",
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### Tester l'authentification

1. **Inscription**: http://localhost:5000/register
2. **Connexion**: http://localhost:5000/login (utilisez les credentials créés)
3. **Profil**: http://localhost:5000/profile (vérifiez les données)
4. **Chatbot**: http://localhost:5000/chat (testez la conversation)

---

## 📚 Documentation Complète

### Gemini AI
- 📖 **[GEMINI-INTEGRATION.md](doc/GEMINI-INTEGRATION.md)**: Documentation complète (architecture, prompts, config, dépannage)
- 🚀 **[QUICK-START-GEMINI.md](doc/QUICK-START-GEMINI.md)**: Guide de démarrage rapide (5 minutes)

### Système
- 📋 **[SRS.md](doc/SRS.md)**: Spécifications des exigences logicielles
- 🏗️ **[SDD.md](doc/SDD.md)**: Document de design système
- 🗺️ **[diagram/](doc/diagram/)**: Diagrammes Mermaid (architecture, séquence, ER, etc.)

---

## 🚀 Déploiement

### Variables d'environnement (.env)

```env
# Gemini AI
GEMINI_API_KEY=votre_cle_gemini_ici

# Flask
SECRET_KEY=votre_secret_key_ici
FLASK_ENV=production  # ou development

# Base de données
DATABASE_PATH=database/chatbot.db

# Uploads
UPLOAD_FOLDER=uploads
MAX_UPLOAD_SIZE=5242880  # 5 Mo en bytes

# Email (optionnel - pour notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=votre_email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe
```

### Checklist de déploiement

- [ ] ✅ Installer dépendances: `pip install -r requirements.txt`
- [ ] ✅ Configurer `.env` avec variables de production
- [ ] ✅ Initialiser base de données: `python init_db.py`
- [ ] ✅ Créer admin: `python create_test_user.py`
- [ ] ✅ Tester Gemini: `python test_gemini.py`
- [ ] ✅ Tester API: `curl http://localhost:5000/api/auth/check`
- [ ] ✅ Vérifier permissions uploads: `chmod 755 uploads/`
- [ ] ✅ Configurer reverse proxy (Nginx/Apache)
- [ ] ✅ Activer HTTPS (Let's Encrypt)
- [ ] ✅ Configurer backup automatique base de données

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer:

1. **Fork** le projet
2. **Créer une branche**: `git checkout -b feature/AmazingFeature`
3. **Commit**: `git commit -m 'Add AmazingFeature'`
4. **Push**: `git push origin feature/AmazingFeature`
5. **Pull Request**: Ouvrir une PR sur GitHub

---

## 📝 Licence

Ce projet est sous licence **MIT**. Voir le fichier `LICENSE` pour plus de détails.

---

## 👤 Auteur

**Madick Ange César**
- 🎓 Étudiant en Informatique (Full-stack, IoT & IA/ML)
- 🏫 The ICT University – Cameroun
- 📧 Email: madick@ict-university.cm
- 💼 GitHub: [@MadickAnge](https://github.com/MadickAnge)

---

## 🙏 Remerciements

- **Google Gemini AI** pour l'API d'intelligence artificielle
- **Flask** pour le framework web Python
- **Font Awesome** pour les icônes
- **ICT University** pour le cas d'usage réel

---

## 📈 Roadmap

### Version actuelle: 1.0.0 ✅
- ✅ Chatbot Gemini 2.0 Flash AI intégré
- ✅ Détection d'intention intelligente (8 catégories)
- ✅ Contexte de conversation (historique 10 messages)
- ✅ Système d'authentification complet avec RBAC
- ✅ Gestion préinscriptions avec upload documents
- ✅ API REST complète (24 endpoints)
- ✅ Interface responsive et moderne
- ✅ CSP sécurisé pour scripts inline
- ✅ Fallback automatique en cas d'erreur API

### Version 1.1.0 (En cours)
- [ ] Amélioration UX/UI du chat
- [ ] Streaming responses Gemini (temps réel)
- [ ] Export préinscriptions (PDF, Excel)
- [ ] Notifications email automatiques
- [ ] Dashboard admin avec graphiques
- [ ] Mode sombre / clair
- [ ] Multi-langue (français, anglais)

### Version 2.0.0 (Long terme)
- [ ] Paiement en ligne intégré
- [ ] Génération automatique de documents (attestations)
- [ ] Chatbot vocal (speech-to-text)
- [ ] Mobile app (React Native)
- [ ] Analytics avancées (satisfaction, conversion)

---

**⭐ Si ce projet vous plaît, n'hésitez pas à lui donner une étoile sur GitHub !**
│   └── nlp_utils.py
│
├── static/                   # Fichiers statiques (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── img/
│       └── ...
│
├── templates/                # Fichiers HTML (interface utilisateur)
│   ├── index.html
│   ├── chat.html
│   └── preinscription.html
│
├── database/                 # Base de données SQLite
│   └── chatbot.db
│
├── init_db.py                # Script d’initialisation de la BD
├── requirements.txt          # Liste des dépendances Python
└── README.md                 # Documentation du projet
```

---

## 🧠 Exemple de Fonctionnement

1. L’étudiant ouvre la page web et interagit avec le chatbot.
2. Le chatbot répond en temps réel selon le modèle IA.
3. Si l’étudiant souhaite se préinscrire, le chatbot le redirige vers le formulaire.
4. Les informations sont enregistrées dans la base de données.
5. L’administrateur peut consulter les préinscriptions via une interface de gestion (optionnelle).

---

## 🚀 Améliorations Futures

* 🔊 Intégration d’un moteur vocal (speech-to-text / text-to-speech).
* 🌍 Support multilingue (français, anglais)
* ☁️ Déploiement sur un hébergeur cloud (Render, Railway, ou PythonAnywhere).
* 🤖 Amélioration du modèle IA avec apprentissage continu.

---

## � Dépannage Courant

### ❌ Le chatbot ne répond pas
- ✅ Vérifiez la clé API Gemini dans `.env`
- ✅ Vérifiez la connexion internet
- ✅ Consultez les logs Flask
- ✅ Test: `python test_gemini.py`

### ❌ Bouton d'envoi inactif
- ✅ Videz le cache: Ctrl + Shift + R
- ✅ Console JavaScript (F12)
- ✅ Vérifiez `script.js?v=20251105c`

### ❌ Erreur CSP
- ✅ Headers configurés dans `app.py`
- ✅ Scripts inline autorisés

### ❌ Base de données corrompue
```bash
rm database/chatbot.db
python init_db.py
```

---

## 💡 Conseils de Performance

- � **Gemini 2.0 Flash** est optimisé pour la vitesse
- 🔄 Utilisez le **fallback** en cas d'erreur API
- 📦 **Cache** les réponses fréquentes (à venir)
- ⚡ **CDN** pour Font Awesome et Google Fonts

---