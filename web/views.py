from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import timedelta, date
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, LogoutView
from .models import *
from .forms import CategoriaFilterForm

@login_required 
def index(request):
    form = CategoriaFilterForm(request.GET)  
    
    if form.is_valid():
        categoria = form.cleaned_data.get('categoria')  
        if categoria:
            libros = Libro.objects.filter(categoria=categoria, disponible=True)  # Filtrar por disponible
        else:
            libros = Libro.objects.filter(disponible=True)  # Solo libros disponibles
    else:
        libros = Libro.objects.filter(disponible=True)  # Solo libros disponibles

    return render(request, 'index.html', {'libros': libros, 'form': form})



class RegisterView(View):
    def get(self, request):
        return render(request, 'registration/register.html')

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect(reverse('register'))  
        user = User.objects.create_user(username=email, email=email, password=password1, first_name=first_name, last_name=last_name)
        #user.is_active = False
        UserProfile.objects.create(user=user, tipo='cliente')
        user.save()
        user = authenticate(username=email, password=password1)
        if user is not None:
            login(request, user)
        messages.success(request, 'Usuario creado exitosamente')
        return redirect('index')
    
class CustomLoginView(SuccessMessageMixin, LoginView):
    success_message = "Sesion Iniciada Exitosamente"
    template_name = 'registration/login.html'  
    redirect_authenticated_user = True
    
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.add_message(request, messages.WARNING, "Sesion Cerrada Exitosamente")
        return response
    
@login_required
def arrendar(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        fecha_seleccionada = timezone.datetime.strptime(fecha, "%Y-%m-%d").date()
        fecha_hoy = timezone.now().date()
        
        if fecha_seleccionada < fecha_hoy:
            messages.error(request, "La fecha seleccionada debe ser hoy o una fecha futura.")
            return render(request, 'arrendar.html', {
                'libro': libro,
                'autor': libro.autor,
                'fecha': fecha, 
            })

        # Crear el nuevo arriendo
        nuevo_arriendo = Arriendo.objects.create(
            fecha=fecha,
            user=request.user,
            libro=libro
        )
        
        # Actualizar el estado del libro si es necesario
        libro.disponible = False  
        libro.save()

        messages.success(request, "Libro arrendado exitosamente.")  # Mensaje de éxito
        return redirect('index')  

    return render(request, 'arrendar.html', {
        'libro': libro,
        'autor': libro.autor,
    })


    

@login_required
def misArriendos(request):
    arriendos = Arriendo.objects.filter(user=request.user).select_related('libro')

    return render(request, 'mis_arriendos.html', {'arriendos': arriendos})


def devolver(request, libro_id):
    libro = get_object_or_404(Libro, id= libro_id)
    libro.disponible = True
    libro.save()

    Arriendo.objects.filter(libro=libro, user=request.user).delete()
    messages.success(request, 'Libro devuelto, Gracias por su preferencia.')
    return redirect('index')  
