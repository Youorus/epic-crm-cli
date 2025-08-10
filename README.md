# 📌 Epic CRM — Gestion Commerciale, Gestion & Support
<img width="1920" height="520" alt="16903799358611_P12-02" src="https://github.com/user-attachments/assets/ced47d15-1a82-44f0-8c58-386da8a03e34" />

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Django](https://img.shields.io/badge/django-5.0-success.svg)
![DRF](https://img.shields.io/badge/DRF-3.16-orange.svg)
![Tests](https://img.shields.io/badge/tests-pytest-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

---

## 🧭 Vue d’ensemble

**Epic CRM** est une application CRM modulaire (API REST + CLI) pour gérer :

* les **utilisateurs** (rôles : *GESTION*, *COMMERCIAL*, *SUPPORT*),
* les **clients** (création, mise à jour, suivi),
* les **contrats** (montants, statut signé, soldes),
* les **événements** (planification et affectation au support).

L’API est exposée via **Django REST Framework**, documentée par **drf‑spectacular** (Swagger/ReDoc) et sécurisée par **JWT** (SimpleJWT). Le dépôt inclut une **interface CLI** pour l’usage quotidien.

---

## ✨ Fonctionnalités

* 🔐 Authentification **JWT** (create / refresh / verify)
* 👥 **Rôles & permissions** métier (commercial, gestion, support)
* 🧾 **CRUD** Clients / Contrats / Événements
* 🔎 **Filtres** (django-filter) sur contrats & événements
* 📚 **Swagger** (+ ReDoc) généré automatiquement
* 🧪 **Tests** unitaires & API avec `pytest` + `pytest-django`
* 📈 **Couverture** de tests avec `coverage.py`
* 🧰 **CLI** ergonomique (menus par rôle)
* 🌱 **Seed** de données de démo (`seed.py`)

---

## 🗂️ Table des matières

* [Prérequis](#-prérequis)
* [Installation & Démarrage](#-installation--démarrage)
* [Configuration](#-configuration)
* [Démarrer le serveur](#-démarrer-le-serveur)
* [Authentification JWT](#-authentification-jwt)
* [Routes principales](#-routes-principales)
* [Utilisation de la CLI](#-utilisation-de-la-cli)
* [Données de démo (seed)](#-données-de-démo-seed)
* [Rôles & Permissions](#-rôles--permissions)
* [Tests & Couverture](#-tests--couverture)
* [Arborescence du projet](#-arborescence-du-projet)
* [Licence](#-licence)

---

## 🔧 Prérequis

* Python **3.12+**
* `pip` et `venv`
* (Optionnel) SQLite (par défaut) ou autre base configurée dans `settings.py`

---

## 🚀 Installation & Démarrage

### 1) Cloner et créer l’environnement virtuel

```bash
git clone https://github.com/Youorus/epic-crm-cli.git
cd epic-crm-cli

python3 -m venv .venv
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2) Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> 💡 Si vous ajoutez de nouvelles dépendances :
>
> ```bash
> pip freeze > requirements.txt
> ```

---

## ⚙️ Configuration

Vous pouvez utiliser des variables d’environnement (ou un fichier `.env` si vous utilisez `python-dotenv`) :

```env
DJANGO_SETTINGS_MODULE=epic_crm.settings
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Appliquez ensuite les migrations et créez un superutilisateur :

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## ▶️ Démarrer le serveur

```bash
python manage.py runserver
```

* API : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Admin : [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
* Swagger : [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
* ReDoc : [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
* Schéma JSON : [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

---

## 🔑 Authentification JWT

**Endpoints**

* `POST /api/auth/jwt/create/` — obtenir *access* & *refresh*
* `POST /api/auth/jwt/refresh/` — rafraîchir l’*access token*
* `POST /api/auth/jwt/verify/` — vérifier un token

**Exemple (curl)**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"username":"<user>", "password":"<pass>"}'
```

Utilisez ensuite l’en-tête HTTP :

```
Authorization: Bearer <access_token>
```

---

## 🧩 Routes principales

* `/api/users/` — CRUD utilisateurs (limité par rôle)
* `/api/clients/` — CRUD clients (restrictions par rôle)
* `/api/contracts/` — Contrats (filtres : `is_signed`, `amount_due__gt`, …)
* `/api/events/` — Événements (filtres : `support_contact`, `client`, `event_start__gte/lte`)

---

## 🧑‍💻 Utilisation de la CLI

Lancez l’interface CLI :

```bash
python -m cli.main
```

Puis naviguez via les menus selon votre rôle (Commercial / Gestion / Support). Les formulaires effectuent les appels à l’API et appliquent les validations.

---

## 🌱 Données de démo (seed)

> ⚠️ **Attention** : en configuration SQLite, le script peut réinitialiser la base.

```bash
python seed.py
```

Ce script crée :

* 3 utilisateurs (`commercial_1`, `support_1`, `gestion_1`),
* des clients & contrats (signés / non signés),
* des événements assignés au support.

---

## 🔐 Rôles & Permissions

| Rôle           |                               Clients |                          Contrats |                                                                 Événements |          Utilisateurs |
| -------------- | ------------------------------------: | --------------------------------: | -------------------------------------------------------------------------: | --------------------: |
| **GESTION**    |                                  CRUD |                              CRUD |                                                 CRUD (assignation support) |                  CRUD |
| **COMMERCIAL** | CRUD *sur ses clients* ; lecture tous | Lecture (contrats de ses clients) | Création uniquement pour **ses contrats signés** ; lecture (clients à lui) | Lecture de son profil |
| **SUPPORT**    |                               Lecture |                           Lecture |                       Lecture & **mise à jour de ses événements assignés** | Lecture de son profil |

> Les contrôles combinent **permissions DRF**, **get\_queryset()** et règles en `perform_create/perform_update`.

---

## 🧪 Tests & Couverture

**Lancer tous les tests**

```bash
pytest -q
```

**Mesurer la couverture**

```bash
coverage run -m pytest
coverage report -m
coverage html && open htmlcov/index.html  # macOS
```

Assurez‑vous que `pytest.ini` contient :

```ini
[pytest]
DJANGO_SETTINGS_MODULE = epic_crm.settings
python_files = tests.py test_*.py *_tests.py
testpaths = tests
addopts = -ra
markers =
    django_db: accès DB pour les tests (pytest-django)
```

---

## 🧱 Arborescence du projet

```text
epic-crm-cli/
├─ epic_crm/                  # Projet Django (settings/urls)
│  ├─ settings.py
│  └─ urls.py
├─ crm/
│  ├─ users/                  # Utilisateurs & rôles
│  ├─ clients/                # Clients
│  ├─ contracts/              # Contrats
│  └─ events/                 # Événements
├─ cli/                       # Interface CLI
│  ├─ menus/                  # Menus par rôle
│  ├─ forms/                  # Saisie et validations
│  └─ services/               # Appels API
├─ tests/                     # Tests unitaires & API
├─ seed.py                    # Données de démo
├─ requirements.txt
├─ pytest.ini
└─ README.md
```

---

## 📜 Licence

**MIT** — libre d’utilisation et de modification.
© Epic CRM
**Auteur :** Marc Takoumba
