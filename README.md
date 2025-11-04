# 🎓 Chatbot de Préinscription Universitaire

## 🧠 Description du Projet

Le **Chatbot de Préinscription Universitaire** est une application web intelligente permettant d’assister les étudiants dans leur processus de **préinscription en ligne**.
Développé avec **Flask (Python)** pour le backend et une interface moderne en **HTML, CSS et JavaScript**, ce chatbot offre une expérience fluide et interactive.

Le système utilise un **modèle IA personnalisé** conçu pour comprendre les demandes des étudiants (informations sur les programmes, conditions d’admission, documents requis, frais, etc.) et y répondre automatiquement. Les données relatives aux utilisateurs et aux échanges sont stockées dans une **base de données SQLite**.

---

## 🧩 Fonctionnalités Principales

* 💬 **Chatbot intelligent** : répond aux questions des étudiants sur la préinscription.
* 🧠 **Modèle IA personnalisé** pour le traitement du langage naturel (NLP).
* 🔐 **Gestion de session** avec Flask.
* 💾 **Base de données SQLite** pour stocker les utilisateurs, formulaires et logs de conversation.
* 🌐 **Interface web moderne** (HTML, CSS, JavaScript).
* 📱 **Design responsive** adapté aux ordinateurs et smartphones.

---

## ⚙️ Technologies Utilisées

| Composant       | Technologie                                        |
| --------------- | -------------------------------------------------- |
| Backend         | Flask (Python)                                     |
| Frontend        | HTML5, CSS3, JavaScript                            |
| Base de données | SQLite                                             |
| Modèle IA       | Modèle personnalisé (NLP)                          |
| Serveur local   | Flask Development Server                           |
| API             | REST API (Flask) pour communication client-serveur |

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

### 4️⃣ Initialiser la base de données

```bash
python init_db.py
```

### 5️⃣ Lancer l’application

```bash
flask run
```

L’application sera disponible sur :
👉 `http://127.0.0.1:5000`

---

## 🧬 Structure du Projet

```
chatbot-preinscription/
│
├── app.py                    # Fichier principal Flask
├── model/                    # Ton modèle IA personnalisé
│   ├── chatbot_model.py
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

## 👨‍💻 Auteur

**Madick Ange César**
🎓 Étudiant en Informatique (Full-stack, IoT & IA/ML)
🌍 [The ICT University – Cameroon]
📧 Email : *[[ton.email@example.com](mailto:ton.email@example.com)]*
💼 GitHub : [https://github.com/<ton-utilisateur>](https://github.com/<ton-utilisateur>)

---