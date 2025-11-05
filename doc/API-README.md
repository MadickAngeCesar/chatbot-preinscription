# 🚀 API REST - Chatbot de Préinscription

Une API REST complète et moderne pour gérer les préinscriptions universitaires.

## 📋 Vue d'ensemble

Cette API fournit tous les endpoints nécessaires pour :
- 🏫 Gérer les établissements d'enseignement
- 🎓 Consulter et filtrer les filières disponibles
- 📝 Administrer les préinscriptions
- 📊 Obtenir des statistiques en temps réel
- 🔍 Effectuer des recherches globales
- ✅ Valider les données

## ⚡ Démarrage rapide

### Prérequis

- Python 3.8+
- Flask installé
- Base de données initialisée

### Lancer le serveur

```bash
# Activer l'environnement virtuel
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Démarrer le serveur
python app.py
```

L'API sera disponible sur : **http://127.0.0.1:5000/api**

## 📚 Documentation

### Documentation complète

Consultez la [Documentation API complète](doc/API-DOCUMENTATION.md) pour tous les détails.

### Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/health` | Vérifier l'état de l'API |
| `GET` | `/api/etablissements` | Liste des établissements |
| `GET` | `/api/etablissements/{id}` | Détails d'un établissement |
| `GET` | `/api/filieres` | Liste des filières |
| `GET` | `/api/filieres/{id}` | Détails d'une filière |
| `GET` | `/api/preinscriptions` | Liste des préinscriptions |
| `GET` | `/api/preinscriptions/{id}` | Détails d'une préinscription |
| `PUT` | `/api/preinscriptions/{id}/statut` | Mettre à jour le statut |
| `GET` | `/api/stats/dashboard` | Statistiques globales |
| `GET` | `/api/search` | Recherche globale |
| `POST` | `/api/validate/email` | Valider un email |

## 🧪 Tests

### Test automatique avec Python

```bash
python test_api.py
```

Ce script teste tous les endpoints et affiche les résultats.

### Test avec Postman

1. Importer la collection : `Chatbot_Preinscription_API.postman_collection.json`
2. Les variables sont préconfigurées
3. Tester chaque endpoint directement

### Test avec cURL

```bash
# Health check
curl http://127.0.0.1:5000/api/health

# Liste des établissements
curl http://127.0.0.1:5000/api/etablissements

# Liste des filières Master
curl "http://127.0.0.1:5000/api/filieres?niveau=Master"

# Statistiques
curl http://127.0.0.1:5000/api/stats/dashboard

# Recherche
curl "http://127.0.0.1:5000/api/search?q=informatique"
```

## 📊 Exemples de code

### Python (requests)

```python
import requests

# Obtenir toutes les filières Master
response = requests.get(
    'http://127.0.0.1:5000/api/filieres',
    params={'niveau': 'Master', 'disponible': 1}
)

filieres = response.json()['data']
for filiere in filieres:
    print(f"{filiere['nom']} - {filiere['frais_scolarite']} FCFA")
```

### JavaScript (fetch)

```javascript
// Obtenir les statistiques
fetch('http://127.0.0.1:5000/api/stats/dashboard')
  .then(response => response.json())
  .then(data => {
    console.log('Total préinscriptions:', data.data.preinscriptions.total);
    console.log('Top filières:', data.data.top_filieres);
  });

// Recherche
const searchTerm = 'informatique';
fetch(`http://127.0.0.1:5000/api/search?q=${searchTerm}`)
  .then(response => response.json())
  .then(data => {
    console.log('Résultats:', data.data);
  });
```

## 🔧 Caractéristiques

### Pagination

Tous les endpoints de liste supportent la pagination :

```bash
GET /api/filieres?page=1&per_page=20
```

**Réponse :**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 42,
    "total_pages": 3
  }
}
```

### Filtres

Les endpoints supportent des filtres multiples :

```bash
# Filières par niveau et établissement
GET /api/filieres?niveau=Master&etablissement_id=1

# Préinscriptions par statut
GET /api/preinscriptions?statut=nouveau

# Établissements par type et ville
GET /api/etablissements?type=université&ville=Yaoundé
```

### Gestion d'erreurs

Format standard des erreurs :

```json
{
  "success": false,
  "error": "Message d'erreur détaillé"
}
```

**Codes de statut HTTP :**
- `200` : Succès
- `201` : Ressource créée
- `400` : Requête invalide
- `404` : Ressource non trouvée
- `500` : Erreur serveur

## 📈 Statistiques disponibles

L'endpoint `/api/stats/dashboard` retourne :

- 📊 Totaux : établissements, filières, préinscriptions
- 📈 Répartition : filières par niveau, préinscriptions par statut
- 📅 Évolution : préinscriptions des 7 derniers jours
- 🏆 Top : filières les plus demandées

## 🔍 Recherche

La recherche globale permet de trouver :

```bash
# Recherche dans tout le système
GET /api/search?q=informatique&type=all

# Recherche uniquement dans les filières
GET /api/search?q=master&type=filieres

# Recherche uniquement dans les établissements
GET /api/search?q=ICT&type=etablissements
```

## ✅ Validation

Vérifier la disponibilité d'un email avant soumission :

```bash
POST /api/validate/email
Content-Type: application/json

{
  "email": "test@example.com"
}
```

**Réponse :**
```json
{
  "success": true,
  "available": false,
  "message": "Cet email est déjà utilisé"
}
```

## 🔐 Sécurité

### Implémenté

- ✅ Validation de toutes les entrées utilisateur
- ✅ Requêtes SQL paramétrées (protection contre injection)
- ✅ CORS activé pour le développement
- ✅ Gestion d'erreurs complète

### À implémenter en production

- 🔒 Authentification JWT
- 🛡️ Rate limiting
- 📊 Logging complet
- 🔐 HTTPS obligatoire
- 🔑 API Keys

## 📝 Structure des données

### Établissement

```json
{
  "id": 1,
  "nom": "ICT University",
  "code": "ICTU",
  "ville": "Yaoundé",
  "type": "université",
  "telephone": "+237 222 22 22 22",
  "email": "contact@ictu.cm",
  "site_web": "https://ictu.cm"
}
```

### Filière

```json
{
  "id": 1,
  "nom": "Licence en Informatique",
  "code": "L-INFO",
  "niveau": "Licence",
  "duree": 3,
  "frais_inscription": 25000,
  "frais_scolarite": 450000,
  "places_disponibles": 50
}
```

### Préinscription

```json
{
  "id": 1,
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean@example.com",
  "statut": "nouveau",
  "filiere": {...},
  "etablissement": {...}
}
```

## 🛠️ Développement

### Ajouter un nouvel endpoint

1. Éditer `api.py`
2. Ajouter la fonction avec le décorateur `@api_bp.route()`
3. Documenter dans `API-DOCUMENTATION.md`
4. Ajouter des tests dans `test_api.py`

### Structure du projet

```
chatbot-preinscription/
├── api.py                          # Blueprint API
├── app.py                          # Application principale
├── test_api.py                     # Tests automatisés
├── doc/
│   └── API-DOCUMENTATION.md        # Documentation complète
└── Chatbot_Preinscription_API.postman_collection.json
```

## 📞 Support

Pour toute question :

- 📧 Email : support@ictu.cm
- 📚 Documentation : [API-DOCUMENTATION.md](doc/API-DOCUMENTATION.md)
- 🐛 Issues : Créer une issue sur le dépôt Git

## 📄 Licence

© 2025 Madick Ange César - The ICT University

---

**Version :** 1.0.0  
**Dernière mise à jour :** Novembre 2025
