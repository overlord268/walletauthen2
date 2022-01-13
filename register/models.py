from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  telefono = models.CharField(max_length=100)
  numero_ID = models.CharField(max_length=100, null=True)