from django import forms
from .models import Student
from accounts.models import User
from academics.models import Programme, StudyYear, StudySemester, Intake

class StudentEditForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

    class Meta:
        model = Student
        fields = [
            'programme', 'current_year', 'current_semester_number', 'intake',
            'admission_date', 'expected_graduation', 'status', 'nationality',
            'guardian_name', 'guardian_phone', 'guardian_email', 'guardian_relationship',
            'blood_group', 'medical_conditions'
        ]
        widgets = {
            'programme': forms.Select(attrs={'class': 'form-select'}),
            'current_year': forms.Select(attrs={'class': 'form-select'}),
            'current_semester_number': forms.Select(attrs={'class': 'form-select'}),
            'intake': forms.Select(attrs={'class': 'form-select'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_graduation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'guardian_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone_number'].initial = self.instance.user.phone_number
            self.fields['date_of_birth'].initial = self.instance.user.date_of_birth
            self.fields['gender'].initial = self.instance.user.gender
            self.fields['address'].initial = self.instance.user.address

    def save(self, commit=True):
        student = super().save(commit=False)
        user = student.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        user.gender = self.cleaned_data['gender']
        user.address = self.cleaned_data['address']
        if commit:
            user.save()
            student.save()
        return student
