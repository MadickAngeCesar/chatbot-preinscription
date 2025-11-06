# 🤖 Intégration Gemini AI - Documentation

## Vue d'ensemble

Le chatbot de préinscription utilise **Google Gemini AI** pour générer des réponses intelligentes et contextuelles. Le système est personnalisé pour ICT University avec des prompts spécifiques au domaine de la préinscription universitaire.

## Architecture

```
┌─────────────────┐
│   Frontend      │ (chat.html)
│   (JavaScript)  │
└────────┬────────┘
         │
         │ POST /api/message
         │
┌────────▼────────┐
│   Flask API     │ (app.py)
│   - Validation  │
│   - Session     │
└────────┬────────┘
         │
         │ generate_response()
         │
┌────────▼────────────────┐
│  Gemini Chatbot Module  │ (gemini_chatbot.py)
│  - Context Management   │
│  - Intent Detection     │
│  - Prompt Engineering   │
└────────┬────────────────┘
         │
         │ Gemini API Call
         │
┌────────▼────────┐
│  Google Gemini  │
│  (gemini-pro)   │
└─────────────────┘
```

## Fichiers principaux

### 1. `gemini_chatbot.py` (Module principal)

**Fonctions clés:**

- `generate_response(user_message, session_id, user_name)`: Génère une réponse avec Gemini
- `detect_intent(message)`: Détecte l'intention de l'utilisateur
- `get_fallback_response(intent)`: Réponses de secours si Gemini échoue
- `test_gemini()`: Teste la connexion Gemini

**Classes:**

- `ConversationContext`: Gère l'historique et le contexte des conversations
  - Conserve les 10 derniers messages
  - Stocke les informations utilisateur
  - Track l'intention courante

### 2. `app.py` (Intégration Flask)

**Endpoint modifié:**

```python
@app.route('/api/message', methods=['POST'])
def api_message():
    # Récupère le nom de l'utilisateur si connecté
    user_name = session.get('user_name')
    
    # Génère la réponse avec Gemini
    bot_response = generate_response(message, session_id, user_name)
    
    # Fallback vers l'ancienne fonction en cas d'erreur
    if not bot_response:
        bot_response = get_bot_response(message, session_id)
```

### 3. `test_gemini.py` (Tests)

**Tests disponibles:**

1. Test de connexion Gemini
2. Test de conversation complète (5 échanges)
3. Test de détection d'intentions
4. Test des réponses de secours
5. Mode interactif

## Configuration

### Variables d'environnement (`.env`)

```env
GEMINI_API_KEY=AIzaSyDHXYrVS1GM21dz1vjvSivKGoi0gSJxtME
```

### Paramètres du modèle

```python
generation_config = {
    'temperature': 0.7,      # Créativité modérée
    'top_p': 0.9,            # Sampling nucléaire
    'top_k': 40,             # Top-K sampling
    'max_output_tokens': 500 # Max 500 tokens (~150 mots)
}
```

**Explication:**

- **temperature (0.7)**: Balance entre créativité et cohérence
- **top_p (0.9)**: Utilise les 90% de probabilité cumulée
- **top_k (40)**: Considère les 40 tokens les plus probables
- **max_output_tokens (500)**: Limite la longueur des réponses

## Prompt Engineering

### Prompt système

Le prompt système définit le rôle, les connaissances et le comportement du chatbot:

#### Structure:

1. **Rôle**: Assistant virtuel pour ICT University
2. **Connaissance du domaine**:
   - Programmes (Licence/Master)
   - Conditions d'admission
   - Frais de scolarité
   - Calendrier académique
   - Contact
3. **Instructions comportementales**:
   - Répondre en français
   - Max 150 mots par réponse
   - Utiliser des emojis avec modération
   - Guider vers la préinscription
   - Proposer des actions concrètes
4. **Exemples de réponses** (few-shot learning)

### Enrichissement contextuel

Le système enrichit chaque message avec:

```python
prompt_parts = [
    f"[L'utilisateur s'appelle {user_name}]",     # Personnalisation
    f"[Intention détectée: {intent}]",             # Context
    f"[Historique récent: ...]",                   # Mémoire
    f"Utilisateur: {user_message}",                # Message
    f"[Guide l'utilisateur vers...]"               # Directive
]
```

## Détection d'intentions

### Intentions supportées:

| Intention | Mots-clés | Action |
|-----------|-----------|--------|
| **preinscription** | préinscription, inscription, m'inscrire | Guide vers formulaire |
| **programmes** | programme, filière, licence, master | Liste les formations |
| **frais** | frais, coût, prix, tarif | Affiche les tarifs |
| **admission** | admission, condition, document | Liste les requis |
| **calendrier** | date, quand, rentrée | Affiche le calendrier |
| **contact** | contact, email, téléphone | Infos de contact |
| **salutation** | bonjour, salut, hello | Message d'accueil |
| **aide** | aide, comment, info | Menu d'aide |

### Algorithme:

```python
def detect_intent(message):
    message_lower = message.lower()
    for intent, keywords in intents.items():
        if any(keyword in message_lower for keyword in keywords):
            return intent
    return 'general'
```

