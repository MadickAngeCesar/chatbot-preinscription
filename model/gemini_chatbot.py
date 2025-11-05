"""
Module Gemini AI pour le Chatbot de Préinscription Universitaire
Utilise Google Gemini pour générer des réponses contextuelles et personnalisées
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

# Configuration Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY non trouvée dans .env")

# Configurer Gemini avec la clé API
genai.configure(api_key=GEMINI_API_KEY)

# ============================================
# PROMPT SYSTÈME POUR LA PRÉINSCRIPTION
# ============================================

SYSTEM_PROMPT = """Tu es un assistant virtuel spécialisé pour ICT University au Cameroun.

🎓 TON RÔLE:
Tu aides les étudiants avec leur processus de préinscription universitaire. Tu es courtois, professionnel et très informatif.

📚 PROGRAMMES DISPONIBLES:

**LICENCE (BAC+3):**
- Génie Logiciel
- Réseaux et Télécommunications
- Cybersécurité
- Intelligence Artificielle
- Science des Données

**MASTER (BAC+5):**
- Génie Logiciel Avancé
- Sécurité des Systèmes d'Information
- Intelligence Artificielle et Big Data
- Cloud Computing et DevOps
- Management des Systèmes d'Information

📋 CONDITIONS D'ADMISSION:

**Licence:**
- Baccalauréat (toutes séries, priorité C, D, F)
- Relevé de notes du BAC
- Acte de naissance
- 4 photos d'identité

**Master:**
- Licence en informatique ou domaine connexe
- Relevé de notes de Licence
- CV académique
- Lettre de motivation

💰 FRAIS (Année 2024-2025):

**Licence:**
- Inscription: 50,000 FCFA
- Scolarité: 850,000 FCFA/an

**Master:**
- Inscription: 75,000 FCFA
- Scolarité: 1,200,000 FCFA/an

📅 CALENDRIER:
- Préinscriptions: Juillet - Septembre
- Rentrée: Octobre
- Examens 1er semestre: Janvier
- Examens 2ème semestre: Juin

📍 CONTACT:
- Site web: www.ict-university.cm
- Email: admissions@ict-university.cm
- Téléphone: +237 6XX XXX XXX
- Adresse: Yaoundé, Cameroun

🎯 TES INSTRUCTIONS:

1. **Réponds en français** avec un ton professionnel mais chaleureux
2. **Sois concis** - max 150 mots par réponse sauf si plus de détails sont demandés
3. **Utilise des emojis** pour rendre les réponses plus engageantes (avec modération)
4. **Guide vers la préinscription** quand approprié
5. **Propose des actions** concrètes (ex: "Voulez-vous remplir le formulaire de préinscription ?")
6. **Si tu ne sais pas**, redirige vers le service des admissions
7. **Personnalise** les réponses selon le contexte de la conversation

📝 EXEMPLES DE RÉPONSES:

**Question sur un programme:**
"Le programme de [NOM] est une formation de [NIVEAU] sur [DURÉE]. Il couvre [DOMAINES]. Les débouchés incluent [MÉTIERS]. Souhaitez-vous en savoir plus sur les conditions d'admission ? 🎓"

**Question sur les frais:**
"Pour [NIVEAU], les frais sont: Inscription [MONTANT] + Scolarité [MONTANT]/an. Des facilités de paiement sont possibles. Voulez-vous discuter des modalités ? 💰"

**Demande de préinscription:**
"Excellent choix ! 🎉 Pour vous préinscrire, j'ai besoin de quelques informations. Cliquez sur 'Préinscription' ou je peux vous guider étape par étape. Préférez-vous quel programme ?"

