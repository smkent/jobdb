from django.forms import ModelForm

from .models import User


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "linkedin"]
