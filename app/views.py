import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, UpdateUserForm, ConfirmationOfPasswordForm, ReservationForm, RideOrderForm,RideRatingForm, ReservationForm
from .models import Reservation, RideOrder, Vehicle
from django.contrib import messages
from datetime import date
import face_recognition
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from geopy.geocoders import Nominatim
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.utils import timezone
from .utils import calculate_price
import requests
import stripe
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import datetime
from django.core.exceptions import ValidationError
stripe.api_key = settings.STRIPE_SECRET_KEY



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        face_image = request.FILES.get('face_id')

        if username and password and face_image:
            # Authentification classique avec username et password
            user = authenticate(username=username, password=password)

            if user is not None:
                # Vérification de FaceID
                if user.face_id:
                    try:
                        # Charger l'image FaceID de l'utilisateur depuis le système
                        known_image = face_recognition.load_image_file(user.face_id.path)
                        
                        # Charger l'image envoyée dans le formulaire pour la comparaison
                        unknown_image = face_recognition.load_image_file(face_image)

                        # Extraire les encodages des visages
                        known_encoding = face_recognition.face_encodings(known_image)
                        unknown_encoding = face_recognition.face_encodings(unknown_image)

                        if not known_encoding or not unknown_encoding:
                            raise ValidationError("Aucun visage détecté dans l'image.")

                        # Comparer les deux visages
                        results = face_recognition.compare_faces([known_encoding[0]], unknown_encoding[0])

                        if results[0]:
                            # Connexion de l'utilisateur après validation FaceID
                            login(request, user)
                            return redirect('home')
                        else:
                            messages.error(request, "Échec de la reconnaissance faciale.")
                    except Exception as e:
                        messages.error(request, f"Erreur lors de la vérification de FaceID : {e}")
                else:
                    messages.error(request, "Aucun FaceID enregistré pour cet utilisateur.")
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Veuillez entrer tous les champs requis.")
    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Formulaire d'inscription invalide. Veuillez vérifier vos informations.")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def home_view(request):
    return render(request, 'home.html')

def user_logout(request):
    logout(request)
    request.session.flush()  # Vider la session lors de la déconnexion
    return redirect('login')  # Redirection vers la page de connexion après déconnexion


def about_view(request):
    return render(request, 'about.html')  # Assurez-vous que 'about.html' existe dans vos templates

def profile_view(request):
    if request.user.is_authenticated:
        user_face_id = request.user.face_id
        data = {
            'user_face_id': user_face_id
        }
        return render(request, 'profile.html', data)
    else:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('login')  # Redirect to login if user is not authenticated
        
