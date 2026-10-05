from django.db import models
import uuid
from django.utils.text import slugify
from apps.categories.models import Category

class Product(models.Model):
    id = models.UUIDField(primary_key= True, default=uuid.uuid4, editable= False)
    slug = models.SlugField(max_length=150, unique=True, editable= False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products" )
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField( default=True)
    deleted_at = models.DateTimeField( null=True, blank=True )
    created_at = models.DateTimeField( auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
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
    barcode = models.CharField(max_length=100, unique= True, null= True, blank=True)
    is_active = models.BooleanField( default=True)
    deleted_at = models.DateTimeField( null=True, blank=True )
    created_at = models.DateTimeField( auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class Attribute(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable= False)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField( default=True)
    deleted_at = models.DateTimeField( null=True, blank=True )
    created_at = models.DateTimeField( auto_now_add=True)
    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable= False)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="value")
    value = models.CharField(max_length=150)
    is_active = models.BooleanField( default=True)
    deleted_at = models.DateTimeField( null=True, blank=True )
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
    variant = models.ForeignKey(Variant, on_delete= models.CASCADE, related_name= "attribute_values")
    attribute_value = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name= "variant_assignments")
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