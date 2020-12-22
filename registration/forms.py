from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile , Provider , User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text="Required. Inform a valid email address.",
    )
    birth_date = forms.DateField(help_text="Required. Format: YYYY-MM-DD")
    phone_number = forms.CharField(max_length=8, required=True, help_text="Required.")
    address = forms.CharField(max_length=30, required=True, help_text="Required.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "address",
            "phone_number",
            "password1",
            "password2",
        )

class signupProviderForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text="Required. Inform a valid email address.",
    )
    phone_number = forms.CharField(max_length=8, required=True, help_text="Required.")
    address = forms.CharField(max_length=30, required=True, help_text="Required.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "address",
            "phone_number",
            "password1",
            "password2",
        )


# User update form allows users to update user name , email , address , phone_number and his birth_date
class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",

        ]


# Profile update form allows users to update image
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "birth_date",
            "address",
            "phone_number",
            "image",
        ]
