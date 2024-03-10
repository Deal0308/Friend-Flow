from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model
from django import forms
from .models import Comment

# Import your custom user model
User = get_user_model()

class UserAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'  # or specify the fields you want to include


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # Specify the fields you want in the form
        labels = {
            'content': 'Your comment'
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4})  # Adjust rows as needed
        }




