from django.db import models, transaction
import uuid
from django.utils import timezone
from django.db.models import Q, F
from django.conf import settings
from apps.products.models import Variant
from apps.warehouses.models import Warehouse
from apps.users.models import User

class Stock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stocked_quantity = models.PositiveIntegerField(default=0)
    remaining_quantity = models.PositiveIntegerField(default=0)
    target_service_level = models.DecimalField(max_digits=5, decimal_places=4, default=0.9500)
    variant = models.ForeignKey(Variant, on_delete=models.PROTECT, related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="stocks")
    is_active = models.BooleanField( default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField( auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["variant", "warehouse"],
                name="unique_stock_variant_warehouse",
            ),
            models.CheckConstraint(
                condition=Q(
                    remaining_quantity__lte=F("stocked_quantity")
                ),
                name="stock_remaining_lte_stocked",
            ),
            models.CheckConstraint(
                condition=Q(target_service_level__gte=0)
                & Q(target_service_level__lte=1),
                name="stock_service_level_between_0_and_1",
            ),
        ]

    def __str__(self):
        return f"{self.variant.name} - {self.warehouse.name}"


class BatchSequence(models.Model):
    period = models.CharField(max_length=6, unique=True)
    last_number = models.PositiveIntegerField(default=0)
    

class Batch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_number = models.CharField(max_length=150)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="batchs_created")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="batchs_received")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.batch_number:
            return super().save(*args, **kwargs)

        with transaction.atomic():
            period = timezone.localdate().strftime("%Y%m")
            sequence, _ = BatchSequence.objects.get_or_create(
                period=period,
            )

            sequence = BatchSequence.objects.select_for_update().get(
                pk=sequence.pk,
            )

            sequence.last_number += 1
            sequence.save(update_fields=["last_number"])

            self.batch_number = (
                f"BAT-{period}-{sequence.last_number:04d}"
            )

            super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        
class BatchItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, related_name="items")
    variant = models.ForeignKey(Variant, on_delete=models.PROTECT, related_name="batch_items")
    expiration_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "variant"],
                name="unique_batch_variant",
            ),
        ]

    def __str__(self):
        return f"{self.batch.batch_number} - {self.variant.name}"