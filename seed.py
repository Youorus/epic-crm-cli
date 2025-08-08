# seed.py (à la racine du projet)
import os
import sys
import random
import django
from datetime import timedelta

# --- Initialisation Django ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epic_crm.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone

from crm.clients.models import Client
from crm.contracts.models import Contract
from crm.events.models import Event

# --- Config seed ---
USER_DATA = [
    {"username": "commercial_1", "email": "commercial@example.com", "role": "COMMERCIAL"},
    {"username": "support_1", "email": "support@example.com", "role": "SUPPORT"},
    {"username": "gestion_1", "email": "gestion@example.com", "role": "GESTION"},
]
PASSWORD = "Azerty123$"
APPS = ["users", "clients", "contracts", "events"]


def _sqlite_path():
    db = settings.DATABASES.get("default", {})
    if db.get("ENGINE") == "django.db.backends.sqlite3":
        name = db.get("NAME")
        # NAME peut être un Path; on convertit en str
        return str(name)
    return None


def _clean_migrations():
    print("🗑 Suppression des anciennes migrations...")
    base = settings.BASE_DIR
    for app in APPS:
        migrations_path = os.path.join(base, "crm", app, "migrations")
        os.makedirs(migrations_path, exist_ok=True)
        for entry in os.listdir(migrations_path):
            path = os.path.join(migrations_path, entry)
            # Ne supprime QUE les fichiers, jamais les dossiers (__pycache__)
            if os.path.isfile(path) and entry != "__init__.py":
                os.remove(path)
        print(f"   ➡ Migrations nettoyées pour {app}")


def _reset_db_if_sqlite():
    db_path = _sqlite_path()
    if db_path and os.path.exists(db_path):
        print(f"🗑 Suppression de la base SQLite : {db_path}")
        os.remove(db_path)


def run_seed():
    print("\n🚀 Lancement du SEED...\n")

    # 1) Reset DB si SQLite
    _reset_db_if_sqlite()

    # 2) Nettoyage des migrations
    _clean_migrations()

    # 3) Recréation des migrations + migrate
    print("📦 Recréation des migrations et application...")
    call_command("makemigrations", *APPS, verbosity=1)
    call_command("migrate", verbosity=1)
    print("✅ Migrations terminées.\n")

    # 4) Création des utilisateurs
    User = get_user_model()
    print("👤 Création des utilisateurs :")
    users = []
    for data in USER_DATA:
        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=PASSWORD,
            role=data["role"],
        )
        users.append(user)
        print(f"   ➡ {user.username} ({user.role})")
    print(f"🔑 Mot de passe commun : {PASSWORD}\n")

    commercial = next(u for u in users if u.role == "COMMERCIAL")
    support = next(u for u in users if u.role == "SUPPORT")
    gestion = next(u for u in users if u.role == "GESTION")

    # 5) Création des clients
    print("🏢 Création des clients :")
    clients = []
    for i in range(5):
        client = Client.objects.create(
            full_name=f"Client Test {i+1}",
            email=f"client{i+1}@fake.com",
            phone=f"06{random.randint(10000000, 99999999)}",
            company_name=f"Entreprise {i+1}",
            last_contact=timezone.now().date() - timedelta(days=random.randint(1, 30)),
            sales_contact=commercial,
        )
        clients.append(client)
        print(f"   ➡ {client.full_name} ({client.email})")
    print()

    # 6) Création des contrats
    print("📄 Création des contrats :")
    contracts = []
    for client in clients:
        contract = Contract.objects.create(
            client=client,
            sales_contact=gestion,
            total_amount=round(random.uniform(1000, 5000), 2),
            amount_due=round(random.uniform(0, 2500), 2),
            is_signed=random.choice([True, False]),
        )
        contracts.append(contract)
        print(f"   ➡ Contrat {contract.id} - Client : {client.full_name} | Signé : {contract.is_signed}")
    print()

    # 7) Création des événements pour les contrats signés (TZ aware)
    print("📅 Création des événements :")
    for contract in contracts:
        if contract.is_signed:
            event = Event.objects.create(
                contract=contract,
                client=contract.client,
                support_contact=support,
                event_name=f"Événement pour {contract.client.full_name}",
                event_start=timezone.now() + timedelta(days=random.randint(1, 10)),
                event_end=timezone.now() + timedelta(days=random.randint(11, 20)),
                location=f"Salle {random.randint(1, 10)} - Paris",
                attendees=random.randint(10, 100),
                notes="Créé via seed",
            )
            print(f"   ➡ {event.event_name} ({event.location})")
    print()

    print("🎯 SEED TERMINÉ AVEC SUCCÈS ✅")
    print(f"👥 Usernames : {[u['username'] for u in USER_DATA]}")


if __name__ == "__main__":
    try:
        run_seed()
    except Exception as e:
        print("❌ Erreur pendant le seed :", e)
        sys.exit(1)