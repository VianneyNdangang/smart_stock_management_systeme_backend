from django.db import models
from .constants import Form
from django.contrib.auth.models import AbstractUser
from ..warehouses.models import Warehouse
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.URLField(max_length=500, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=15, null=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True,related_name="users")
    role = models.CharField(max_length=16, null=False, choices=Form.ROLES)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField( auto_now_add=True)
  

    class Meta:
        ordering = ["-created_at"]
        # permissions = [
        #     ("view_user")
        # ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

