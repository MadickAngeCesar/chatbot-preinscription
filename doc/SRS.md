
# SRS — Spécification des Exigences Logicielle

Version: 1.0

Date: 2025-11-04

Projet: Chatbot de Préinscription Universitaire

Auteur: Madick Ange César (baseline from README)

## 1. Introduction

### 1.1 But du document
Ce document décrit les exigences fonctionnelles et non-fonctionnelles du système "Chatbot de Préinscription Universitaire". Il sert de référence pour les développeurs, testeurs et parties prenantes lors de la conception, du développement et de la validation.

### 1.2 Portée du système
Le système est une application web qui fournit :
- un chatbot intelligent pour assister les étudiants sur la préinscription ;
- un formulaire de préinscription guidé et stocké en base ;
- la persistance des conversations et des préinscriptions dans une base SQLite ;
- une API REST minimale pour la communication client/serveur ;
- une interface web responsive (PC et mobile).

### 1.3 Définitions, acronymes et abréviations
- SRS : Software Requirements Specification
- SDD : Software Design Document
- UI : User Interface
- API : Application Programming Interface
- DB : Base de données

### 1.4 Références
- README.md (présent dans le dépôt) — description générale du projet

## 2. Description générale

### 2.1 Contexte d'utilisation
L'utilisateur final (étudiant) accède à l'application via un navigateur. Le chatbot aide à répondre aux questions (programmes, documents requis, frais), guide vers le formulaire de préinscription et enregistre les données.

### 2.2 Parties prenantes
- Étudiants (utilisateurs finaux)
- Administrateurs / personnel de l'université (consommation des préinscriptions)
- Développeurs et testeurs

### 2.3 Hypothèses et dépendances
- L'application s'exécute sur un serveur Flask (dev ou production) ;
- La base de données est SQLite (fichier local) ;
- Le modèle IA est encapsulé dans le dossier `model/` et accessible localement (pas d'API externe imposée) ;
- Le navigateur client supporte JavaScript moderne.

## 3. Exigences fonctionnelles

Les exigences sont numérotées RF-1, RF-2, etc.

### RF-1 : Authentification / Session
- RF-1.1 : Le système doit gérer des sessions utilisateur via Flask pour maintenir l'état de la conversation.

### RF-2 : Chatbot — conversation
- RF-2.1 : L'utilisateur peut envoyer un message textuel au chatbot via l'interface web.
- RF-2.2 : Le chatbot doit répondre en temps raisonnable (ex: < 3s en conditions normales) en utilisant le modèle IA local.
- RF-2.3 : Les échanges (message utilisateur + réponse) doivent être stockés en DB (table `messages`/`logs`).

### RF-3 : Guidage vers le formulaire de préinscription
- RF-3.1 : Le chatbot doit être capable d'initier/rediriger l'utilisateur vers le formulaire si la préinscription est demandée.
- RF-3.2 : Le formulaire doit permettre la saisie des champs essentiels (nom, prénom, email, téléphone, programme choisi, documents joints en option) et valider les champs côté client et serveur.
- RF-3.3 : Les données soumises doivent être persistées dans la table `preinscriptions`.

### RF-4 : API REST
- RF-4.1 : Fournir un endpoint POST `/api/message` pour envoyer un message et recevoir la réponse du chatbot.
- RF-4.2 : Fournir un endpoint POST `/api/preinscription` pour soumettre le formulaire.
- RF-4.3 : Fournir un endpoint GET `/api/preinscriptions` (optionnel, protégé) pour lister les préinscriptions.

### RF-5 : Administration (optionnel)
- RF-5.1 : L'administrateur peut consulter les préinscriptions et les logs de conversation.

## 4. Exigences non-fonctionnelles

### RNF-1 : Performances
- RNF-1.1 : Le temps de réponse moyen du chatbot doit rester < 3s en conditions locales raisonnables.

### RNF-2 : Sécurité
- RNF-2.1 : Toutes les saisies utilisateurs doivent être validées et assainies côté serveur pour éviter les injections.
- RNF-2.2 : Les endpoints administrateurs doivent être protégés via une authentification minimale (session ou token).

### RNF-3 : Fiabilité et persistance
- RNF-3.1 : Les données critiques (préinscriptions) doivent être conservées dans SQLite et récupérables après redémarrage.

### RNF-4 : Portabilité
- RNF-4.1 : Le projet doit être exécutable sur un poste de développement Windows / Linux / Mac avec Python 3.8+ et Flask.

### RNF-5 : Usabilité
- RNF-5.1 : L'interface doit être responsive et accessible sur mobile ; messages clairs en cas d'erreur.

### RNF-6 : Localisation
- RNF-6.1 : L'application doit au minimum supporter le français (contenu en français par défaut).

## 5. Données et exigences de stockage

### 5.1 Modèle de données (haut niveau)
- Table `users` (optionnelle) : id, nom, prenom, email, téléphone, role
- Table `preinscriptions` : id, nom, prenom, email, telephone, programme, date_soumission, statut, meta_json
- Table `messages` : id, session_id, role (user/bot), contenu, timestamp

### 5.2 Contraintes de conservation
- Les préinscriptions doivent être conservées indéfiniment (ou jusqu'à suppression/archivage manuel).

## 6. Interfaces externes

### 6.1 Interfaces utilisateur
- Pages HTML : `index.html`, `chat.html`, `preinscription.html` (templates existants dans `templates/`).

### 6.2 Interfaces système
- Endpoints REST listés en RF-4.

### 6.3 Interfaces logicielles
- Module IA local dans `model/` exposant une API interne (ex: fonction `respond(message, session_id)`).

## 7. Critères d'acceptation
- CA-1 : L'utilisateur peut démarrer une conversation et obtenir une réponse cohérente du chatbot.
- CA-2 : Le formulaire de préinscription stocke correctement les données en DB et renvoie un statut 200.
- CA-3 : Les messages sont persistés dans la table `messages`.
- CA-4 : Le système passe les tests automatisés basiques (tests unitaires pour endpoints et validation du formulaire).

## 8. Priorités et plan de versions
- MVP (v1.0) : Chat UI, moteur de réponse simple (règles ou modèle basique), formulaire de préinscription, stockage SQLite, endpoints REST.
- v1.1 : Améliorations du modèle IA, interface admin, gestion de fichiers joints.

## 9. Annexes
- README.md pour l'installation et l'exécution locale.
- Doc technique (SDD) pour l'implémentation et la conception détaillée.

---

Fin du SRS (v1.0)
