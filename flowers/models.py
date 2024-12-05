from django.db import models

class Flower(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='flowers/', blank=True, null=True)
    stock = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True, default=0)# Requires Pillow library
    # Add other relevant fields like category, availability, etc.
