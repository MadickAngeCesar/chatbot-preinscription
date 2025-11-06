"""
Script de test simple pour vérifier que l'API fonctionne
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Test de l'endpoint /health"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_etablissements():
    """Test de l'endpoint /api/etablissements"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Liste des établissements")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/etablissements", timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        data = response.json()
        print(f"📄 Nombre d'établissements: {len(data.get('etablissements', []))}")
        if data.get('etablissements'):
            print(f"📄 Premier établissement: {data['etablissements'][0].get('nom')}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_filieres():
    """Test de l'endpoint /api/filieres"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Liste des filières")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/filieres", timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        data = response.json()
        print(f"📄 Nombre de filières: {len(data.get('filieres', []))}")
        if data.get('filieres'):
            print(f"📄 Première filière: {data['filieres'][0].get('nom')}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Fonction principale"""
    print("\n🚀 Début des tests de l'API")
    print("🌐 URL de base: " + BASE_URL)
    
    tests = [
        test_health,
        test_etablissements,
        test_filieres
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except KeyboardInterrupt:
            print("\n\n⚠️ Tests interrompus par l'utilisateur")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
            results.append(False)
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Tests réussis: {passed}/{total}")
    print(f"❌ Tests échoués: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés avec succès!")
    else:
        print("\n⚠️ Certains tests ont échoué")
    
    print("\n💡 Pour plus de tests, consultez QUICK-START.md")


if __name__ == "__main__":
    main()
