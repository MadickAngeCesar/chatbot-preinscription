# 🔧 Correction - Colonne password_hash Manquante

## ❌ Problème Identifié

```
Error: table users has no column named password_hash
```

La table `users` existait déjà dans la base de données mais n'avait pas la colonne `password_hash` nécessaire pour le système d'authentification.

---

## ✅ Solution Appliquée

### 1. Modification du Script de Migration

**Fichier modifié:** `migrate_db.py`

Ajout de la vérification et création automatique de la colonne `password_hash` :

```python
# Vérifier et ajouter la colonne password_hash
cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]

if 'password_hash' not in columns:
    print("📝 Ajout de la colonne password_hash...")
    cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    print("✅ Colonne password_hash ajoutée")
```

---

### 2. Exécution de la Migration

```bash
python migrate_db.py
```

**Résultat:**
```
🔄 Début de la migration...
📝 Ajout de la colonne password_hash...
✅ Colonne password_hash ajoutée

📊 Structure finale de la table users:
  - id: INTEGER
  - nom: TEXT NOT NULL
  - prenom: TEXT NOT NULL
  - email: TEXT NOT NULL
  - telephone: TEXT
  - role: TEXT
  - created_at: TIMESTAMP
  - password_hash: TEXT  ← ✅ AJOUTÉE
```

---

### 3. Création des Utilisateurs de Test

**Nouveau fichier:** `create_test_user.py`

Ce script crée automatiquement deux utilisateurs de test avec mots de passe hachés :

#### Utilisateur 1: Étudiant
- **Email:** test@example.com
- **Mot de passe:** TestPass123
- **Rôle:** etudiant

#### Utilisateur 2: Admin
- **Email:** admin@ict.sn
- **Mot de passe:** AdminPass123
- **Rôle:** admin

**Exécution:**
```bash
python create_test_user.py
```

**Résultat:**
```
✅ Utilisateur créé: test@example.com (ID: 2)
✅ Utilisateur créé: admin@ict.sn (ID: 3)

👥 Total: 3 utilisateur(s)
```

---

## 🧪 Tests de Validation

### Test 1: Vérifier la Structure de la Table

```bash
sqlite3 database/chatbot.db
```

```sql
PRAGMA table_info(users);
```

**Résultat attendu:**
```
0|id|INTEGER|0||1
1|nom|TEXT|1||0
2|prenom|TEXT|1||0
3|email|TEXT|1||0
4|telephone|TEXT|0||0
5|role|TEXT|0||0
6|created_at|TIMESTAMP|0|CURRENT_TIMESTAMP|0
7|password_hash|TEXT|0||0  ← ✅ PRÉSENTE
```

---

### Test 2: Vérifier les Utilisateurs

```sql
SELECT id, email, role, 
       CASE WHEN password_hash IS NOT NULL THEN 'OUI' ELSE 'NON' END as has_password
FROM users;
```

**Résultat attendu:**
```
1|madickangecesar59@gmail.com|etudiant|OUI
2|test@example.com|etudiant|OUI
3|admin@ict.sn|admin|OUI
```

---

### Test 3: Connexion via l'API

```bash
# Démarrer le serveur
python app.py

# Dans un autre terminal ou navigateur
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

**Réponse attendue:**
```json
{
  "success": true,
  "message": "Connexion réussie",
  "user": {
    "id": 2,
    "nom": "Test",
    "prenom": "User",
    "email": "test@example.com",
    "role": "etudiant"
  }
}
```

---

### Test 4: Interface Web

1. **Ouvrir:** http://127.0.0.1:5000/login
2. **Entrer:**
   - Email: `test@example.com`
   - Mot de passe: `TestPass123`
3. **Cliquer:** "Se connecter"
4. **Résultat:** ✅ Redirection vers `/chat`

---

## 📁 Fichiers Modifiés/Créés

| Fichier | Action | Description |
|---------|--------|-------------|
| `migrate_db.py` | ✏️ Modifié | Ajout vérification et création de `password_hash` |
| `create_test_user.py` | ✨ Créé | Script pour créer utilisateurs de test |
| `database/chatbot.db` | 🔄 Mis à jour | Structure table users modifiée |

---

## 🔐 Hachage des Mots de Passe

Le système utilise **SHA-256** pour hacher les mots de passe :

```python
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Exemple
password = "TestPass123"
hashed = hash_password(password)
# Résultat: "9241e5d5..." (64 caractères hexadécimaux)
```

**Stockage dans la BD:**
```sql
INSERT INTO users (email, password_hash, ...)
VALUES ('test@example.com', '9241e5d5...', ...);
```

**Vérification lors de la connexion:**
```python
# Récupérer le hash stocké
stored_hash = "9241e5d5..."

# Hacher le mot de passe saisi
input_hash = hash_password(input_password)

