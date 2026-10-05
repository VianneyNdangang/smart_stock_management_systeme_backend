from django.db import models
import uuid
from django.utils.text import slugify


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False )
    name = models.CharField( max_length=100 )
    slug = models.SlugField( max_length=100, unique=True, editable=False)
    description = models.TextField(blank=True)
    level = models.PositiveIntegerField(default=1, editable=False)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="children")
    is_active = models.BooleanField( default=True)
    deleted_at = models.DateTimeField( null=True, blank=True )
    created_at = models.DateTimeField( auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_active_category_name",
            )
        ]

    def __str__(self):
        return self.name