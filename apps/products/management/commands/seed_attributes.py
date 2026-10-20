
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.products.models import Attribute, AttributeValue


ATTRIBUTE_DATA = {
    "Couleur": [
        "Noir", "Blanc", "Rouge", "Bleu", "Vert",
        "Jaune", "Orange", "Rose", "Violet", "Gris",
        "Marron", "Beige", "Multicolore",
    ],
    "Taille": [
        "XS", "S", "M", "L", "XL", "XXL", "XXXL",
    ],
    "Pointure": [
        "36", "37", "38", "39", "40", "41",
        "42", "43", "44", "45", "46",
    ],
    "Matière": [
        "Coton", "Polyester", "Cuir", "Jean",
        "Laine", "Lin", "Plastique", "Métal",
        "Bois", "Verre", "Silicone",
    ],
    "Capacité": [
        "250 ml", "500 ml", "750 ml", "1 L",
        "1,5 L", "2 L", "5 L", "10 L",
    ],
    "Poids": [
        "100 g", "250 g", "500 g", "1 kg",
        "2 kg", "5 kg", "10 kg", "25 kg",
    ],
    "Format": [
        "Petit", "Moyen", "Grand", "Très grand",
    ],
    "Saveur": [
        "Nature", "Chocolat", "Vanille", "Fraise",
        "Citron", "Mangue", "Orange", "Caramel",
    ],
    "Parfum": [
        "Floral", "Boisé", "Fruité", "Oriental",
        "Frais", "Vanillé",
    ],
    "Puissance": [
        "5 W", "10 W", "20 W", "30 W",
        "50 W", "100 W", "500 W", "1000 W",
    ],
    "Tension": [
        "5 V", "12 V", "24 V", "110 V", "220 V",
    ],
    "Stockage": [
        "32 Go", "64 Go", "128 Go", "256 Go",
        "512 Go", "1 To", "2 To",
    ],
    "Connectivité": [
        "USB", "USB-C", "Bluetooth", "Wi-Fi",
        "Ethernet", "HDMI",
    ],
    "Compatibilité": [
        "Android", "iOS", "Windows", "macOS",
        "Universel",
    ],
    "Condition": [
        "Neuf", "Reconditionné", "Occasion",
    ],
}


class Command(BaseCommand):
    help = (
        "Crée les attributs et leurs valeurs de démonstration "
        "sans générer de doublons."
    )

    def handle(self, *args, **options):
        created_attributes = 0
        created_values = 0

        with transaction.atomic():
            for name, values in ATTRIBUTE_DATA.items():
                attribute, attribute_created = (
                    Attribute.objects.get_or_create(
                        name=name,
                        defaults={"slug": slugify(name)},
                    )
                )

                if attribute_created:
                    created_attributes += 1

                # Évite de créer deux fois la même valeur
                # pour un même attribut.
                value_objects = [
                    AttributeValue(
                        attribute=attribute,
                        value=value,
                    )
                    for value in values
                ]

                created = AttributeValue.objects.bulk_create(
                    value_objects,
                    ignore_conflicts=True,
                    batch_size=500,
                )

                created_values += len(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed terminé : {created_attributes} attribut(s) "
                f"créé(s) et {created_values} valeur(s) créée(s)."
            )
        )