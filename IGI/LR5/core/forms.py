from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import Client, Driver, Organization

class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=True)
    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Вам должно быть не менее 18 лет'
    )
    organization_name = forms.CharField(max_length=100, required=False, help_text='Название организации (если есть)')
    organization_address = forms.CharField(max_length=200, required=False, help_text='Адрес организации (если есть)')
    organization_phone = forms.CharField(max_length=20, required=False, help_text='Телефон организации (если есть)')
    organization_email = forms.EmailField(required=False, help_text='Email организации (если есть)')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_date', 'phone', 'organization_name', 'organization_address', 'organization_phone', 'organization_email', 'password1', 'password2')

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        today = date.today()
        age = relativedelta(today, birth_date).years
        if age < 18:
            raise ValidationError('Вам должно быть не менее 18 лет для регистрации.')
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create or get organization if details provided
            organization = None
            if self.cleaned_data.get('organization_name'):
                organization = Organization.objects.create(
                    name=self.cleaned_data['organization_name'],
                    address=self.cleaned_data['organization_address'],
                    phone=self.cleaned_data['organization_phone'],
                    email=self.cleaned_data['organization_email']
                )
            
            # Create client profile
            Client.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                birth_date=self.cleaned_data['birth_date'],
                organization=organization
            )
        
        return user

class DriverRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=True, help_text='Введите номер телефона')
    license_number = forms.CharField(max_length=20, required=True, help_text='Номер водительской лицензии')
    experience = forms.IntegerField(min_value=0, required=True, help_text='Стаж вождения (лет)')
    birth_date = forms.DateField(required=True, help_text='Дата рождения', 
                               widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            Driver.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                license_number=self.cleaned_data['license_number'],
                experience=self.cleaned_data['experience'],
                birth_date=self.cleaned_data['birth_date']
            )
        
        return user 