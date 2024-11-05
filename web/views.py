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
from .forms import CategoriaFilterForm, LibroForm



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

        # Crear el nuevo arriendo con la fecha en `fecha_arriendo`
        nuevo_arriendo = Arriendo.objects.create(
            fecha_arriendo=fecha_seleccionada,
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

    libros_data = []

    for arriendo in arriendos:
        libro = arriendo.libro
        fecha_arriendo = arriendo.fecha_arriendo 
        dias_arriendo = libro.tipo.dias_arriendo if libro.tipo else 0
        fecha_devolucion = fecha_arriendo + timedelta(days=dias_arriendo) if fecha_arriendo else None

        # Calcula multa si la fecha de devolución ha pasado
        multa = 0
        if fecha_devolucion and date.today() > fecha_devolucion:
            dias_atraso = (date.today() - fecha_devolucion).days
            multa = dias_atraso * libro.tipo.precio_dias_atraso if libro.tipo else 0

        # Agrega los datos calculados a un diccionario
        libros_data.append({  
            'id': libro.id,
            'nombre': libro.nombre,
            'autor': libro.autor,
            'categoria': libro.categoria,
            'fecha_arriendo': fecha_arriendo,
            'fecha_devolucion': fecha_devolucion,
            'multa': multa,
        })

    return render(request, 'mis_arriendos.html', {'libros_data': libros_data})




@login_required
def devolver(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    arriendo = get_object_or_404(Arriendo, libro=libro, user=request.user)

    # Calcular la fecha de devolución esperada y la multa si está atrasado
    dias_arriendo = libro.tipo.dias_arriendo if libro.tipo else 0
    fecha_devolucion_esperada = arriendo.fecha_arriendo + timedelta(days=dias_arriendo)
    dias_atraso = (date.today() - fecha_devolucion_esperada).days
    multa = 0

    if dias_atraso > 0:
        # Calcular la multa por los días de atraso
        multa = dias_atraso * libro.tipo.precio_dias_atraso if libro.tipo else 0
        messages.warning(
            request,
            f"El libro '{libro.nombre}' se retornó con {dias_atraso} días de atraso, generando una multa de ${multa}."
        )
    else:
        messages.success(request, f"El libro '{libro.nombre}' fue devuelto sin problemas.")

    # Actualizar el estado del libro a disponible
    libro.disponible = True
    libro.save()
    
    # Eliminar o marcar el arriendo como completado (según tu lógica)
    arriendo.delete()  # O marca como completado si deseas conservar el registro

    return redirect('misarriendos')  # Redirigir a la vista de arriendos


def agregar_libro(request):
    if request.method == 'POST':
        form = LibroForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo libro en la base de datos
            messages.success(request, "Libro agregado exitosamente.")
            return redirect('misarriendos')  # Cambia 'misarriendos' por la URL que deseas redirigir
    else:
        form = LibroForm()
    return render(request, 'agregar_libro.html', {'form': form})