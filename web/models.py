from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=45)

    def __str__(self):
        return self.nombre

class Tipo(models.Model):
    nombre = models.CharField(max_length=45)
    dias_arriendo = models.IntegerField()
    precio_dias_atraso = models.IntegerField()

    def __str__(self):
        return self.nombre

class Libro(models.Model):
    nombre = models.CharField(max_length=255)
    isbn = models.CharField(max_length=45)
    autor = models.CharField(max_length=45)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)
    disponible = models.BooleanField(default=True)
    arrendador = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class UserProfile(models.Model):

    def __str__(self):
        nombre = self.user.first_name
        apellido = self.user.last_name
        usuario = self.user.username
        return f'{id} | {nombre} {apellido} | {usuario} |'


class Arriendo(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField()
    user = models.ForeignKey(User, related_name='arriendos', on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, related_name='arriendos', on_delete=models.CASCADE)

    def __str__(self):
        id = self.id
        fecha = self.fecha
        usuario = self.user.username
        libro = self.libro.nombre
        categoria = self.libro.categoria.nombre
        return f'{id} | Fecha: {fecha} | User: {usuario} | Eq: {libro} | Cat: {categoria}'
        
    
    class Meta:
        permissions = [
            ("agregar_libros", "agregar nuevos libros"),
        ]
