from django.test import TestCase

# Create your tests here.

import pytest

from django.contrib.auth import get_user_model
from apps.products.models import Product


User = get_user_model()


@pytest.mark.django_db
def test_product_can_be_created():
    user = User.objects.create_user(
        username="test_manager",
        email="manager@example.com",
        password="TestPassword123!",
    )

    product = Product.objects.create(
        name="Produit de test",
        description="Produit utilisé pour les tests automatisés",
        image="https://example.com/images/product-test.jpg",
        is_perishable=False,
        created_by=user,
    )

    assert product.pk is not None
    assert product.name == "Produit de test"
    assert product.is_perishable is False
    assert product.created_by == user
    assert product.image.startswith("https://")
    assert product.slug
    assert product.number