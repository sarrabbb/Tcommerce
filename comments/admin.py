from django.contrib import admin
from .models import Comment , CommentProvider

# Register your models here.
admin.site.register(Comment)
admin.site.register(CommentProvider)
