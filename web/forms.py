from django import forms
from .models import Categoria, Libro

class CategoriaFilterForm(forms.Form):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit();'})
    )

class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['nombre', 'autor', 'isbn', 'categoria', 'tipo']
        widgets = {
            'categoria': forms.Select(choices=[('Novelas', 'Novelas'), ('Terror', 'Terror'), ('Autoayuda', 'Autoyyuda')]),
            'tipo': forms.Select(choices=[('Estandar', 'Estandar'), ('Clasicos', 'Clasicos', ('Estrenos', 'Estrenos'))]),  
        }