# Comparer
if input_hash == stored_hash:
    print("✅ Mot de passe correct")
```

---

## 🚀 Commandes Rapides

### Recréer la Base de Données (Si Nécessaire)

```bash
# Supprimer l'ancienne base
rm database/chatbot.db

# Recréer avec la nouvelle structure
python init_db.py

# Créer les utilisateurs de test
python create_test_user.py
```

---

### Ajouter Manuellement la Colonne (Alternative)

Si vous préférez faire la migration manuellement :

```bash
sqlite3 database/chatbot.db
```

```sql
-- Ajouter la colonne
ALTER TABLE users ADD COLUMN password_hash TEXT;

-- Vérifier
PRAGMA table_info(users);

-- Sortir
.quit
```

---

### Changer le Mot de Passe d'un Utilisateur

```bash
python
```

```python
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connexion
conn = sqlite3.connect('database/chatbot.db')
cursor = conn.cursor()

# Nouveau mot de passe
new_password = "NouveauPass123"
new_hash = hash_password(new_password)

# Mise à jour
cursor.execute("""
    UPDATE users 
    SET password_hash = ? 
    WHERE email = ?
""", (new_hash, "test@example.com"))

conn.commit()
conn.close()

print("✅ Mot de passe mis à jour")
```

---

## 📊 État Final de la Base de Données

### Table users (Structure Complète)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    telephone TEXT,
    role TEXT DEFAULT 'etudiant' CHECK(role IN ('admin', 'etudiant', 'visiteur')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    password_hash TEXT  -- ← NOUVELLE COLONNE
);
```

### Index Créés

```sql
CREATE INDEX idx_preinscriptions_user ON preinscriptions(user_id);
CREATE INDEX idx_filieres_etablissement ON filieres(etablissement_id);
CREATE INDEX idx_preinscriptions_etablissement ON preinscriptions(etablissement_id);
CREATE INDEX idx_preinscriptions_filiere ON preinscriptions(filiere_id);
CREATE INDEX idx_preinscriptions_statut ON preinscriptions(statut);
CREATE INDEX idx_messages_session ON messages(session_id);
```

---

## ✅ Checklist de Vérification

- [x] Colonne `password_hash` ajoutée à la table `users`
- [x] Colonne `role` présente et valide
- [x] Colonne `created_at` présente
- [x] Utilisateurs de test créés avec mots de passe hachés
- [x] Script de migration fonctionnel
- [x] Script de création d'utilisateurs fonctionnel
- [x] Index de performance créés
- [x] Structure de la table vérifiée

---

## 🎓 Utilisateurs de Test Disponibles

### Pour Tests Étudiant

```
Email: test@example.com
Password: TestPass123
Role: etudiant
```

**Accès:**
- ✅ Page d'accueil
- ✅ Connexion
- ✅ Chat
- ✅ Préinscription
- ✅ Profil
- ❌ Dashboard admin

---

### Pour Tests Admin

```
Email: admin@ict.sn
Password: AdminPass123
Role: admin
```

**Accès:**
- ✅ Toutes les pages étudiant
- ✅ Dashboard admin
- ✅ Gestion utilisateurs
- ✅ Modification des rôles

---

## 📝 Notes Importantes

1. **Sécurité:** Les mots de passe ne sont JAMAIS stockés en clair
2. **Migration:** Le script `migrate_db.py` est idempotent (peut être exécuté plusieurs fois)
3. **Utilisateurs:** Le script `create_test_user.py` met à jour les mots de passe si l'utilisateur existe déjà
4. **Index:** Les index améliorent les performances des requêtes SQL

---

## 🐛 Dépannage

### Problème: "table users has no column named password_hash"

**Solution:**
```bash
python migrate_db.py
```

---

### Problème: "UNIQUE constraint failed: users.email"

L'utilisateur existe déjà.

**Solution 1 - Mettre à jour:**
```bash
python create_test_user.py
```

**Solution 2 - Supprimer et recréer:**
```sql
sqlite3 database/chatbot.db
DELETE FROM users WHERE email = 'test@example.com';
.quit
```

Puis:
```bash
python create_test_user.py
```

---

### Problème: Mot de passe incorrect lors de la connexion

**Vérifier le hash:**
```bash
sqlite3 database/chatbot.db
SELECT email, password_hash FROM users WHERE email = 'test@example.com';
.quit
```

**Recréer l'utilisateur:**
```bash
python create_test_user.py
```

---

## ✨ Résumé

**Problème résolu:** ✅  
**Colonne ajoutée:** `password_hash TEXT`  
**Utilisateurs de test:** 2 créés  
**Scripts créés:** 2 (migrate_db.py modifié, create_test_user.py créé)  
**État:** Prêt pour les tests d'authentification

---

**Date:** 2024  
**Version:** 2.0.1  
**Statut:** ✅ Base de données corrigée et fonctionnelle
