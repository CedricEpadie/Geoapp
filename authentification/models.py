from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    PROFESSION_CHOICES = [
        ('Topographe', 'Topographe'),
        ('Urbaniste', 'Urbaniste'),
        ('Environnementaliste', 'Environnementaliste'),
        ('Génie civil', 'Génie civil'),
        ('Etudiant', 'Etudiant'),
    ]
    
    profession = models.CharField(max_length=150, choices=PROFESSION_CHOICES, blank=True, null=True)
    
    def __str__(self):
        return self.username
