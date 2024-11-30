from django.db import models

class Flower(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='flowers/', blank=True, null=True)  # Requires Pillow library
    # Add other relevant fields like category, availability, etc.
