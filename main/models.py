from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # You can add additional fields here if needed
    email = models.EmailField(unique=True)
    # username, password are already in AbstractUser


User = get_user_model()


class RequestCount(models.Model):
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=64, db_index=True)
    ip_address = models.GenericIPAddressField(null=True)
    window_start = models.DateTimeField(null=True)
    requests = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "device_id")