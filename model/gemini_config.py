"""
Configuration Gemini AI - Personnalisation des prompts et paramètres
Modifiez ce fichier pour adapter le chatbot à vos besoins
"""

# ============================================
# INFORMATIONS UNIVERSITÉ (À PERSONNALISER)
# ============================================

UNIVERSITY_INFO = {
    'nom': 'ICT University',
    'pays': 'Cameroun',
    'ville': 'Yaoundé',
    'site_web': 'www.ict-university.cm',
    'email': 'admissions@ict-university.cm',
    'telephone': '+237 6XX XXX XXX',
    'annee_academique': '2024-2025'
}

# ============================================
# PROGRAMMES ACADÉMIQUES
# ============================================

PROGRAMMES = {
    'licence': {
        'duree': '3 ans (BAC+3)',
        'programmes': [
            {
                'nom': 'Génie Logiciel',
                'description': 'Développement d\'applications, architecture logicielle, gestion de projets',
                'debouches': ['Développeur Full-Stack', 'Architecte Logiciel', 'Chef de Projet IT']
            },
            {
                'nom': 'Réseaux et Télécommunications',
                'description': 'Infrastructure réseau, protocoles, administration systèmes',
                'debouches': ['Administrateur Réseau', 'Ingénieur Télécom', 'Architecte Cloud']
            },
            {
                'nom': 'Cybersécurité',
                'description': 'Sécurité des systèmes, cryptographie, ethical hacking',
                'debouches': ['Expert Cybersécurité', 'Pentester', 'Analyste SOC']
            },
            {
                'nom': 'Intelligence Artificielle',
                'description': 'Machine Learning, Deep Learning, traitement du langage naturel',
                'debouches': ['Data Scientist', 'ML Engineer', 'Chercheur IA']
            },
            {
                'nom': 'Science des Données',
                'description': 'Analyse de données, visualisation, Big Data',
                'debouches': ['Data Analyst', 'Business Intelligence', 'Data Engineer']
            }
        ]
    },
    'master': {
        'duree': '2 ans (BAC+5)',
        'programmes': [
            {
                'nom': 'Génie Logiciel Avancé',
                'description': 'Architecture distribuée, DevOps, qualité logicielle',
                'debouches': ['Lead Developer', 'Architecte Solutions', 'CTO']
            },
            {
                'nom': 'Sécurité des Systèmes d\'Information',
                'description': 'Audit sécurité, conformité, gestion des risques',
                'debouches': ['RSSI', 'Consultant Sécurité', 'Auditeur IT']
            },
            {
                'nom': 'Intelligence Artificielle et Big Data',
                'description': 'IA avancée, traitement massif de données, recherche',
                'debouches': ['Research Scientist', 'AI Architect', 'Chief Data Officer']
            },
            {
                'nom': 'Cloud Computing et DevOps',
                'description': 'Infrastructure cloud, automatisation, conteneurisation',
                'debouches': ['Cloud Architect', 'DevOps Engineer', 'SRE']
            },
            {
                'nom': 'Management des Systèmes d\'Information',
                'description': 'Stratégie IT, gouvernance, transformation digitale',
                'debouches': ['CIO', 'IT Manager', 'Consultant Stratégie Digitale']
            }
        ]
    }
}

# ============================================
# CONDITIONS D'ADMISSION
# ============================================

ADMISSION = {
    'licence': {
        'diplome_requis': 'Baccalauréat (toutes séries, priorité C, D, F)',
        'documents': [
            'Copie certifiée du Baccalauréat',
            'Relevé de notes du BAC',
            'Acte de naissance',
            '4 photos d\'identité récentes',
            'Certificat de nationalité (pour les étrangers)'
        ],
        'selection': 'Dossier + Test d\'entrée (Mathématiques, Logique, Anglais)',
        'note_minimum': 'Moyenne BAC ≥ 12/20 (recommandé)'
    },
    'master': {
        'diplome_requis': 'Licence en Informatique ou domaine connexe',
        'documents': [
            'Copie certifiée de la Licence',
            'Relevés de notes de Licence (tous les semestres)',
            'CV académique et professionnel',
            'Lettre de motivation (1-2 pages)',
            '2 lettres de recommandation',
            'Copie du Baccalauréat'
        ],
        'selection': 'Dossier + Entretien de motivation',
        'note_minimum': 'Moyenne Licence ≥ 13/20 (recommandé)'
    }
}

# ============================================
# FRAIS DE SCOLARITÉ
# ============================================