def confirm_deleteUser_View(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ConfirmationOfPasswordForm(request.POST)
            if form.is_valid():
                current_user_password = request.user.password
                entered_password = form.cleaned_data['password']
                if check_password(entered_password, current_user_password):
                    try:
                        current_user = request.user
                        current_user.delete()
                        return redirect('home')
                    except:
                        messages.error(request, "Erreur lors de la suppression de votre compte.")
                else:
                    messages.error(request, "Le mot de passe est incorrect.")
        else:
            form = ConfirmationOfPasswordForm()

        current_user_face_id = request.user.face_id
        data = {
            "user_face_id": current_user_face_id,
            "form": form
        }
        
        return render(request, 'confirm_deleteUser.html', data)
    else:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('login')  # Redirect to login if user is not authenticated

def updateAccount_view(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UpdateUserForm(request.POST, request.FILES, instance=request.user)  # Pass current user as instance
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.instance)  # Keep the user logged in after password change
                messages.success(request, "Votre compte a été mis à jour avec succès.")
                # return redirect('profile')
            # else:
            #     messages.error(request, "Formulaire de modification invalide. Veuillez vérifier vos informations.")
        else:
            form = UpdateUserForm(instance=request.user)  # Prepopulate the form with the current user data

        user_face_id = request.user.face_id  # Get the face_id of the current user
        data = {
            'user_face_id': user_face_id,
            'form': form
        }
        return render(request, 'modifier_compte.html', data)
    else:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('login')  # Redirect to login if user is not authenticated

def updatePassword_view(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PasswordChangeForm(user = request.user, data = request.POST)  # Pass current user as instance
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Keep the user logged in after password change
                messages.success(request, "Votre mot de passe a été mis à jour avec succès.")
                # return redirect('profile')
            # else:
            #     messages.error(request, "Erreur lors de modification de votre mot de passe.")
        else:
            form = PasswordChangeForm(user = request.user)  # Prepopulate the form with the current user data

        user_face_id = request.user.face_id  # Get the face_id of the current user
        data = {
            'user_face_id': user_face_id,
            'form': form
        }
        return render(request, 'modifier_mdp.html', data)
    else:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('login')  # Redirect to login if user is not authenticated
    

@csrf_exempt
def geolocate_view(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if not (latitude and longitude):
            return JsonResponse({'error': 'Invalid data'}, status=400)
        
        # Définir un User-Agent personnalisé
        geolocator = Nominatim(user_agent="MonApplication/1.0")
        location = geolocator.reverse(f"{latitude}, {longitude}")
        address = location.address
        return JsonResponse({'address': address})
    return render(request, 'geolocate.html')


def confirm_ride(request, type, id):
    # Récupérer la réservation ou la commande
    if type == 'reservation':
        ride = get_object_or_404(Reservation, id=id)
    elif type == 'order':
        ride = get_object_or_404(RideOrder, id=id)
    else:
        return render(request, 'error.html', {'message': "Type de trajet invalide."})

    # Calculer l'itinéraire et le prix
    route = calculate_route(ride.pickup, ride.destination)
    if route is None:
        # Gérez l'erreur, redirigez ou affichez un message approprié
        return render(request, 'error.html', {'message': "Impossible de calculer l'itinéraire. Veuillez réessayer plus tard."})

    price_simple = calculate_price(route['distance'], 'simple')
    price_xl = calculate_price(route['distance'], 'xl')
    price_comfort = calculate_price(route['distance'], 'comfort')

    # Créer une session Stripe
    stripe_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"Trajet de {ride.pickup} à {ride.destination}",
                    "description": f"Type: {type.capitalize()} - Distance: {route['distance']} km",
                },
                "unit_amount": int(price_simple * 100), 
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri(f"/payment-success/{type}/{id}/"),
        cancel_url=request.build_absolute_uri(f"/payment-cancelled/{type}/{id}/"),
    )

    return render(request, 'confirm_ride.html', {
        'ride': ride,
        'route': route,
        'price_simple': price_simple,
        'price_xl': price_xl,
        'price_comfort': price_comfort,
        'stripe_session_id': stripe_session.id,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'key': settings.GOOGLE_API_KEY
    })


def reservation_success(request):
    return render(request, 'reservation_success.html')

def order_success(request):
    return render(request, 'order_success.html')


def my_orders(request):
    return render(request, 'my_orders.html')

@login_required
def orders_list(request, order_type):
    if order_type == 'reservations':
        orders = Reservation.objects.filter(user=request.user)
        # Redirige vers une autre vue ou affiche les réservations
        return redirect("reservation_history")
    elif order_type == 'rideOrders':
        orders = RideOrder.objects.filter(user=request.user)
        return render(request, 'orders_list.html', {'orders': orders, 'order_type': order_type})
    else:
        # Gérez le cas où order_type est invalide
        return render(request, 'orders_list.html', {
            'orders': [],
            'order_type': 'unknown'
        })

def calculate_route(departure, destination):
    try:
        api_key = 'AIzaSyCdS-b3HBY7uprOXdV34wTgYJW1tSWGn0s'
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={departure}&destination={destination}&key={api_key}"
        response = requests.get(url)
        data = response.json()

        
        print(data)

        if data['status'] == 'OK':
            route = data['routes'][0]['legs'][0]
            return {
                'distance': route['distance']['value'],  
                'duration': route['duration']['value'],  
                'steps': route['steps']  
            }
        else:
            
            print(f"API error: {data['status']} - {data.get('error_message')}")
    except Exception as e:
        print(f"Error calculating route: {e}")
    
    return None


def calculate_price(distance, vehicle_type):
    base_price = 5.0
    if vehicle_type == 'simple':
        price_per_km = 1.0
    elif vehicle_type == 'xl':
        price_per_km = 1.5
    elif vehicle_type == 'comfort':
        price_per_km = 2.0

    return base_price + (distance / 1000.0) * price_per_km

def course_confirme(request):
    pickup = request.GET.get('pickup')
    destination = request.GET.get('destination')
    vehicle = request.GET.get('vehicle')
    price = request.GET.get('price')

    context = {
        'pickup': pickup,
        'destination': destination,
        'vehicle': vehicle,
        'price': price,
    }

    return render(request, 'course_confirme.html', context)


def edit_order(request, order_type, id):
    if order_type == 'reservations':
        order = get_object_or_404(Reservation, id=id)
        form = ReservationForm(request.POST or None, instance=order)
    elif order_type == 'rideOrders':
        order = get_object_or_404(RideOrder, id=id)
        form = RideOrderForm(request.POST or None, instance=order)
    else:
        return redirect('my_orders')  # Redirection si l'ordre n'est pas trouvé

    if form.is_valid():
        form.save()
        return redirect('my_orders')  # Redirection après la sauvegarde

    return render(request, 'edit_order.html', {'form': form, 'order_type': order_type})

def delete_order(request, order_type, id):
    if order_type == 'reservations':
        order = get_object_or_404(Reservation, id=id)
    elif order_type == 'rideOrders':
        order = get_object_or_404(RideOrder, id=id)
    else:
        return redirect('my_orders')  # Redirection si l'ordre n'est pas trouvé

    if request.method == 'POST':
        order.delete()
        return redirect('my_orders')  # Redirection après la suppression

    return render(request, 'confirm_delete.html', {'order': order, 'order_type': order_type})


def rate_ride(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        form = RideRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.reservation = reservation
            rating.save()
            return redirect('home')
    else:
        form = RideRatingForm()
    return render(request, 'rate_ride.html', {'form': form, 'reservation': reservation})

def vehicle_tracking(request):
    vehicles = Vehicle.objects.filter(available=True)
    return render(request, 'vehicle_tracking.html', {'vehicles': vehicles})

def confirmation(request):
    return render(request, 'confirmation.html')

def book_ride(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                reservation = form.save(commit=False)
                reservation.user = request.user
                reservation.vehicle_type = form.cleaned_data['vehicle_type']
                start_point = form.cleaned_data['start_point']
                destination = form.cleaned_data['destination']
                
                print(f"Start Point: {start_point}")
                print(f"Destination: {destination}")
                            

                try:
                    price = calculate_price(start_point, destination, reservation.vehicle_type)  
                    if price is None:
                        raise ValueError("Le calcul du prix a échoué.")
                    reservation.price = price
                except ValueError as e:
                    return render(request, 'book_ride.html', {
                        'form': form,
                        'error': f"Erreur lors du calcul du prix : {e}"
                    })
                if 'immediate' in request.POST:
                    reservation.scheduled_datetime = timezone.now()
                    reservation.status = 'Confirmed'
                else:
                    if reservation.scheduled_datetime <= timezone.now():
                        return render(request, 'book_ride.html', {
                            'form': form,
                            'error': 'Veuillez sélectionner une date et une heure futures pour la réservation.'
                        })
                    reservation.status = 'Scheduled'
                reservation.save()
                return redirect('payment_page', reservation.id)
            else:
                return redirect('login')
    else:
        form = ReservationForm()
    return render(request, 'book_ride.html', {'form': form})


@login_required  
def order_ride(request):
    if request.method == 'POST':
        form = RideOrderForm(request.POST)
        if form.is_valid():
            ride_order = form.save(commit=False)
            # Assurez-vous que l'utilisateur est connecté
            if request.user.is_authenticated:
                ride_order.user = request.user
                ride_order.save()
                return redirect('confirm_ride', type='order', id=ride_order.id)
            else:
                # Rediriger l'utilisateur vers la page de connexion s'il n'est pas authentifié
                return redirect('login')
    else:
        form = RideOrderForm()
    return render(request, 'book_ride.html', {'form': form, 'date_today': date.today().isoformat()})

@login_required
def reservation_view(request):
    context = {"date_today": now().date()}

    if request.method == "POST":
        pickup = request.POST.get("depart")
        destination = request.POST.get("destination")
        date = request.POST.get("date")
        time = request.POST.get("time")

        context.update({
            "pickup": pickup,
            "destination": destination,
            "date": date,
            "time": time,
        })

        if not (pickup and destination and date and time):
            context["error"] = "Tous les champs sont requis."
            return render(request, "book_ride.html", context)

        # Créer une nouvelle réservation
        reservation = Reservation.objects.create(
            user=request.user,
            pickup=pickup,
            destination=destination,
            date=date,
            time=time,
        )

        # Stocker temporairement les données dans la session si nécessaire
        request.session["reservation_data"] = {
            "pickup": pickup,
            "destination": destination,
            "date": date,
            "time": time,
        }

        # Rediriger avec l'ID de la réservation
        return redirect('confirm_ride', type='reservation', id=reservation.id)

    return render(request, "book_ride.html", context)


@login_required
def reservation_history_view(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'reservation_history.html', {'reservations': reservations})

def payment_success(request, type, id):
    # Récupérer la réservation ou la commande
    if type == 'reservation':
        ride = get_object_or_404(Reservation, id=id)
    elif type == 'order':
        ride = get_object_or_404(RideOrder, id=id)
    else:
        return render(request, 'error.html', {'message': "Type de trajet invalide."})

    # Marquer le trajet comme payé
    ride.is_paid = True
    ride.save()

    # Envoyer un e-mail de confirmation
    send_mail(
        subject="Confirmation de paiement EasyRide",
        message=(
            f"Bonjour {ride.user.username},\n\n"
            f"Votre paiement pour le trajet de {ride.pickup} à {ride.destination} a été confirmé.\n\n"
            f"Merci d'utiliser EasyRide !"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[ride.user.email],
    )

    return render(request, 'payment_success.html', {'ride': ride, 'type': type})

def payment_cancelled(request, type, id):
    return render(request, 'payment_cancelled.html', {
        'message': "Votre paiement a été annulé. Vous pouvez réessayer.",
        'type': type,
        'id': id,
    })

