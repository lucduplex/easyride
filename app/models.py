from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    cell = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    face_id = models.ImageField(upload_to='face_ids/', blank=True, null=True)

    # Ajoute related_name pour éviter les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    REQUIRED_FIELDS = ['email', 'cell']

    def __str__(self):
        return self.username
    
class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pickup = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.pickup} à {self.destination}"


class RideOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pickup = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='en cours')  
    
    def __str__(self):
        return f"Commande de {self.user.username} de {self.pickup} à {self.destination}"
    
# Noter la course et 
class RideRating(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name="ride_rating")
    rating = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Évaluation de la course {self.reservation} : {self.rating} étoiles"

# Suivis des vehicules
class Vehicle(models.Model):
    name = models.CharField(max_length=255)
    location_lat = models.FloatField()
    location_lng = models.FloatField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

