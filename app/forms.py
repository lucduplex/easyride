import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Reservation, RideOrder , RideRating
from django.core.validators import RegexValidator

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    cell = forms.CharField(max_length=15, validators=[RegexValidator(regex=r'^(\D*514|\D*438)\D*\d{3}\D*\d{4}$', message="Le numéro de téléphone doit commencer par 514 ou 438 et doit comporter 15 chiffres.")], required=True)
    address = forms.CharField(max_length=255, required=True)
    face_id = forms.ImageField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'cell', 'address', 'face_id', 'password1', 'password2')
        
        
class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=15, required=True)
    cell = forms.CharField(max_length=15, validators=[RegexValidator(regex=r'^(\D*514|\D*438)\D*\d{3}\D*\d{4}$', message="Le numéro de téléphone doit commencer par 514 ou 438 et doit comporter 15 chiffres.")], required=True)
    email = forms.EmailField(required=True)
    address = forms.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'cell', 'address')
        
        
class ConfirmationOfPasswordForm(forms.Form):
    password = forms.CharField(required=True)



class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['pickup', 'destination', 'date', 'time']



class RideOrderForm(forms.ModelForm):
    class Meta:
        model = RideOrder
        fields = ['pickup', 'destination']
        
class RideRatingForm(forms.ModelForm):
    class Meta:
        model = RideRating
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'placeholder': 'Notez de 1 à 5'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Laissez un commentaire'})
        }
        labels = {
            'rating': 'Note (1-5)',
            'comment': 'Commentaire'
        }
