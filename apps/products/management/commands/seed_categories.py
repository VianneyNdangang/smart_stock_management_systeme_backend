
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.categories.models import Category


TAXONOMY_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "google_product_taxonomy.txt"
)

SEPARATOR = " > "


class Command(BaseCommand):
    help = "Importe la taxonomie e-commerce Google dans les catégories Django."

    def handle(self, *args, **options):
        if not TAXONOMY_FILE.exists():
            raise CommandError(
                f"Fichier de taxonomie introuvable : {TAXONOMY_FILE}"
            )

        created_count = 0
        existing_count = 0
        categories_by_path = {}

        with TAXONOMY_FILE.open("r", encoding="utf-8-sig") as file:
            lines = [
                line.strip()
                for line in file
                if line.strip() and not line.startswith("#")
            ]

        with transaction.atomic():
            for line in lines:
                try:
                    _, full_path = line.split(" - ", 1)
                except ValueError:
                    self.stderr.write(
                        self.style.WARNING(f"Ligne ignorée : {line}")
                    )
                    continue

                parent = None
                current_path = []

                for name in full_path.split(SEPARATOR):
                    current_path.append(name)
                    path_key = SEPARATOR.join(current_path)

                    if path_key in categories_by_path:
                        parent = categories_by_path[path_key]
                        continue

                    # Un slug basé sur le chemin complet distingue
                    # les catégories homonymes de branches différentes.
                    category_slug = slugify(path_key)

                    category, created = Category.objects.get_or_create(
                        slug=category_slug,
                        defaults={
                            "name": name,
                            "parent": parent,
                        },
                    )

                    categories_by_path[path_key] = category
                    parent = category

                    if created:
                        created_count += 1
                    else:
                        existing_count += 1

        total = Category.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Import terminé : {created_count} catégorie(s) créée(s), "
                f"{existing_count} déjà existante(s). "
                f"Total en base : {total}."
            )
        )