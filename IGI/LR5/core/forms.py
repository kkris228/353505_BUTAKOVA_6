from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
import uuid
from .models import Client, Driver, Organization, Vehicle, News
from .validators import validate_phone

class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(
        max_length=20, 
        required=True,
        help_text='Формат: +375 (29) 123-45-67 или +375291234567'
    )
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

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        validate_phone(phone)
        return phone

    def clean_organization_phone(self):
        org_phone = self.cleaned_data.get('organization_phone')
        if org_phone:  # Проверяем только если телефон указан
            validate_phone(org_phone)
        return org_phone

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
    phone = forms.CharField(
        max_length=20, 
        required=True, 
        help_text='Формат: +375 (29) 123-45-67 или +375291234567'
    )
    license_number = forms.CharField(max_length=20, required=True, help_text='Номер водительской лицензии')
    experience = forms.IntegerField(min_value=0, required=True, help_text='Стаж вождения (лет)')
    birth_date = forms.DateField(required=True, help_text='Дата рождения', 
                               widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        validate_phone(phone)
        return phone

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

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['model', 'plate_number', 'year', 'capacity', 'body_type', 'is_available']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
            'capacity': forms.NumberInput(attrs={'min': 0}),
        }

class DriverForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(
        max_length=20,
        required=True,
        label='Телефон',
        help_text='Формат: +375 (29) 123-45-67 или +375291234567'
    )
    
    class Meta:
        model = Driver
        fields = ['first_name', 'last_name', 'email', 'phone', 'license_number', 'experience', 'birth_date', 'is_available', 'photo']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'experience': forms.NumberInput(attrs={'min': 0}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            initial = kwargs.get('initial', {})
            initial.update({
                'first_name': instance.user.first_name,
                'last_name': instance.user.last_name,
                'email': instance.user.email,
            })
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        validate_phone(phone)
        return phone

    def save(self, commit=True):
        driver = super().save(commit=False)
        if not hasattr(driver, 'user'):
            # Создаем уникальный username, добавляя случайный UUID
            unique_id = str(uuid.uuid4())[:8]
            username = f"driver_{self.cleaned_data['license_number']}_{unique_id}"
            
            # Создаем пароль на основе лицензии
            password = f"Driver_{self.cleaned_data['license_number'][:6]}"
            
            # Create new user if this is a new driver
            user = User.objects.create_user(
                username=username,
                email=self.cleaned_data['email'],
                password=password,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
            driver.user = user
        else:
            # Update existing user
            driver.user.first_name = self.cleaned_data['first_name']
            driver.user.last_name = self.cleaned_data['last_name']
            driver.user.email = self.cleaned_data['email']
            if commit:
                driver.user.save()
        
        if commit:
            driver.save()
        return driver 

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'description', 'content', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 