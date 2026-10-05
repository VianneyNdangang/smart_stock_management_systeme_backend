from django.db import models
from .constants import RegionChoices
import uuid


class Warehouse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    location = models.CharField(max_length=100)
    region = models.CharField(max_length=15, null=False, choices=RegionChoices.choices)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField( auto_now_add=True)
  
    @property
    def is_deleted(self):
        return self.deleted_at is not None
    
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}"
