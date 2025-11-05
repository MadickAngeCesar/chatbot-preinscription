"""
Script de test pour le module Gemini AI
Teste la connexion et génère des réponses d'exemple
"""

import sys
import os

# Ajouter le répertoire parent (racine du projet) au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from model.gemini_chatbot import generate_response, test_gemini, conversation_context

def test_conversation_flow():
    """Teste un flux de conversation complet"""
    
    print("\n" + "="*60)
    print("🤖 TEST DU CHATBOT GEMINI AI")
    print("="*60 + "\n")
    
    # Test 1: Vérification de base
    print("📋 Test 1: Vérification de la connexion Gemini...")
    if not test_gemini():
        print("❌ La connexion à Gemini a échoué. Vérifiez votre clé API.")
        return False
    
    print("\n" + "-"*60 + "\n")
    
    # Test 2: Conversation simulée
    session_id = "test_session_001"
    test_messages = [
        ("Bonjour !", "Jean Dupont"),
        ("Quels sont les programmes disponibles en Licence ?", "Jean Dupont"),
        ("Combien coûte la Licence en Génie Logiciel ?", "Jean Dupont"),
        ("Quels documents dois-je fournir ?", "Jean Dupont"),
        ("Je veux m'inscrire", "Jean Dupont")
    ]
    
    for i, (message, user_name) in enumerate(test_messages, 1):
        print(f"💬 Utilisateur ({user_name}): {message}")
        print("\n⏳ Génération de la réponse...")
        
        try:
            response = generate_response(message, session_id, user_name)
            print(f"\n🤖 Chatbot: {response}")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            return False
        
        print("\n" + "-"*60 + "\n")
    
    # Test 3: Résumé de la conversation
    print("📊 RÉSUMÉ DE LA CONVERSATION")
    print("="*60)
    
    from model.gemini_chatbot import get_conversation_summary
    summary = get_conversation_summary(session_id)
    
    print(f"✅ Nombre de messages: {summary['message_count']}")
    print(f"✅ Dernière intention: {summary['intent']}")
    print(f"✅ Session créée: {summary['created_at']}")
    
    print("\n" + "="*60)
    print("✅ TOUS LES TESTS ONT RÉUSSI !")
    print("="*60 + "\n")
    
    return True

def test_intent_detection():
    """Teste la détection d'intentions"""
    
    print("\n" + "="*60)
    print("🎯 TEST DE DÉTECTION D'INTENTIONS")
    print("="*60 + "\n")
    
    from model.gemini_chatbot import detect_intent
    
    test_cases = [
        ("Je veux m'inscrire", "preinscription"),
        ("Quels programmes proposez-vous ?", "programmes"),
        ("Combien ça coûte ?", "frais"),
        ("Quels documents faut-il ?", "admission"),
        ("Quand est la rentrée ?", "calendrier"),
        ("Comment vous contacter ?", "contact"),
        ("Bonjour", "salutation"),
        ("Aidez-moi", "aide")
    ]
    
    success = 0
    total = len(test_cases)
    
    for message, expected_intent in test_cases:
        detected = detect_intent(message)
        status = "✅" if detected == expected_intent else "❌"
        print(f"{status} '{message}' → {detected} (attendu: {expected_intent})")
        if detected == expected_intent:
            success += 1
    
    print(f"\n📊 Résultat: {success}/{total} tests réussis ({success*100/total:.0f}%)")
    print("="*60 + "\n")

def test_fallback():
    """Teste les réponses de secours"""
    
    print("\n" + "="*60)
    print("🔄 TEST DES RÉPONSES DE SECOURS")
    print("="*60 + "\n")
    
    from model.gemini_chatbot import get_fallback_response
    
    intents = ['preinscription', 'programmes', 'frais', 'admission', 'calendrier', 'contact', 'salutation', 'aide']
    
    for intent in intents:
        response = get_fallback_response(intent)
        print(f"📌 {intent.upper()}:")
        print(f"   {response[:100]}...")
        print()

def interactive_mode():
    """Mode interactif pour tester le chatbot"""
    
    print("\n" + "="*60)
    print("💬 MODE INTERACTIF - Testez le chatbot en direct")
    print("="*60)
    print("Tapez 'quit' pour quitter\n")
    
    session_id = "interactive_session"
    user_name = "Testeur"
    
    while True:
        try:
            message = input("Vous: ").strip()
            
            if not message:
                continue
            
            if message.lower() in ['quit', 'exit', 'quitter']:
                print("\n👋 Au revoir !\n")
                break
            
            response = generate_response(message, session_id, user_name)
            print(f"\n🤖 Chatbot: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !\n")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}\n")

if __name__ == "__main__":
    print("\n🚀 TESTS DU MODULE GEMINI AI CHATBOT\n")
    
    # Menu de sélection
    print("Choisissez un test:")
    print("1. Test complet de conversation")
    print("2. Test de détection d'intentions")
    print("3. Test des réponses de secours")
    print("4. Mode interactif")
    print("5. Tous les tests")
    print()
    
    try:
        choice = input("Votre choix (1-5): ").strip()
        
        if choice == "1":
            test_conversation_flow()
        elif choice == "2":
            test_intent_detection()
        elif choice == "3":
            test_fallback()
        elif choice == "4":
            interactive_mode()
        elif choice == "5":
            test_intent_detection()
            test_fallback()
            test_conversation_flow()
        else:
            print("❌ Choix invalide")
    
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir !\n")
    except Exception as e:
        print(f"\n❌ Erreur: {e}\n")
