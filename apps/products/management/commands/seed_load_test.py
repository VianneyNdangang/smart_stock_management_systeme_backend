
import random
import uuid
from decimal import Decimal
from itertools import product as cartesian_product

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.products.models import (
    Product,
    Variant,
    Attribute,
    AttributeValue,
    VariantAttributeValue,
    CategoryProduct,
)
from apps.inventory.models import Stock, Warehouse


# Données synthétiques de démonstration.
# Chaque famille définit les attributs autorisés et leurs valeurs.
FAMILIES = {
    "clothing": {
        "names": [
            "T-shirt Nike", "T-shirt Adidas", "Polo classique",
            "Chemise homme", "Jean slim", "Sweat à capuche",
        ],
        "attributes": {
            "Couleur": ["Noir", "Blanc", "Rouge", "Bleu"],
            "Taille": ["S", "M", "L", "XL"],
            "Matière": ["Coton", "Polyester"],
        },
        "price": (3500, 25000),
        "perishable": False,
        "category_keywords": [
            "clothing", "apparel", "vêtement", "shirt", "pantalon",
            "fashion", "jean", "chemise",
        ],
    },
    "shoes": {
        "names": [
            "Chaussures de sport Nike", "Chaussures Adidas",
            "Chaussures de ville", "Sandales confort",
        ],
        "attributes": {
            "Couleur": ["Noir", "Blanc", "Rouge", "Bleu"],
            "Pointure": ["38", "39", "40", "41", "42", "43", "44"],
            "Matière": ["Cuir", "Textile", "Synthétique"],
        },
        "price": (8000, 65000),
        "perishable": False,
        "category_keywords": [
            "shoe", "footwear", "chaussure", "sandale", "boot",
        ],
    },
    "smartphones": {
        "names": [
            "Samsung Galaxy", "Apple iPhone", "Xiaomi Redmi",
            "Tecno Spark", "Infinix Note",
        ],
        "attributes": {
            "Couleur": ["Noir", "Argent", "Bleu", "Vert"],
            "Stockage": ["64 Go", "128 Go", "256 Go", "512 Go"],
        },
        "price": (65000, 950000),
        "perishable": False,
        "category_keywords": [
            "smartphone", "mobile phone", "cell phone", "téléphone",
        ],
    },
    "computers": {
        "names": [
            "Ordinateur portable HP", "Lenovo ThinkPad",
            "Dell Latitude", "Asus VivoBook",
        ],
        "attributes": {
            "Couleur": ["Noir", "Argent", "Gris"],
            "Stockage": ["256 Go SSD", "512 Go SSD", "1 To SSD"],
        },
        "price": (180000, 850000),
        "perishable": False,
        "category_keywords": [
            "laptop", "computer", "ordinateur", "notebook",
        ],
    },
    "food": {
        "names": [
            "Jus de fruits", "Riz parfumé", "Farine de blé",
            "Sucre en poudre", "Biscuits emballés",
        ],
        "attributes": {
            "Saveur": ["Nature", "Orange", "Pomme", "Ananas"],
            "Capacité": ["250 ml", "500 ml", "1 L", "5 kg"],
        },
        "price": (500, 15000),
        "perishable": True,
        "category_keywords": [
            "food", "beverage", "grocery", "juice", "rice",
            "aliment", "boisson", "jus", "riz", "farine",
        ],
    },
    "appliances": {
        "names": [
            "Mixeur électrique", "Ventilateur électrique",
            "Bouilloire électrique", "Fer à repasser",
        ],
        "attributes": {
            "Couleur": ["Noir", "Blanc", "Gris"],
            "Puissance": ["500 W", "1000 W", "1500 W", "2000 W"],
        },
        "price": (12000, 125000),
        "perishable": False,
        "category_keywords": [
            "appliance", "electronic", "électroménager",
            "ventilateur", "mixeur", "kettle",
        ],
    },
    "furniture": {
        "names": [
            "Chaise de bureau", "Table de travail",
            "Étagère de rangement", "Fauteuil classique",
        ],
        "attributes": {
            "Couleur": ["Noir", "Blanc", "Marron"],
            "Matière": ["Bois", "Métal", "Plastique"],
        },
        "price": (10000, 180000),
        "perishable": False,
        "category_keywords": [
            "furniture", "chair", "table", "desk", "meuble", "chaise",
        ],
    },
    "cleaning": {
        "names": [
            "Détergent liquide", "Savon de ménage",
            "Liquide vaisselle", "Nettoyant multi-usage",
        ],
        "attributes": {
            "Format": ["500 ml", "1 L", "2 L", "5 L"],
            "Parfum": ["Citron", "Lavande", "Floral", "Nature"],
        },
        "price": (700, 18000),
        "perishable": False,
        "category_keywords": [
            "cleaning", "detergent", "household", "détergent",
            "entretien", "ménage", "soap",
        ],
    },
}


