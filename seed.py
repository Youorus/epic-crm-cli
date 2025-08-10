# seed.py
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

# --- Config seeds ---
USER_DATA = [
    {"username": "commercial_1", "email": "alice.dupont@example.com", "role": "COMMERCIAL"},
    {"username": "support_1", "email": "bob.moreau@example.com", "role": "SUPPORT"},
    {"username": "gestion_1", "email": "claire.bernard@example.com", "role": "GESTION"},
]
PASSWORD = "Azerty123$"
APPS = ["users", "clients", "contracts", "events"]

CLIENT_NAMES = [
    ("Jean Martin", "Société Alpha"),
    ("Sophie Durand", "Durand Consulting"),
    ("Karim Boulahya", "TechWave"),
    ("Emma Lefèvre", "Lefèvre & Fils"),
    ("Lucas Petit", "Petit Design"),
    ("Nora Benali", "Benali Co."),
    ("Antoine Girard", "Girard Architecture"),
    ("Lina Fontaine", "Fontaine Luxe"),
]

EVENT_LOCATIONS = [
    "Salle Eiffel - Paris", "Hôtel de Ville - Lyon", "Centre Expo - Marseille",
    "Palais des Congrès - Lille", "Espace Atlantique - Nantes", "Salle Horizon - Toulouse",
    "Château de Versailles", "Villa Méditerranée - Marseille"
]

def _sqlite_path():
    db = settings.DATABASES.get("default", {})
    if db.get("ENGINE") == "django.db.backends.sqlite3":
        return str(db.get("NAME"))
    return None

def _clean_migrations():
    print("🗑 Suppression des anciennes migrations...")
    base = settings.BASE_DIR
    for app in APPS:
        migrations_path = os.path.join(base, "crm", app, "migrations")
        os.makedirs(migrations_path, exist_ok=True)
        for entry in os.listdir(migrations_path):
            path = os.path.join(migrations_path, entry)
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

    _reset_db_if_sqlite()
    _clean_migrations()

    print("📦 Recréation des migrations et application...")
    call_command("makemigrations", *APPS, verbosity=1)
    call_command("migrate", verbosity=1)
    print("✅ Migrations terminées.\n")

    # Utilisateurs
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

    # Clients
    print("🏢 Création des clients :")
    clients = []
    for full_name, company in random.sample(CLIENT_NAMES, 5):
        client = Client.objects.create(
            full_name=full_name,
            email=f"{full_name.lower().replace(' ', '.')}@exemple.com",
            phone=f"0{random.randint(6,7)}{random.randint(10000000, 99999999)}",
            company_name=company,
            last_contact=timezone.now().date() - timedelta(days=random.randint(1, 60)),
            sales_contact=commercial,
        )
        clients.append(client)
        print(f"   ➡ {client.full_name} ({client.email})")
    print()

    # Contrats
    print("📄 Création des contrats :")
    contracts = []
    for client in clients:
        total_amount = round(random.uniform(1200, 8000), 2)
        amount_due = round(random.uniform(0, total_amount), 2)
        contract = Contract.objects.create(
            client=client,
            sales_contact=commercial,
            total_amount=total_amount,
            amount_due=amount_due,
            is_signed=random.choice([True, False]),
        )
        contracts.append(contract)
        print(f"   ➡ Contrat {contract.id} - Client : {client.full_name} | "
              f"Montant : {total_amount}€ | Signé : {contract.is_signed}")
    print()

    # Événements
    print("📅 Création des événements :")
    for contract in contracts:
        if contract.is_signed:
            event = Event.objects.create(
                contract=contract,
                client=contract.client,
                support_contact=support,
                event_name=random.choice([
                    "Formation produit", "Conférence annuelle", "Atelier découverte",
                    "Séminaire stratégique", "Présentation client", "Atelier technique"
                ]) + f" - {contract.client.company_name}",
                event_start=timezone.now() + timedelta(days=random.randint(2, 15)),
                event_end=timezone.now() + timedelta(days=random.randint(16, 30)),
                location=random.choice(EVENT_LOCATIONS),
                attendees=random.randint(5, 150),
                notes=random.choice([
                    "Prévoir café et viennoiseries.",
                    "Matériel audio/vidéo requis.",
                    "Invitations envoyées.",
                    "Salle confirmée.",
                    "En attente de confirmation du client."
                ]),
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