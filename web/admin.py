from django.contrib import admin
from .models import UserProfile, Categoria, Tipo, Libro, Arriendo

admin.site.register(UserProfile)
admin.site.register(Categoria)
admin.site.register(Tipo)
admin.site.register(Libro)
admin.site.register(Arriendo)


