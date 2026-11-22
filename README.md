# Wacdo – Gestion des affectations

Application web Django de gestion des affectations des collaborateurs dans les restaurants Wacdo : restaurants, collaborateurs, fonctions (postes) et affectations, avec un accès réservé aux administrateurs authentifiés.

## Stack technique

| Composant      | Version  | Rôle                                                  |
|----------------|----------|-------------------------------------------------------|
| Python         | 3.14     | Langage côté serveur                                  |
| Django         | 5.2 LTS  | Framework web (ORM, templates, authentification)      |
| MySQL          | 8.0      | Base de données relationnelle                         |
| mysqlclient    | 2.3.0    | Pilote MySQL recommandé par Django                    |
| python-dotenv  | 1.2.3    | Chargement des variables d'environnement depuis `.env` |

Django 5.2 est une version LTS (support étendu), compatible avec Python 3.10 à 3.14 et MySQL 8.0+.

## Installation

### 1. Cloner le projet et créer l'environnement virtuel

```powershell
git clone https://github.com/benjaminpillard/wacdo-affectations.git
cd wacdo-affectations
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Créer la base MySQL

```sql
CREATE DATABASE wacdo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wacdo_user'@'localhost' IDENTIFIED BY 'mot_de_passe';
GRANT ALL PRIVILEGES ON wacdo.* TO 'wacdo_user'@'localhost';
-- Nécessaire pour que les tests puissent créer la base test_wacdo :
GRANT ALL PRIVILEGES ON test_wacdo.* TO 'wacdo_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configurer les variables d'environnement

Copier `.env.example` en `.env` et renseigner les valeurs :

```powershell
copy .env.example .env
```

| Variable               | Description                                    | Défaut      |
|------------------------|------------------------------------------------|-------------|
| `DJANGO_SECRET_KEY`    | Clé secrète Django (obligatoire)               | —           |
| `DJANGO_DEBUG`         | `True` en développement, `False` en production | `False`     |
| `DJANGO_ALLOWED_HOSTS` | Hôtes autorisés, séparés par des virgules      | vide        |
| `DB_NAME`              | Nom de la base                                 | —           |
| `DB_USER`              | Utilisateur MySQL                              | —           |
| `DB_PASSWORD`          | Mot de passe MySQL                             | —           |
| `DB_HOST`              | Hôte MySQL                                     | `127.0.0.1` |
| `DB_PORT`              | Port MySQL                                     | `3306`      |

Le fichier `.env` est ignoré par git : aucun secret n'est versionné. Les paramètres sont lus dans `config/settings.py` via `os.environ` / `os.getenv`.

Générer une clé secrète :

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Initialiser la base et créer un administrateur

```powershell
python manage.py migrate
python manage.py createsuperuser
```

### 5. Lancer le serveur

```powershell
python manage.py runserver
```

L'application est accessible sur http://127.0.0.1:8000/ et l'interface d'administration Django sur http://127.0.0.1:8000/admin/.

## Architecture

```
wacdo-affectations/
├── config/              # Projet Django : settings, urls racine, wsgi/asgi
├── gestion/             # Application métier
│   ├── models.py        # Collaborateur, Restaurant, Fonction, Affectation
│   ├── forms.py         # Formulaires de saisie, de recherche et validation
│   ├── views.py         # Vues génériques (ListView, DetailView, CreateView…)
│   ├── mixins.py        # AdministrateurRequisMixin (contrôle d'accès)
│   ├── urls.py          # Routes de l'application
│   ├── admin.py         # Configuration de l'admin Django
│   ├── tests.py         # Tests fonctionnels, d'interface et de sécurité
│   ├── migrations/
│   └── templates/gestion/
├── .env.example         # Modèle de configuration
├── requirements.txt
└── manage.py
```

### Modèle de données

- **Collaborateur** : modèle utilisateur personnalisé (`AUTH_USER_MODEL`) héritant d'`AbstractUser`. Connexion par email, champs nom, prénom, date de première embauche et booléen `administrateur`.
- **Restaurant** : nom, adresse, code postal (5 chiffres), ville.
- **Fonction** : intitulé de poste (unique).
- **Affectation** : clés étrangères vers Collaborateur, Restaurant et Fonction, plus une date de début et une date de fin (vide = affectation en cours). Les suppressions sont protégées (`on_delete=PROTECT`) pour conserver l'historique.

### Sécurité

- Authentification via le système intégré de Django (`LoginView` / `LogoutView`).
- Toutes les vues de gestion utilisent `AdministrateurRequisMixin` : un visiteur non connecté est redirigé vers la page de connexion, un collaborateur non administrateur reçoit une erreur 403.
- Les mots de passe des administrateurs sont hachés avec PBKDF2-SHA256 (hacheur par défaut de Django) et contrôlés par les validateurs de mot de passe. Les collaborateurs standards ont un mot de passe inutilisable.
- Protection CSRF sur tous les formulaires ; les suppressions ne sont acceptées qu'en POST.

## Fonctionnalités

- **Restaurants** : liste avec recherche (nom, code postal, ville), création, modification, détail avec collaborateurs en poste (filtrables par poste et date de début), historique des affectations et affectation d'un nouveau collaborateur.
- **Collaborateurs** : liste avec recherche (nom, prénom, email), création, liste des collaborateurs non affectés, détail avec affectations en cours et historique, changement de poste.
- **Fonctions** : liste, création, modification.
- **Affectations** : recherche par poste, date de début, date de fin et ville.

## Tests

```powershell
python manage.py test gestion
```

Les tests couvrent :

- **Fonctionnels** : règles métier des affectations, création de restaurant et de collaborateur, changement de poste, collaborateurs non affectés, recherche.
- **Sécurité** : redirection des visiteurs non connectés, refus (403) pour les non-administrateurs, hachage des mots de passe.
- **Interface** : affichage des pages principales et des bons gabarits.

## Débogage

- `DJANGO_DEBUG=True` dans `.env` affiche les pages d'erreur détaillées de Django.
- `python manage.py check` vérifie la configuration du projet.
- `python manage.py showmigrations` affiche l'état des migrations.
- `python manage.py shell` permet d'interroger l'ORM directement.
- `python manage.py dbshell` ouvre un client MySQL sur la base configurée.