## Gestion du contexte

### Historique de conversation

- **Capacité**: 10 derniers messages (5 échanges)
- **Structure**: `{role: 'user'|'assistant', content: str, timestamp: ISO}`
- **Utilisation**: Passé à Gemini pour maintenir la cohérence

### Informations utilisateur

Stockées dans le contexte:
- Nom et prénom
- Programme d'intérêt
- Niveau d'études
- Questions posées

## Réponses de secours (Fallback)

Si Gemini échoue, le système utilise des réponses pré-définies:

```python
fallback_responses = {
    'preinscription': "Je serais ravi de vous aider...",
    'programmes': "Nous proposons des programmes en...",
    # ... 8 réponses au total
}
```

**Raisons de fallback:**

- Erreur API Gemini (rate limit, quota)
- Timeout réseau
- Erreur de validation
- API key invalide

## Sécurité

### Paramètres de sécurité Gemini:

```python
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]
```

### Validation des entrées:

- Message non vide
- Longueur max: implicite via max_output_tokens
- Sanitization: Flask jsonify

## Tests

### Exécuter les tests:

```bash
# Test complet
python test_gemini.py

# Menu interactif
python test_gemini.py
> Choix: 4

# Test de connexion uniquement
python -c "from gemini_chatbot import test_gemini; test_gemini()"
```

### Tests unitaires:

1. **test_conversation_flow()**: Simule 5 échanges
2. **test_intent_detection()**: Vérifie 8 intentions
3. **test_fallback()**: Teste les 8 réponses de secours
4. **interactive_mode()**: Mode REPL pour tests manuels

## Performances

### Temps de réponse typique:

- **Première requête**: 2-4 secondes (cold start)
- **Requêtes suivantes**: 0.5-2 secondes
- **Avec historique (10 msg)**: +0.2-0.5 secondes

### Optimisations:

1. **Limitation de l'historique**: Max 10 messages (vs illimité)
2. **Tokens optimisés**: max_output_tokens=500 (vs 2048 par défaut)
3. **Fallback rapide**: Réponses pré-définies en cas d'erreur
4. **Context trimming**: Compression automatique de l'historique

## Monitoring

### Logs à surveiller:

```python
print(f"❌ Erreur Gemini: {e}")          # Erreurs API
print(f"⚠️ Erreur Gemini, fallback: {e}") # Utilisation fallback
print("✅ Gemini fonctionne!")           # Succès test
```

### Métriques importantes:

- Taux d'utilisation Gemini vs Fallback
- Temps de réponse moyen
- Intentions détectées (distribution)
- Sessions actives
- Messages par session

## Dépannage

### Problème: "GEMINI_API_KEY non trouvée"

**Solution:**
```bash
# Vérifier .env
cat .env | grep GEMINI_API_KEY

# Recharger les variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"
```

### Problème: "Erreur 429 - Rate limit"

**Solution:**
- Vérifier quota API: https://aistudio.google.com/app/apikey
- Implémenter rate limiting côté serveur
- Utiliser fallback temporairement

### Problème: Réponses incohérentes

**Solution:**
1. Augmenter `temperature` pour plus de créativité (0.7 → 0.9)
2. Réduire `temperature` pour plus de cohérence (0.7 → 0.5)
3. Vérifier l'historique (trop ancien?)
4. Améliorer le prompt système

### Problème: Réponses trop longues

**Solution:**
- Réduire `max_output_tokens`: 500 → 300
- Ajouter instruction dans le prompt: "Réponse max 100 mots"

### Problème: Gemini répond hors sujet

**Solution:**
1. Renforcer le prompt système avec "UNIQUEMENT sur ICT University"
2. Ajouter validation post-génération
3. Utiliser fallback si hors sujet détecté

## Améliorations futures

### Court terme:

- [ ] Ajouter streaming responses (chunks en temps réel)
- [ ] Implémenter cache des réponses fréquentes
- [ ] Ajouter métriques de satisfaction utilisateur
- [ ] Créer dashboard admin pour monitoring

### Moyen terme:

- [ ] Fine-tuning du modèle avec données réelles
- [ ] Multi-langue (français, anglais)
- [ ] Intégration avec base de connaissances vectorielle
- [ ] A/B testing de différents prompts

### Long terme:

- [ ] Passage à Gemini 1.5 Pro (contexte 1M tokens)
- [ ] Génération d'images (programmes, campus)
- [ ] Analyse de sentiment des conversations
- [ ] Prédiction de l'intention d'inscription

## Ressources

### Documentation officielle:

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Python SDK](https://github.com/google/generative-ai-python)

### Limites Gemini API (gratuit):

- 60 requêtes/minute
- 1500 requêtes/jour
- 1 million tokens/jour

### Support:

- Email: support@ict-university.cm
- Documentation: `doc/GEMINI-INTEGRATION.md`
- Tests: `python test_gemini.py`

---

**Dernière mise à jour**: Novembre 2024  
**Auteur**: Madick Ange César  
**Version**: 1.0.0
