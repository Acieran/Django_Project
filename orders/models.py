from django.db import models

class FlowerCart(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    flower = models.ForeignKey('flowers.Flower', on_delete=models.CASCADE)
    quantity = models.IntegerField()

class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    flower = models.ForeignKey('flowers.Flower', on_delete=models.CASCADE)
    quantity = models.IntegerField()

class Order(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

