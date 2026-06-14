# Restaurant Manager — Easy POS

Système de gestion de restaurant complet développé avec Django. Il couvre la caisse enregistreuse (POS), la gestion des commandes, le suivi cuisine (KDS), les stocks, les ressources humaines, la paie, les finances et les réservations en ligne.

---

## Fonctionnalites

**Caisse POS**
- Prise de commande rapide avec catalogue produits visuel
- Support Sur place, A emporter, Livraison
- Impression de ticket de caisse
- Gestion des clients et modes de paiement

**Ecran Cuisine (KDS)**
- Affichage des tickets en temps reel (Kanban : En attente / En cours / Prete)
- Validation des plats par le cuisinier
- Generation automatique d'une facture lors du passage en statut "Prete"

**Gestion des stocks**
- Suivi des ingredients et niveaux de stock
- Alertes de stock bas
- Historique des variations

**Ressources Humaines**
- Fiche employe avec photo
- Affectation aux postes
- Supervision hierarchique
- Creation de comptes utilisateurs avec role pre-configure

**Finances**
- Liste des factures generees automatiquement
- Suivi du chiffre d'affaires

**Reservations en ligne**
- Page publique de reservation et commande client
- Acces direct sans compte requis pour les clients

**Controle d'acces par roles (RBAC)**
- Roles pre-definis : Administrateur, Directeur, Chef cuisinier, Cuisinier, Serveur, Gestionnaire de stock
- Chaque role donne acces uniquement aux modules qui le concernent
- Cree et gere depuis l'interface d'administration Django

---

## Stack technique

| Composant    | Technologie              |
|--------------|--------------------------|
| Backend      | Django 5.2               |
| Base de donnees | SQLite (dev) / MySQL (prod) |
| Frontend     | HTML / CSS Vanilla / JavaScript |
| Authentification | Django Auth + groupes de permissions |
| Images       | Pillow                   |
| Variables d'environnement | python-dotenv |

---

## Prerequis

- Python 3.10 ou superieur
- pip
- Git

---

## Installation

### 1. Cloner le depot

```bash
git clone https://github.com/votre-utilisateur/Restaurant-manager.git
cd Restaurant-manager
```

### 2. Creer et activer un environnement virtuel

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dependances

```bash
pip install -r requirements.txt
```

### 4. Configurer l'environnement

Copier le fichier exemple et le renseigner :

```bash
copy .env.example .env
```

Editer `.env` avec vos valeurs :

```env
DJANGO_SECRET_KEY=votre-cle-secrete-ici
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Base de donnees (SQLite par defaut, laisser vide)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

> Pour utiliser MySQL en production, renseigner `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Initialiser les roles et permissions

Cette commande cree les 6 groupes pre-definis avec leurs permissions associees :

```bash
python manage.py setup_roles
```

### 7. Creer un compte administrateur

```bash
python manage.py createsuperuser
```

Suivre les instructions pour definir un nom d'utilisateur et un mot de passe.

### 8. Lancer le serveur de developpement

```bash
python manage.py runserver
```

L'application est accessible a l'adresse : `http://127.0.0.1:8000/`

---

## Acces et navigation

| URL | Description | Acces |
|-----|-------------|-------|
| `/` | Page d'accueil publique et reservation en ligne | Public |
| `/login/` | Page de connexion | Public |
| `/pos/` | Caisse enregistreuse | Serveur, Admin |
| `/cuisine/` | Ecran cuisine (KDS) | Cuisinier, Chef cuisinier |
| `/commandes/` | Liste des commandes | Serveur et +  |
| `/produits/` | Gestion du catalogue | Manager et + |
| `/stock/` | Gestion des stocks | Gestionnaire de stock, Admin |
| `/rh/` | Ressources humaines | Directeur, Admin |
| `/finances/` | Suivi financier | Directeur, Admin |
| `/admin/` | Administration Django | Superutilisateur |

---

## Roles et permissions

Les roles sont configures via `python manage.py setup_roles`. L'administrateur les assigne ensuite aux comptes depuis `/rh/`.

| Role | Acces |
|------|-------|
| Administrateur | Acces complet a tous les modules |
| Directeur | Lecture de tous les modules, RH, Finances |
| Chef cuisinier | Ecran cuisine, Catalogue, Stock |
| Cuisinier | Ecran cuisine, Catalogue |
| Serveur | Caisse POS, Catalogue |
| Gestionnaire de stock | Stock, Operations |

---

## Structure du projet

```
Restaurant-manager/
├── manage.py
├── requirements.txt
├── .env.example
├── restaurant_manager/       # Configuration Django (settings, urls)
├── restaurant/
│   ├── models.py             # Modeles de donnees
│   ├── views.py              # Logique metier et vues
│   ├── urls.py               # Routes URL
│   ├── templates/restaurant/ # Templates HTML
│   ├── static/restaurant/    # CSS, JS, images statiques
│   └── management/commands/
│       └── setup_roles.py    # Commande d'initialisation des roles
├── media/                    # Fichiers uploadés (images produits, employes)
└── docs/
    └── cahier-des-charges.md
```

---

## Remise en production

Pour un deploiement en production, il est recommande de :

1. Passer `DJANGO_DEBUG=False` dans `.env`
2. Utiliser une base de donnees MySQL ou PostgreSQL
3. Configurer un serveur WSGI (Gunicorn) derriere un reverse proxy (Nginx)
4. Executer `python manage.py collectstatic` pour les fichiers statiques
5. Configurer `ALLOWED_HOSTS` avec le domaine reel

---

## Licence

Projet developpe dans le cadre d'un systeme de gestion de restaurant. Tous droits reserves.
