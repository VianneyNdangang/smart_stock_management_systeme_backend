from django.db import models
import uuid
from django.utils.text import slugify
from apps.categories.models import Category
from django.conf import settings
from django.utils import timezone

class Product(models.Model):
    id = models.UUIDField(primary_key= True, default=uuid.uuid4, editable= False)
    slug = models.SlugField(max_length=150, unique=True, editable= False)
    number = models.CharField(max_length=50, unique=True, editable=False, null=True)
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    is_perishable = models.BooleanField(default=False)
    image = models.ImageField(upload_to="products/")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name="products_created")
    is_active = models.BooleanField( default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField( auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if not self.number:
            aujourdhui = timezone.now()
            prefixe_date = aujourdhui.strftime("%Y%m") # Format: 202610
            
            # On cherche les produits créés ce mois-ci qui ont un numéro commençant par ce préfixe
            produits_du_mois = Product.objects.filter(number__startswith=f"PRD-{prefixe_date}")
            
            compteur = produits_du_mois.count() + 1
            
            # Donne par exemple : PRD-202610-0001
            self.number = f"PRD-{prefixe_date}-{compteur:04d}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Variant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable= False)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="variants")
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField( max_length=100, unique= True, null= True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name="variants_created")
    is_active = models.BooleanField( default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField( auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class VariantImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="variants/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.alt_text and self.variant:
             self.alt_text = self.variant.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.variant.name}"


class Attribute(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable= False)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True, editable=False)
    created_at = models.DateTimeField( auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable= False)
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, related_name="values")
    value = models.CharField(max_length=150)
    is_active = models.BooleanField( default=True)
    created_at = models.DateTimeField( auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attribute", "value"],
                name="unique_attribute_value"
            )
        ]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class VariantAttributeValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable= False)
    variant = models.ForeignKey(Variant, on_delete= models.PROTECT, related_name= "attribute_values")
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, related_name= "variant_assignments")
    created_at = models.DateTimeField( auto_now_add= True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["variant", "attribute_value"],
                name="unique_variant_attribute_value"
            ),
        ]
    def __str__(self):
        return f"{self.variant} - {self.attribute_value}"

class CategoryProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products" )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="category_assignements")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["category", "product"],
                name="unique_category_product",
            ),
        ]
    def __str__(self):
        return f"{self.category} - {self.product}"
   