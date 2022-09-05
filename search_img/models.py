from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    url = models.CharField(max_length=500)
    create_at = models.DateTimeField(auto_now_add=True)


class Pixels(models.Model):
    id = models.IntegerField(blank=None, primary_key=True)
    alt = models.CharField(max_length=100, blank=True)
    origin = models.ImageField()
    query = models.CharField(max_length=30, blank=True)

