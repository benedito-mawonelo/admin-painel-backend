from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    STATUS_CHOICES = (
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
    )

    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    avatar = models.URLField(blank=True, null=True)
    roles = models.ManyToManyField(Role, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name or self.username

class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"