FRAIS = {
    'licence': {
        'inscription': '50,000 FCFA (une fois)',
        'scolarite_annuelle': '850,000 FCFA',
        'total_l1': '900,000 FCFA',
        'facilites': [
            'Paiement en 3 tranches (Octobre, Janvier, Avril)',
            'Bourses au mérite (jusqu\'à 50%)',
            'Prêts étudiants partenaires'
        ]
    },
    'master': {
        'inscription': '75,000 FCFA (une fois)',
        'scolarite_annuelle': '1,200,000 FCFA',
        'total_m1': '1,275,000 FCFA',
        'facilites': [
            'Paiement en 3 tranches',
            'Bourses d\'excellence (jusqu\'à 70%)',
            'Assistanat d\'enseignement (rémunéré)'
        ]
    },
    'autres_frais': {
        'carte_etudiant': '5,000 FCFA/an',
        'bibliotheque': 'Inclus',
        'wifi_campus': 'Inclus',
        'acces_laboratoires': 'Inclus'
    }
}

# ============================================
# CALENDRIER ACADÉMIQUE
# ============================================

CALENDRIER = {
    'preinscriptions': {
        'debut': 'Juillet',
        'fin': 'Septembre',
        'plateforme': 'En ligne sur www.ict-university.cm/admission'
    },
    'tests_admission': {
        'licence': 'Dernière semaine de Septembre',
        'master': 'Entretiens individuels (Septembre)'
    },
    'rentree': {
        'date': 'Première semaine d\'Octobre',
        'integration': '1 semaine d\'intégration et orientation'
    },
    'semestre_1': {
        'cours': 'Octobre - Décembre',
        'examens': 'Dernière semaine de Janvier',
        'rattrapage': 'Première semaine de Février'
    },
    'semestre_2': {
        'cours': 'Février - Mai',
        'examens': 'Dernière semaine de Juin',
        'rattrapage': 'Première semaine de Juillet'
    },
    'vacances': {
        'noel': '2 semaines (23 Dec - 6 Jan)',
        'paques': '1 semaine (variable)',
        'ete': 'Juillet - Septembre'
    }
}

# ============================================
# STAGES ET ALTERNANCE
# ============================================

STAGES = {
    'licence': {
        'obligatoire': True,
        'duree': '2-3 mois (fin L3)',
        'periode': 'Juillet - Septembre',
        'accompagnement': 'Encadrement académique + Tuteur entreprise',
        'partenaires': ['Entreprises locales', 'Startups', 'Multinationales']
    },
    'master': {
        'obligatoire': True,
        'duree': '6 mois (fin M2)',
        'periode': 'Janvier - Juin',
        'remuneration': 'Possible selon l\'entreprise',
        'debouche': 'Souvent transformé en CDI'
    }
}

# ============================================
# VIE ÉTUDIANTE
# ============================================

VIE_CAMPUS = {
    'clubs': [
        'Club Développement (Web, Mobile, Desktop)',
        'Club Cybersécurité & CTF',
        'Club IA & Robotique',
        'Club Entrepreneuriat Tech'
    ],
    'evenements': [
        'Hackathon annuel (Prix: jusqu\'à 500,000 FCFA)',
        'Conférences tech (speakers internationaux)',
        'Job Fair (recrutement)',
        'Alumni Meetups'
    ],
    'infrastructures': [
        'Bibliothèque numérique (10,000+ ressources)',
        'Laboratoires informatiques (200+ postes)',
        'Wifi haut débit (100 Mbps)',
        'Espaces de coworking',
        'Cafétéria'
    ]
}

# ============================================
# PERSONNALITÉ DU CHATBOT
# ============================================

BOT_PERSONALITY = {
    'tone': 'professionnel_amical',  # Options: formel, professionnel_amical, decontracte
    'use_emojis': True,
    'max_response_words': 150,
    'language': 'fr',  # Options: fr, en, fr_en (bilingue)
    'proactivity': 'medium',  # Options: low, medium, high (suggestions proactives)
    'humor_level': 'subtle'  # Options: none, subtle, moderate
}

# ============================================
# INSTRUCTIONS SPÉCIALES
# ============================================

