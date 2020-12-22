from django.db import models
from django.conf import settings
from products.models import Product
from registration.models import  Provider 
from django.contrib.auth.models import User


# Create your models here.
class Comment(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    flag = models.BooleanField(default=False)
    content = models.TextField()

    def __str__(self):
        return self.content

class CommentProvider(models.Model):
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , related_name='active_user')
    created_on = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    flag = models.BooleanField(default=False)


    def __str__(self):
        return self.content
