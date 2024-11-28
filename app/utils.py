import requests
from math import radians, sin, cos, sqrt, atan2
from django.core.mail import send_mail
from django.utils import timezone

# Définition des tarifs par kilomètre pour chaque type de véhicule
VEHICLE_PRICING = {
    'UberX': 1.5,       
    'UberXL': 2.5,      
    'Black': 3.5,       
    'SUV': 4.0,         
}

BASE_PRICE = 5  # Prix de base en cad

def send_email_notification(user_email, reservation):
    """
    Envoie un courriel de confirmation pour la réservation.
    """
    formatted_price = f"${reservation.price:.2f}"
    subject = "Confirmation de votre réservation - EasyRide"
    message = (
        f"Bonjour,\n\nVotre réservation de {reservation.start_point} à {reservation.destination} "
        f"a été confirmée pour un véhicule de type {reservation.vehicle_type}. "
        f"Le coût estimé est de {formatted_price}.\n\nMerci d'avoir choisi EasyRide !"
    )
    
    send_mail(
        subject,
        message,
        'no-reply@easyride.com',  # Adresse de l'expéditeur
        [user_email],  # Liste des destinataires
        fail_silently=False,
    )

# def geocode_address(address):
#     """
#     Utilise l'API Google Maps pour convertir une adresse en coordonnées GPS.
#     Nécessite une clé API Google Maps.
#     """
#     api_key = "AIzaSyAlCaWecwieHtFdAIJfExsVpvghyez573k"  # Remplacez par votre clé API Google Maps
#     url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Vérifie si la requête est réussie
        
#         data = response.json()
#         if data['results']:
#             latitude = data['results'][0]['geometry']['location']['lat']
#             longitude = data['results'][0]['geometry']['location']['lng']
#             return (latitude, longitude)
#         else:
#             raise ValueError("Adresse non trouvée.")
    
#     except requests.exceptions.RequestException as e:
#         error_message = data.get('error_message', 'Inconnue') if 'data' in locals() else str(e)
#         raise RuntimeError(f"Erreur API Google Maps : {error_message}") from e
import requests

def geocode_address(address):
    API_KEY = 'AIzaSyAtxDAdqf6Dg3Ozr0i0nrutpAi46G0RZRE'
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    # Vérification de la réponse de l'API
    if data['status'] == 'OK' and data['results']:
        return data['results'][0]['geometry']['location']  # Coordonnées du premier résultat
    else:
        # Ajout d'une sortie plus détaillée pour le débogage
        print(f"Erreur de géocodage pour l'adresse: {address}")
        print(f"Réponse de l'API: {data}")
        return None  # Adresse non trouvée
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(start_coords, dest_coords):
    """
    Calcule la distance en kilomètres entre deux points géographiques
    en utilisant la formule de Haversine.
    """
    # Coordonnées de départ et de destination
    lat1, lon1 = start_coords['lat'], start_coords['lng']
    lat2, lon2 = dest_coords['lat'], dest_coords['lng']
    
    # Conversion des degrés en radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Calcul des différences
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Formule de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Rayon de la Terre (en kilomètres)
    radius = 6371.0
    
    # Distance en kilomètres
    distance = radius * c
    return distance


def calculate_price(start_address, destination_address, vehicle_type):
    """
    Calcule le prix de la course en fonction de la distance et du type de véhicule.
    """
    try:
        # Convertit les adresses en coordonnées
        start_coords = geocode_address(start_address)
        dest_coords = geocode_address(destination_address)
        
        # Vérifie que les coordonnées ont été obtenues
        if not start_coords or not dest_coords:
            raise ValueError("Une des adresses n'a pas pu être géocodée.")
        
        # Calcule la distance
        distance = calculate_distance(start_coords, dest_coords)
        
        # Vérifie que le type de véhicule est valide
        if vehicle_type not in VEHICLE_PRICING:
            raise ValueError(f"Type de véhicule invalide: {vehicle_type}")

        # Obtenir le tarif par kilomètre pour le type de véhicule
        price_per_km = VEHICLE_PRICING[vehicle_type]
        
        # Calcul du prix total
        total_price = BASE_PRICE + (price_per_km * distance)
        return round(total_price, 2)  # Retourne le prix arrondi à deux décimales

    except (ValueError, RuntimeError) as e:
        # Log ou gestion des erreurs personnalisée
        print(f"Erreur lors du calcul du prix: {e}")
        return None  # Ou une valeur par défaut pour les cas d'erreurs