SPECIAL_INSTRUCTIONS = """
RÈGLES SPÉCIFIQUES:

1. **Personnalisation**: Utilise le prénom de l'utilisateur quand disponible
2. **Orientation**: Guide subtilement vers la préinscription après 2-3 échanges informatifs
3. **Clarté**: Reformule les questions ambiguës avant de répondre
4. **Empathie**: Reconnaît le stress du processus d'admission
5. **Action**: Chaque réponse doit proposer une action concrète ou une question de suivi
6. **Limites**: Si tu ne sais pas, recommande de contacter le service des admissions
7. **Positivité**: Encourage et motive les candidats

EXEMPLES DE PHRASES TYPES:

- "Excellent choix ! Le programme de [X] est très demandé 🎓"
- "Je comprends votre préoccupation concernant [Y]. Voici ce qu'il faut savoir..."
- "Pour résumer simplement: [réponse concise]"
- "Voulez-vous que je vous guide étape par étape ?"
- "Avez-vous d'autres questions avant de commencer votre préinscription ?"

RÉPONSES INTERDITES:

❌ "Je ne sais pas" (utiliser: "Pour cette question spécifique, contactez admissions@...")
❌ Informations contradictoires avec la base de données
❌ Promesses non officielles (bourses garanties, admission certaine)
❌ Conseils financiers personnels
❌ Sujets hors du cadre universitaire
"""

# ============================================
# PARAMÈTRES GEMINI (AVANCÉS)
# ============================================

GEMINI_CONFIG = {
    'model_name': 'gemini-pro',
    'generation_config': {
        'temperature': 0.7,  # 0.0 = déterministe, 1.0 = créatif
        'top_p': 0.9,
        'top_k': 40,
        'max_output_tokens': 500,
        'candidate_count': 1  # Nombre de réponses à générer
    },
    'safety_settings': [
        {
            'category': 'HARM_CATEGORY_HARASSMENT',
            'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
        },
        {
            'category': 'HARM_CATEGORY_HATE_SPEECH',
            'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
        },
        {
            'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
            'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
        },
        {
            'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
            'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
        }
    ]
}

# ============================================
# MÉTRIQUES ET MONITORING
# ============================================

METRICS = {
    'track_intent_distribution': True,
    'track_response_time': True,
    'track_fallback_usage': True,
    'track_user_satisfaction': False,  # À implémenter
    'log_conversations': True,
    'anonymize_logs': True
}

# ============================================
# EXPORT POUR UTILISATION
# ============================================

def get_complete_context():
    """Retourne tout le contexte pour le prompt"""
    return {
        'university': UNIVERSITY_INFO,
        'programmes': PROGRAMMES,
        'admission': ADMISSION,
        'frais': FRAIS,
        'calendrier': CALENDRIER,
        'stages': STAGES,
        'vie_campus': VIE_CAMPUS
    }

def get_formatted_prompt():
    """Génère le prompt système complet avec toutes les infos"""
    context = get_complete_context()
    
    # Format programmes
    programmes_text = ""
    for niveau, data in PROGRAMMES.items():
        programmes_text += f"\n**{niveau.upper()} ({data['duree']}):**\n"
        for prog in data['programmes']:
            programmes_text += f"- {prog['nom']}: {prog['description']}\n"
    
    # Format frais
    frais_text = f"""
**LICENCE:**
- Inscription: {FRAIS['licence']['inscription']}
- Scolarité: {FRAIS['licence']['scolarite_annuelle']}/an

**MASTER:**
- Inscription: {FRAIS['master']['inscription']}
- Scolarité: {FRAIS['master']['scolarite_annuelle']}/an
"""
    
    return f"""Tu es l'assistant virtuel de {UNIVERSITY_INFO['nom']} au {UNIVERSITY_INFO['pays']}.

🎓 PROGRAMMES DISPONIBLES:
{programmes_text}

💰 FRAIS:
{frais_text}

📅 CALENDRIER:
- Préinscriptions: {CALENDRIER['preinscriptions']['debut']} - {CALENDRIER['preinscriptions']['fin']}
- Rentrée: {CALENDRIER['rentree']['date']}

📞 CONTACT:
- Email: {UNIVERSITY_INFO['email']}
- Site: {UNIVERSITY_INFO['site_web']}

{SPECIAL_INSTRUCTIONS}
"""

if __name__ == "__main__":
    print("📋 Configuration Gemini AI Chatbot")
    print("="*60)
    print(f"\n🏫 Université: {UNIVERSITY_INFO['nom']}")
    print(f"📚 Programmes Licence: {len(PROGRAMMES['licence']['programmes'])}")
    print(f"📚 Programmes Master: {len(PROGRAMMES['master']['programmes'])}")
    print(f"💰 Frais Licence: {FRAIS['licence']['scolarite_annuelle']}")
    print(f"💰 Frais Master: {FRAIS['master']['scolarite_annuelle']}")
    print(f"\n✅ Configuration chargée avec succès!\n")
