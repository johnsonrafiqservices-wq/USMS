from django import forms
from django.contrib.auth import get_user_model
from academics.models import Department

User = get_user_model()


class StaffCreateForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    staff_id = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    staff_type = forms.ChoiceField(choices=[('academic', 'Academic'), ('non_academic', 'Non-academic')], widget=forms.Select(attrs={'class': 'form-select'}), initial='academic')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username
