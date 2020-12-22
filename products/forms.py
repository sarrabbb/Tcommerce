from django import forms
from .models import Product , Category , FlashSales

from django.forms import ModelForm

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = [
            "title",
            "description",
        ]

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "discount_price",
            "quantity",
            "category",
            "image",
        ]

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields["category"].empty_label = "Select"
        # self.fields['image'].required = False


class FlashSalesForm(ModelForm):
 
    class Meta(ModelForm):
        model = FlashSales
        fields = [
            "product",
            "new_price",
            "expire_date",
        ]
