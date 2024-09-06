from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    profession = models.CharField(max_length=150, blank=True, null=True)
    
    def __str__(self):
        return self.username