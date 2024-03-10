from django.contrib.auth.forms import UserChangeForm
from .models import Profile
from django import forms

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'photo']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['photo'].widget.attrs.update({'class': 'form-control-file'})

class UserForm(UserChangeForm):
    class Meta:
        model = Profile  # Use Profile model instead of User model
        fields = ['user', 'bio', 'photo']  # Add 'user' field to link with User model


from .models import Message  # Import the Message model

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['content'].label = ''
        self.fields['content'].widget.attrs.update({'placeholder': 'Type your message here...'})

