from .models import Comment , CommentProvider
from django import forms


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)

class CommentProviderForm(forms.ModelForm):
    class Meta:
        model = CommentProvider
        fields = ("content",)
