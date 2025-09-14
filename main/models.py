from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # You can add additional fields here if needed
    email = models.EmailField(unique=True)
    # username, password are already in AbstractUser


User = get_user_model()


class RequestCount(models.Model):
    ip_address = models.CharField(
        max_length=45, blank=True, null=True)  # For anonymous
    user = models.ForeignKey(User, null=True, blank=True,
                             on_delete=models.CASCADE)  # For logged-in
    requests = models.PositiveIntegerField(default=0)
    window_start = models.DateTimeField(null=True, blank=True)
    last_request = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.requests} reqs"
        return f"{self.ip_address} - {self.requests} reqs"
