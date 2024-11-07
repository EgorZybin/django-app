from django import forms
from .models import Profile


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        clear_checkbox_label = 'Удалить аватар'



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'email', 'bio', 'agreement_accepted', 'avatar')
