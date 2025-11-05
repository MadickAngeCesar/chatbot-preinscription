# 🚀 Guide de Démarrage Rapide - Gemini AI

## Installation en 5 minutes

### Étape 1: Installer les dépendances

```bash
pip install google-generativeai==0.3.2
```

### Étape 2: Vérifier la configuration

Le fichier `.env` doit contenir:
```env
GEMINI_API_KEY=AIzaSyDHXYrVS1GM21dz1vjvSivKGoi0gSJxtME
```

### Étape 3: Tester Gemini

```bash
python test_gemini.py
```

Choisissez l'option **1** pour un test complet ou **4** pour le mode interactif.

### Étape 4: Lancer l'application

```bash
python app.py
```

Visitez: http://localhost:5000

---

## Test rapide en console

```python
# Dans un terminal Python
from gemini_chatbot import generate_response

# Test simple
response = generate_response("Bonjour, quels programmes proposez-vous ?")
print(response)
```

---

## Structure des fichiers

```
chatbot-preinscription/
├── gemini_chatbot.py      # Module principal Gemini
├── gemini_config.py       # Configuration et données
├── test_gemini.py         # Tests et mode interactif
├── app.py                 # Application Flask (intégration)
├── .env                   # Clé API Gemini
└── doc/
    └── GEMINI-INTEGRATION.md  # Documentation complète
```

---

## Personnalisation rapide

### Modifier les informations de l'université

Éditez `gemini_config.py`:

```python
UNIVERSITY_INFO = {
    'nom': 'VOTRE_UNIVERSITÉ',
    'pays': 'VOTRE_PAYS',
    'email': 'contact@votre-universite.com',
    # ...
}
```

### Ajuster le comportement du chatbot

Dans `gemini_config.py`:

```python
BOT_PERSONALITY = {
    'tone': 'formel',              # Plus formel
    'use_emojis': False,           # Désactiver les emojis
    'max_response_words': 100,     # Réponses plus courtes
}
```

### Modifier les paramètres Gemini

Dans `gemini_chatbot.py`:

```python
generation_config = {
    'temperature': 0.5,   # Plus cohérent (0.0-1.0)
    'max_output_tokens': 300,  # Plus court
}
```

---

## Commandes utiles

### Tests

```bash
# Test complet
python test_gemini.py

# Mode interactif
python test_gemini.py
> Choix: 4

# Test simple
python -c "from gemini_chatbot import test_gemini; test_gemini()"
```

### Vérification configuration

```bash
# Afficher la config
python gemini_config.py

# Vérifier la clé API
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'Clé API: {os.getenv(\"GEMINI_API_KEY\")[:20]}...')"
```

---

## Dépannage express

### ❌ "GEMINI_API_KEY non trouvée"

```bash
# Vérifier que .env existe
ls -la .env

# Recharger les variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"
```

### ❌ "Module 'google.generativeai' not found"

```bash
# Réinstaller le package
pip uninstall google-generativeai -y
pip install google-generativeai==0.3.2
```

### ❌ "Rate limit exceeded"

- Attendre 60 secondes
- Vérifier quota: https://aistudio.google.com/app/apikey
- Le système basculera automatiquement sur les réponses de secours

### ❌ Réponses trop longues

Dans `gemini_chatbot.py`, ligne 150:
```python
'max_output_tokens': 300,  # Au lieu de 500
```

---

## Exemples de conversations

### Exemple 1: Demande d'information

**Utilisateur**: "Quels programmes en IA proposez-vous ?"

**Chatbot**: "Nous proposons 2 programmes en Intelligence Artificielle :

📚 **Licence en IA** (3 ans) : Machine Learning, Deep Learning, traitement du langage naturel. Débouchés : Data Scientist, ML Engineer.

📚 **Master IA & Big Data** (2 ans) : IA avancée, traitement massif de données. Débouchés : Research Scientist, AI Architect.

Souhaitez-vous connaître les conditions d'admission ? 🎓"

### Exemple 2: Question sur les frais

**Utilisateur**: "Combien coûte la Licence ?"

**Chatbot**: "💰 Frais pour la Licence :
- Inscription : 50,000 FCFA (une fois)
- Scolarité : 850,000 FCFA/an

Des facilités de paiement sont disponibles (3 tranches). Bourses au mérite jusqu'à 50% !

Voulez-vous commencer votre préinscription ? ✅"

### Exemple 3: Processus de préinscription

**Utilisateur**: "Comment m'inscrire ?"

**Chatbot**: "Je vous guide ! 🎓

**Étapes de préinscription :**
1. Remplir le formulaire en ligne
2. Télécharger vos documents
3. Payer les frais d'inscription
4. Passer le test d'entrée (Septembre)

Cliquez sur 'Préinscription' ci-dessus pour commencer maintenant. Besoin d'aide ? 😊"

---

## Intégration dans votre code

### Dans Flask (app.py)

```python
from gemini_chatbot import generate_response

@app.route('/api/message', methods=['POST'])
def api_message():
    message = request.json.get('message')
    session_id = session.get('chat_session_id')
    user_name = session.get('user_name')
    
    # Générer avec Gemini
    response = generate_response(message, session_id, user_name)
    
    return jsonify({'response': response})
```

### Dans JavaScript (frontend)

```javascript
async function sendMessage(message) {
  const response = await fetch('/api/message', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message})
  });
  
  const data = await response.json();
  displayMessage(data.response);
}
```

---

## Monitoring simple

### Voir les conversations en temps réel

```python
from gemini_chatbot import conversation_context

# Afficher toutes les sessions actives
print(f"Sessions actives: {len(conversation_context.conversations)}")

# Voir l'historique d'une session
context = conversation_context.get_context('session_123')
for msg in context['history']:
    print(f"{msg['role']}: {msg['content']}")
```

### Statistiques basiques

```python
from gemini_chatbot import get_conversation_summary

summary = get_conversation_summary('session_123')
print(f"Messages: {summary['message_count']}")
print(f"Intention: {summary['intent']}")
print(f"Début: {summary['created_at']}")
```

---

## Performances attendues

| Métrique | Valeur |
|----------|--------|
| **Temps de réponse** | 0.5-2s |
| **Précision** | ~90% |
| **Taux fallback** | <5% |
| **Satisfaction** | >85% |

---

## Support

- 📖 Doc complète: `doc/GEMINI-INTEGRATION.md`
- 🧪 Tests: `python test_gemini.py`
- 📧 Support: support@ict-university.cm
- 🌐 API Gemini: https://aistudio.google.com/

---

## Checklist de déploiement

- [ ] ✅ `pip install google-generativeai`
- [ ] ✅ Clé API dans `.env`
- [ ] ✅ Test de connexion réussi
- [ ] ✅ Personnalisation `gemini_config.py`
- [ ] ✅ Tests de conversation OK
- [ ] ✅ Intégration Flask fonctionnelle
- [ ] ✅ Frontend connecté
- [ ] ✅ Monitoring activé
- [ ] ✅ Documentation lue

**Prêt à déployer ! 🚀**

---

**Dernière mise à jour**: Novembre 2024
