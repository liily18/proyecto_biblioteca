from django.urls import path
from .views import index, arrendar, misArriendos, devolver
from web.views import CustomLoginView, CustomLogoutView, RegisterView

urlpatterns = [
    path('', index, name='index'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('libros/<int:libro_id>/arrendar/', arrendar, name='arrendar'),
    path('libros/misarriendos/', misArriendos, name='misarriendos'),
    path('mis_arriendos/<int:libro_id>/devolver/', devolver, name='devolver'),
]