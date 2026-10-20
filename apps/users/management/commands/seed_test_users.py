
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


TEST_USERS = [
    {
        "username": "admin.test",
        "email": "admin.test@example.com",
        "password": "AdminTest2026!",
        "role_keyword": "admin",
        "is_staff": True,
        "is_superuser": True,
        "permission_ids": [21, 24, 8, 22, 29, 32, 44, 41, 42, 37, 40, 9, 12, 10],
        "group_ids": [2, 3],
    },
    {
        "username": "manager.test",
        "email": "manager.test@example.com",
        "password": "ManagerTest2026!",
        "role_keyword": "manager",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "username": "worker.test",
        "email": "worker.test@example.com",
        "password": "WorkerTest2026!",
        "role_keyword": "foot worker",
        "is_staff": False,
        "is_superuser": False,
    },
]


class Command(BaseCommand):
    help = "Crée ou met à jour les comptes utilisateurs de test."

    def find_role(self, User, keyword):
        choices = User._meta.get_field("role").choices

        for value, label in choices:
            if keyword in str(value).lower() or keyword in str(label).lower():
                return value

        available_roles = ", ".join(
            f"{value} ({label})" for value, label in choices
        )
        raise CommandError(
            f"Rôle '{keyword}' introuvable. "
            f"Rôles disponibles : {available_roles}"
        )

    def handle(self, *args, **options):
        User = get_user_model()

        with transaction.atomic():
            for data in TEST_USERS:
                role = self.find_role(User, data["role_keyword"])

                user, created = User.objects.get_or_create(
                    email=data["email"],
                    defaults={
                        "username": data["username"],
                        "role": role,
                    },
                )

                user.username = data["username"]
                user.role = role
                user.is_active = True
                user.is_staff = data["is_staff"]
                user.is_superuser = data["is_superuser"]
                user.set_password(data["password"])
                user.save()

                action = "créé" if created else "mis à jour"

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Utilisateur {action} : {user.email}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Les comptes de test ont été préparés avec succès."
            )
        )