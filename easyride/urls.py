from django.contrib import admin
from django.urls import path
from app.views import payment_cancelled,payment_success,reservation_view, reservation_history_view,confirmation, rate_ride, signup, login_view, home_view, user_logout, about_view, profile_view, confirm_deleteUser_View, updateAccount_view, updatePassword_view, geolocate_view, book_ride, reservation_success, order_ride, order_success, my_orders, orders_list, confirm_ride, course_confirme, edit_order, delete_order, vehicle_tracking
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('', home_view, name='home'),
    path('logout/', user_logout, name='logout'),
    path('about/', about_view, name='about'),
    path('profile/', profile_view, name='profile'),
    path('confirm_deleteUser/', confirm_deleteUser_View, name='confirm_deleteUser'),
    path('updateAccount/', updateAccount_view, name='updateAccount'),
    path('updatePassword/', updatePassword_view, name='updatePassword'),
    path('geolocate/', geolocate_view, name='geolocate'),
    path('book_ride/', book_ride, name='book_ride'),
    path('order_ride/', order_ride, name='order_ride'),
    path('my_orders/', my_orders, name='my_orders'), 
    path('my_orders/<str:order_type>/', orders_list, name='orders_list'), 
    path('reservation_success/', reservation_success, name='reservation_success'), 
    path('order_success/', order_success, name='order_success'),
    path('course_confirme/<str:type>/<int:id>/', course_confirme, name='course_confirme'),
    path('edit_order/<str:order_type>/<int:id>/', edit_order, name='edit_order'),
    path('delete_order/<str:order_type>/<int:id>/',delete_order, name='delete_order'),
    path('rate_ride/<int:reservation_id>/', rate_ride, name='rate_ride'),
    path('book_ride/',book_ride, name='book_ride'),
    path('confirmation/',confirmation, name='confirmation'),
    path('vehicle_tracking/', vehicle_tracking, name='vehicle_tracking'), 
    path('reservation/', reservation_view, name='reservation'),
    path('reservation/history/', reservation_history_view, name='reservation_history'),
    path('confirm-ride/<str:type>/<int:id>/', confirm_ride, name='confirm_ride'),
    path('payment-success/<str:type>/<int:id>/', payment_success, name='payment_success'),
    path('payment-cancelled/<str:type>/<int:id>/',payment_cancelled, name='payment_cancelled'),    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
