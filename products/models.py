from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Category(models.Model):
    owner =  models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
        
        
class Product(models.Model):
    owner =  models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.TextField()
    price = models.DecimalField(max_digits=100, decimal_places=2)
    discount_price = models.FloatField(blank=True)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to="pics/")
    addedTime = models.DateTimeField(auto_now_add=True, auto_now=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class FlashSales(models.Model):
    product = models.ForeignKey(Product ,on_delete=models.CASCADE)
    new_price = models.DecimalField(max_digits=100, decimal_places=2)
    publish_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    expire_date = models.DateTimeField(blank=True, null=True)
    approved =  models.BooleanField(default=False)

    def __str__(self):
        return self.product.name
