from django.db import models

class FlowerCart(models.Model): #Cart Model
    user = models.ForeignKey('account.User', on_delete=models.CASCADE) #Link the cart to user
    flower = models.ForeignKey('flowers.Flower',on_delete=models.CASCADE) #Link the cart to the Flower
    quantity = models.IntegerField()

class Order(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    #Add other fields: status (e.g., pending, shipped, delivered), address, etc.
    flowerCart = models.ForeignKey('orders.FlowerCart', on_delete=models.CASCADE, blank=True, null=True)