# Images de démonstration. Les URLs sont des exemples de photos Unsplash.
IMAGE_URLS = [
    "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
    "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab",
    "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
]


def model_has_field(model, field_name):
    """Vérifie qu'un champ existe réellement sur un modèle."""
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


def find_category(family_key, categories):
    """
    Cherche une catégorie pertinente à partir de son nom.
    Ne force pas une catégorie sans rapport avec le produit.
    """
    keywords = FAMILIES[family_key]["category_keywords"]

    matches = [
        category
        for category in categories
        if any(
            keyword in category.name.casefold()
            for keyword in keywords
        )
    ]

    return random.choice(matches) if matches else None


class Command(BaseCommand):
    help = (
        "Génère des produits de démonstration avec variantes, "
        "attributs relationnels et stocks."
    )

    def add_arguments(self, parser):
        parser.add_argument("--products", type=int, default=1000)
        parser.add_argument("--variants-per-product", type=int, default=5)
        parser.add_argument("--batch-size", type=int, default=200)
        parser.add_argument("--seed", type=int, default=42)

    def handle(self, *args, **options):
        product_count = options["products"]
        variants_per_product = options["variants_per_product"]
        batch_size = options["batch_size"]

        if product_count < 1:
            raise CommandError("--products doit être supérieur à zéro.")

        if variants_per_product < 1:
            raise CommandError(
                "--variants-per-product doit être supérieur à zéro."
            )

        if batch_size < 1:
            raise CommandError("--batch-size doit être supérieur à zéro.")

        random.seed(options["seed"])

        warehouses = list(
            Warehouse.objects.filter(is_active=True)
            if model_has_field(Warehouse, "is_active")
            else Warehouse.objects.all()
        )

        if not warehouses:
            raise CommandError(
                "Aucun entrepôt disponible. Crée un entrepôt avant le seed."
            )

        category_model = apps.get_model("categories", "Category")
        categories = list(category_model.objects.all())

        if model_has_field(category_model, "is_active"):
            categories = [
                category for category in categories
                if category.is_active
            ]

        User = apps.get_model("users", "User")
        user = User.objects.filter(is_active=True).first()

        # Créer ou réutiliser les attributs et leurs valeurs.
        attribute_values = {}

        for family in FAMILIES.values():
            for attribute_name, values in family["attributes"].items():
                attribute, _ = Attribute.objects.get_or_create(
                    name=attribute_name,
                    defaults={"slug": slugify(attribute_name)},
                )

                for value in values:
                    attribute_value, _ = AttributeValue.objects.get_or_create(
                        attribute=attribute,
                        value=value,
                    )
                    attribute_values[(attribute_name, value)] = (
                        attribute_value
                    )

        # Numérotation explicite : bulk_create n'appelle pas save().
        prefix = f"PRD-{__import__('datetime').date.today():%Y%m}-"
        last_number = (
            Product.objects.filter(number__startswith=prefix)
            .order_by("-number")
            .values_list("number", flat=True)
            .first()
        )

        if last_number:
            try:
                start_number = int(last_number.rsplit("-", 1)[1]) + 1
            except (ValueError, IndexError):
                start_number = Product.objects.count() + 1
        else:
            start_number = 1

        existing_slugs = set(
            Product.objects.values_list("slug", flat=True)
        )

        created_products = 0
        created_variants = 0
        created_stocks = 0
        created_links = 0

        for batch_start in range(0, product_count, batch_size):
            batch_count = min(batch_size, product_count - batch_start)

            with transaction.atomic():
                products_to_create = []
                product_metadata = []

                for offset in range(batch_count):
                    index = batch_start + offset
                    number = prefix + f"{start_number + index:06d}"

                    family_key = random.choice(list(FAMILIES))
                    family = FAMILIES[family_key]
                    base_name = random.choice(family["names"])

                    # Évite les noms identiques pour les produits de test.
                    name = f"{base_name} - Série {start_number + index}"

                    base_slug = slugify(name)[:180] or f"produit-{index}"
                    slug = base_slug
                    suffix = 1

                    while slug in existing_slugs:
                        slug = f"{base_slug[:170]}-{suffix}"
                        suffix += 1

                    existing_slugs.add(slug)

                    product_kwargs = {
                        "id": uuid.uuid4(),
                        "name": name,
                        "slug": slug,
                        "number": number,
                        "is_active": True,
                    }

                    if model_has_field(Product, "description"):
                        product_kwargs["description"] = (
                            f"{name}. Produit synthétique de démonstration "
                            "pour les tests de gestion de stock."
                        )

                    if model_has_field(Product, "is_perishable"):
                        product_kwargs["is_perishable"] = family["perishable"]

                    if model_has_field(Product, "created_by") and user:
                        product_kwargs["created_by"] = user

                    image_url = random.choice(IMAGE_URLS)
                    if model_has_field(Product, "image_url"):
                        product_kwargs["image_url"] = image_url
                    elif model_has_field(Product, "image"):
                        product_kwargs["image"] = image_url

                    product = Product(**product_kwargs)
                    products_to_create.append(product)

                    category = find_category(family_key, categories)
                    product_metadata.append(
                        (product, family_key, family, category)
                    )

                Product.objects.bulk_create(
                    products_to_create,
                    batch_size=batch_size,
                )

                category_links = [
                    CategoryProduct(category=category, product=product)
                    for product, _, _, category in product_metadata
                    if category is not None
                ]

                CategoryProduct.objects.bulk_create(
                    category_links,
                    ignore_conflicts=True,
                    batch_size=batch_size,
                )

                variants_to_create = []
                variant_metadata = []

                for product, family_key, family, _ in product_metadata:
                    attribute_names = list(family["attributes"])

                    # Prépare toutes les combinaisons possibles, puis en
                    # sélectionne sans doublon pour chaque produit.
                    value_lists = [
                        family["attributes"][attribute_name]
                        for attribute_name in attribute_names
                    ]
                    combinations = list(cartesian_product(*value_lists))
                    random.shuffle(combinations)

                    selected = combinations[:min(
                        variants_per_product, len(combinations)
                    )]

                    for variant_index, combination in enumerate(selected, 1):
                        variant_name = " / ".join(
                            f"{attribute}: {value}"
                            for attribute, value in zip(
                                attribute_names, combination
                            )
                        )

                        sku = (
                            f"{product.number}-V{variant_index:03d}"
                        )

                        price_min, price_max = family["price"]
                        price = Decimal(
                            str(random.randint(price_min, price_max))
                        )

                        variant_kwargs = {
                            "id": uuid.uuid4(),
                            "product": product,
                            "name": variant_name,
                            "sku": sku,
                            "price": price,
                            "is_active": True,
                        }

                        if model_has_field(Variant, "created_by") and user:
                            variant_kwargs["created_by"] = user

                        variant = Variant(**variant_kwargs)
                        variants_to_create.append(variant)

                        variant_metadata.append(
                            (variant, family, attribute_names, combination)
                        )

                Variant.objects.bulk_create(
                    variants_to_create,
                    batch_size=batch_size * variants_per_product,
                )

                links_to_create = []
                stocks_to_create = []

                for variant, family, attribute_names, combination in variant_metadata:
                    # Une valeur au maximum par attribut pour chaque variante.
                    for attribute_name, value in zip(
                        attribute_names, combination
                    ):
                        links_to_create.append(
                            VariantAttributeValue(
                                variant=variant,
                                attribute_value=attribute_values[
                                    (attribute_name, value)
                                ],
                            )
                        )

                    stocked_quantity = random.randint(20, 500)
                    remaining_quantity = random.randint(
                        0, stocked_quantity
                    )

                    stocks_to_create.append(
                        Stock(
                            id=uuid.uuid4(),
                            variant=variant,
                            warehouse=random.choice(warehouses),
                            stocked_quantity=stocked_quantity,
                            remaining_quantity=remaining_quantity,
                            target_service_level=Decimal("0.9500"),
                            is_active=True,
                        )
                    )

                VariantAttributeValue.objects.bulk_create(
                    links_to_create,
                    ignore_conflicts=True,
                    batch_size=batch_size * variants_per_product * 3,
                )

                Stock.objects.bulk_create(
                    stocks_to_create,
                    batch_size=batch_size * variants_per_product,
                )

                created_products += len(products_to_create)
                created_variants += len(variants_to_create)
                created_links += len(links_to_create)
                created_stocks += len(stocks_to_create)

            self.stdout.write(
                f"Progression : {created_products}/{product_count} produits"
            )

        self.stdout.write(self.style.SUCCESS(
            "\nGénération terminée.\n"
            f"Produits créés : {created_products}\n"
            f"Variantes créées : {created_variants}\n"
            f"Associations variante-attribut : {created_links}\n"
            f"Stocks créés : {created_stocks}\n"
        ))