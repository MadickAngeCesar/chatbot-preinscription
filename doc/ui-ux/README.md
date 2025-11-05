# 🎨 Documentation UI/UX - Chatbot de Préinscription

## 📋 Vue d'ensemble

Cette documentation présente le design system et les maquettes d'interface pour le projet Chatbot de Préinscription Universitaire.

## 🎨 Design System

### Palette de couleurs

#### Couleurs primaires
- **Primary**: `#6366F1` (Indigo)
- **Primary Dark**: `#4F46E5`
- **Primary Light**: `#818CF8`
- **Primary Lighter**: `#C7D2FE`
- **Primary Lightest**: `#E0E7FF`

#### Couleurs secondaires
- **Secondary**: `#10B981` (Green)
- **Secondary Dark**: `#059669`
- **Secondary Light**: `#34D399`

#### Couleurs d'accentuation
- **Accent**: `#F59E0B` (Amber)
- **Accent Dark**: `#D97706`

#### Couleurs neutres
- **Gray 50-900**: Échelle de gris complète
- **Background Primary**: `#FFFFFF`
- **Background Secondary**: `#F9FAFB`

#### Couleurs de statut
- **Success**: `#10B981`
- **Warning**: `#F59E0B`
- **Error**: `#EF4444`
- **Info**: `#3B82F6`

### Typographie

**Police principale**: Inter (Google Fonts)
- Weights: 300, 400, 500, 600, 700, 800

**Échelle typographique**:
- XS: 0.75rem (12px)
- SM: 0.875rem (14px)
- Base: 1rem (16px)
- LG: 1.125rem (18px)
- XL: 1.25rem (20px)
- 2XL: 1.5rem (24px)
- 3XL: 1.875rem (30px)
- 4XL: 2.25rem (36px)
- 5XL: 3rem (48px)

### Espacement

Système d'espacement basé sur des multiples de 0.25rem (4px):
- XS: 0.25rem (4px)
- SM: 0.5rem (8px)
- MD: 1rem (16px)
- LG: 1.5rem (24px)
- XL: 2rem (32px)
- 2XL: 3rem (48px)

### Bordures et ombres

**Border Radius**:
- SM: 0.375rem
- Base: 0.5rem
- LG: 0.75rem
- XL: 1rem
- 2XL: 1.5rem
- Full: 9999px

**Box Shadows**:
- SM: `0 1px 2px 0 rgba(0, 0, 0, 0.05)`
- Base: `0 1px 3px 0 rgba(0, 0, 0, 0.1)`
- MD: `0 4px 6px -1px rgba(0, 0, 0, 0.1)`
- LG: `0 10px 15px -3px rgba(0, 0, 0, 0.1)`
- XL: `0 20px 25px -5px rgba(0, 0, 0, 0.1)`
- 2XL: `0 25px 50px -12px rgba(0, 0, 0, 0.25)`

## 📱 Maquettes d'interface

### 1. Landing Page (landing-page.svg)
Page d'accueil avec:
- Navigation responsive avec logo et liens
- Section Hero avec titre accrocheur et CTA
- Statistiques (2.5k+ étudiants, 95% satisfaction, 24/7 disponibilité)
- Aperçu du chatbot en action
- Section fonctionnalités (6 cartes)
- CTA final

**Breakpoints**:
- Desktop: 1440px
- Tablet: 768px
- Mobile: 375px

### 2. Interface Chat Desktop (chatbot-desktop.svg)
Application de chat complète avec:
- **Sidebar gauche** (280px):
  - Logo et branding
  - Bouton "Nouvelle conversation"
  - Historique des conversations
  - Liens rapides (Formulaire, Accueil)
  - Profil utilisateur

- **Zone principale**:
  - Header avec avatar du bot et statut
  - Zone de messages avec scroll
  - Message de bienvenue avec quick actions
  - Barre d'input avec icônes et compteur de caractères

**Dimensions**: 1440x900px

### 3. Formulaire de Préinscription (form-desktop.svg)
Formulaire multi-étapes avec:
- **Header**:
  - Icône du formulaire
  - Titre et description
  - Barre de progression avec 4 étapes
  - Indicateur de progression visuel

- **Étapes**:
  1. **Informations personnelles**: Nom, prénom, email, téléphone, date/lieu de naissance, adresse
  2. **Choix du programme**: Cartes de programmes, niveau d'études, motivation
  3. **Documents**: Upload de photo, diplôme, relevé de notes, CV
  4. **Confirmation**: Récapitulatif et acceptation des CGU

- **Navigation**: Boutons Précédent/Suivant/Soumettre

**Dimensions**: 1440x1200px