IMPORTANT: Tu réponds UNIQUEMENT sur les sujets liés à ICT University et la préinscription. Pour d'autres sujets, redirige poliment vers ton domaine d'expertise.
"""

# ============================================
# CONTEXTE DES CONVERSATIONS
# ============================================

class ConversationContext:
    """Gère le contexte des conversations avec historique"""
    
    def __init__(self):
        self.conversations = {}
    
    def get_context(self, session_id):
        """Récupère le contexte d'une session"""
        if session_id not in self.conversations:
            self.conversations[session_id] = {
                'history': [],
                'user_info': {},
                'intent': None,
                'created_at': datetime.now().isoformat()
            }
        return self.conversations[session_id]
    
    def add_message(self, session_id, role, content):
        """Ajoute un message à l'historique"""
        context = self.get_context(session_id)
        context['history'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Garder seulement les 10 derniers messages
        if len(context['history']) > 10:
            context['history'] = context['history'][-10:]
    
    def update_user_info(self, session_id, info):
        """Met à jour les infos utilisateur"""
        context = self.get_context(session_id)
        context['user_info'].update(info)
    
    def set_intent(self, session_id, intent):
        """Définit l'intention de l'utilisateur"""
        context = self.get_context(session_id)
        context['intent'] = intent

# Instance globale
conversation_context = ConversationContext()

# ============================================
# CONFIGURATION DU MODÈLE GEMINI
# ============================================

# Configuration du modèle
generation_config = {
    'temperature': 0.7,  # Créativité modérée
    'top_p': 0.9,
    'top_k': 40,
    'max_output_tokens': 500,  # Limiter la longueur des réponses
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

# Initialiser le modèle
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash-exp',
    generation_config=generation_config,
    safety_settings=safety_settings
)

# ============================================
# FONCTIONS DE DÉTECTION D'INTENTION
# ============================================

def detect_intent(message):
    """Détecte l'intention de l'utilisateur"""
    message_lower = message.lower()
    
    intents = {
        'preinscription': ['préinscription', 'preinscription', "m'inscrire", 'inscription', 'postuler', 'candidature'],
        'programmes': ['programme', 'filière', 'formation', 'licence', 'master', 'cursus', 'étude'],
        'frais': ['frais', 'coût', 'prix', 'payer', 'paiement', 'combien', 'tarif'],
        'admission': ['admission', 'condition', 'requis', 'document', 'dossier', 'exigence'],
        'calendrier': ['date', 'quand', 'rentrée', 'calendrier', 'délai', 'inscription'],
        'contact': ['contact', 'téléphone', 'email', 'adresse', 'localisation', 'où'],
        'salutation': ['bonjour', 'salut', 'bonsoir', 'hello', 'hey', 'coucou'],
        'aide': ['aide', 'aider', 'comment', 'info', 'information', 'renseigner']
    }
    
    for intent, keywords in intents.items():
        if any(keyword in message_lower for keyword in keywords):
            return intent
    
    return 'general'

# ============================================
# FONCTION PRINCIPALE DE GÉNÉRATION
# ============================================

def generate_response(user_message, session_id='default', user_name=None):
    """
    Génère une réponse avec Gemini en utilisant le contexte
    
    Args:
        user_message (str): Message de l'utilisateur
        session_id (str): ID de la session pour le contexte
        user_name (str): Nom de l'utilisateur si disponible
    
    Returns:
        str: Réponse générée
    """
    try:
        # Récupérer le contexte
        context = conversation_context.get_context(session_id)
        
        # Détecter l'intention
        intent = detect_intent(user_message)
        conversation_context.set_intent(session_id, intent)
        
        # Construire le prompt avec contexte
        prompt_parts = []
        
        # Ajouter le nom si disponible
        if user_name:
            prompt_parts.append(f"[L'utilisateur s'appelle {user_name}]")
        
        # Ajouter l'intention détectée
        prompt_parts.append(f"[Intention détectée: {intent}]")
        
        # Ajouter l'historique récent (3 derniers échanges)
        if context['history']:
            recent_history = context['history'][-6:]  # 3 échanges (user + bot)
            history_text = "\n".join([
                f"{'Utilisateur' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in recent_history
            ])
            prompt_parts.append(f"\n[Historique récent:\n{history_text}]")
        
        # Ajouter le message actuel
        prompt_parts.append(f"\nUtilisateur: {user_message}")
        
        # Prompt d'enrichissement selon l'intention
        enrichments = {
            'preinscription': "\n[Guide l'utilisateur vers le formulaire de préinscription en ligne]",
            'programmes': "\n[Donne des détails sur les programmes et propose de parler d'admission]",
            'frais': "\n[Sois transparent sur les coûts et mentionne les facilités de paiement]",
            'admission': "\n[Liste les documents requis et les conditions spécifiques]",
            'salutation': "\n[Accueille chaleureusement et propose ton aide]"
        }
        
        if intent in enrichments:
            prompt_parts.append(enrichments[intent])
        
        full_prompt = "\n".join(prompt_parts)
        
        # Générer la réponse avec Gemini
        # Inclure le prompt système au début
        complete_prompt = f"{SYSTEM_PROMPT}\n\n{full_prompt}"
        
        # Utiliser l'API compatible avec version 0.3.2
        response = model.generate_content(complete_prompt)
        
        bot_response = response.text.strip()
        
        # Sauvegarder dans l'historique
        conversation_context.add_message(session_id, 'user', user_message)
        conversation_context.add_message(session_id, 'assistant', bot_response)
        
        return bot_response
    
    except Exception as e:
        print(f"❌ Erreur Gemini: {e}")
        return get_fallback_response(intent)

# ============================================
# RÉPONSES DE SECOURS
# ============================================

def get_fallback_response(intent='general'):
    """Réponses de secours si Gemini n'est pas disponible"""
    
    fallback_responses = {
        'preinscription': "Je serais ravi de vous aider avec votre préinscription ! 🎓 Pour commencer, cliquez sur le bouton 'Préinscription' ci-dessus ou dites-moi quel programme vous intéresse (Licence ou Master).",
        
        'programmes': "Nous proposons des programmes en Licence et Master dans plusieurs domaines:\n\n📚 Licence: Génie Logiciel, Réseaux, Cybersécurité, IA, Data Science\n📚 Master: Génie Logiciel Avancé, Sécurité SI, IA & Big Data, Cloud & DevOps\n\nQuel domaine vous intéresse ? 🎯",
        
        'frais': "💰 Nos frais pour 2024-2025:\n\n**Licence:**\n- Inscription: 50,000 FCFA\n- Scolarité: 850,000 FCFA/an\n\n**Master:**\n- Inscription: 75,000 FCFA\n- Scolarité: 1,200,000 FCFA/an\n\nDes facilités de paiement sont disponibles. Souhaitez-vous plus de détails ? 📊",
        
        'admission': "📋 Documents requis:\n\n**Licence:**\n- Baccalauréat\n- Relevé de notes\n- Acte de naissance\n- 4 photos\n\n**Master:**\n- Licence (informatique)\n- Relevés de notes\n- CV + Lettre de motivation\n\nVoulez-vous commencer votre préinscription ? ✅",
        
        'calendrier': "📅 Calendrier académique:\n\n- Préinscriptions: Juillet - Septembre\n- Rentrée: Octobre 2024\n- Examens S1: Janvier 2025\n- Examens S2: Juin 2025\n\nC'est le moment idéal pour vous préinscrire ! 🎓",
        
        'contact': "📞 Comment nous contacter:\n\n- 📧 Email: admissions@ict-university.cm\n- 📱 Tél: +237 6XX XXX XXX\n- 🌐 Site: www.ict-university.cm\n- 📍 Adresse: Yaoundé, Cameroun\n\nPuis-je vous aider avec autre chose ? 😊",
        
        'salutation': "Bonjour ! 👋 Je suis votre assistant virtuel pour ICT University.\n\nJe peux vous aider avec:\n- 🎓 Informations sur nos programmes\n- 📝 Processus de préinscription\n- 💰 Frais et modalités\n- 📅 Dates importantes\n\nComment puis-je vous assister aujourd'hui ? 😊",
        
        'aide': "Je suis là pour vous aider ! 🤝\n\nPosez-moi des questions sur:\n✅ Les programmes (Licence/Master)\n✅ Les conditions d'admission\n✅ Les frais de scolarité\n✅ Les dates de préinscription\n✅ Comment vous inscrire\n\nQue souhaitez-vous savoir ? 💡"
    }
    
    return fallback_responses.get(intent, 
        "Je suis votre assistant pour la préinscription à ICT University. 🎓 Comment puis-je vous aider aujourd'hui ? (programmes, admission, frais, inscription...)")

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def clear_context(session_id):
    """Efface le contexte d'une session"""
    if session_id in conversation_context.conversations:
        del conversation_context.conversations[session_id]

def get_conversation_summary(session_id):
    """Obtient un résumé de la conversation"""
    context = conversation_context.get_context(session_id)
    return {
        'message_count': len(context['history']),
        'intent': context['intent'],
        'user_info': context['user_info'],
        'created_at': context['created_at']
    }

# ============================================
# FONCTION DE TEST
# ============================================

def test_gemini():
    """Teste la connexion avec Gemini"""
    try:
        test_response = generate_response("Bonjour, je veux m'inscrire", "test_session")
        print("✅ Gemini fonctionne correctement!")
        print(f"Réponse de test: {test_response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Erreur de test Gemini: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Test du module Gemini AI...")
    test_gemini()