### 4. Chat Mobile (mobile-chat.svg)
Version mobile optimisée:
- Header compact avec back button
- Messages adaptés à la petite taille
- Quick actions en cards verticales
- Input en bas avec icons
- Optimisé pour thumb zone

**Dimensions**: 375x812px (iPhone X/11/12)

## 🎯 Principes de Design

### 1. Hiérarchie visuelle
- Utilisation de tailles de police et de poids variés
- Espacement généreux entre les sections
- Contraste de couleurs pour attirer l'attention

### 2. Accessibilité
- Ratios de contraste WCAG AA minimum
- Tailles de texte lisibles (min 14px)
- Zones de clic suffisantes (min 44x44px sur mobile)
- Labels clairs et descriptifs

### 3. Responsive Design
- Mobile-first approach
- Breakpoints cohérents
- Touch-friendly sur mobile
- Grilles flexibles

### 4. Feedback utilisateur
- États hover/focus/active
- Animations subtiles et fluides
- Messages de confirmation
- Indicateurs de chargement
- Toasts notifications

### 5. Cohérence
- Composants réutilisables
- Spacing system uniforme
- Palette de couleurs limitée
- Typographie cohérente

## 🚀 Composants UI

### Boutons
- **Primary**: Gradient indigo, texte blanc
- **Secondary**: Fond gris, bordure
- **Outline**: Transparent avec bordure colorée
- **Success**: Gradient vert

### Cards
- Border radius: 12-16px
- Shadow: Subtile avec hover elevation
- Padding: 24px
- Border: 1px gris clair

### Inputs
- Height: 48px
- Border: 2px gris
- Focus: Border bleue + shadow
- Icon position: Gauche (padding-left)

### Messages (Chat)
- Bot: Fond gris clair, aligné à gauche
- User: Fond bleu gradient, aligné à droite
- Avatar: 40px cercle
- Border radius: 12px
- Max width: 70%

### Modals
- Backdrop: Noir 50% opacité
- Content: Blanc, border radius 24px
- Animation: Fade in + scale
- Max width: 500px

### Toasts
- Position: Top right
- Animation: Slide in from right
- Auto-dismiss: 3 secondes
- Types: Success, Error, Warning, Info

## 📐 Grilles et Layout

### Desktop
- Container max-width: 1280px
- Sidebar: 280px fixe
- Content: Flex 1
- Padding horizontal: 24px

### Tablet (768px-1024px)
- Container: Full width avec padding
- Sidebar: Coulissante (overlay)
- Grilles: 2 colonnes

### Mobile (<768px)
- Container: Full width
- Sidebar: Menu hamburger
- Grilles: 1 colonne
- Padding: 16px

## 🎭 Animations

### Transitions
- Fast: 150ms
- Base: 200ms
- Slow: 300ms
- Easing: ease ou ease-in-out

### Keyframes
- fadeInUp: Opacity 0→1 + translateY 30px→0
- slideIn: translateX 100%→0
- float: translateY avec scale (boucle infinie)
- pulse: Opacity et scale (boucle infinie)
- spin: Rotation 360° (loading)

## 📊 États des composants

### Boutons
- Default: Couleur de base
- Hover: translateY(-2px) + shadow elevation
- Active: Scale légèrement
- Disabled: Opacity 50%, cursor not-allowed

### Inputs
- Default: Border gris
- Focus: Border bleue + shadow bleue
- Error: Border rouge + message
- Disabled: Background gris clair

### Cards
- Default: Shadow subtile
- Hover: translateY(-8px) + shadow forte

## 🎨 Icônes

Utilisation de **Font Awesome 6** pour toutes les icônes:
- Graduation cap: Logo université
- Robot: Avatar chatbot
- User: Profil utilisateur
- Paper plane: Envoyer message
- File: Documents
- Check circle: Succès
- Exclamation: Erreurs/warnings
- Et plus...

## 📝 Notes d'implémentation

### CSS
- Variables CSS pour tous les tokens
- Classes utilitaires
- BEM naming convention
- Mobile-first media queries

### JavaScript
- Vanilla JS (pas de framework requis)
- Event delegation
- Local storage pour historique
- Fetch API pour communications serveur

### Assets
- SVG pour icônes et illustrations
- WebP pour images (avec fallback)
- Lazy loading pour images
- Compression optimale

## 🔗 Ressources

- **Fonts**: [Google Fonts - Inter](https://fonts.google.com/specimen/Inter)
- **Icons**: [Font Awesome](https://fontawesome.com/)
- **Color Tool**: [Coolors](https://coolors.co/)
- **Contrast Checker**: [WebAIM](https://webaim.org/resources/contrastchecker/)

---

**Designer**: Madick Ange César  
**Date**: Novembre 2025  
**Version**: 1.0
