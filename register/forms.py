from django import forms

class RegisterForm(forms.Form):
  email_field = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'example@email.com', 'class': 'form-control'}))
  telefono_field = forms.CharField(label='Celular', max_length=12, widget=forms.TextInput(attrs={'placeholder': '32123456', 'class': 'form-control'}))
  nombre_field = forms.CharField(label='Nombre', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Juan', 'class': 'form-control'}))
  apellidos_field = forms.CharField(label='Apellidos', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Pérez Pérez', 'class': 'form-control'}))
  id_field = forms.CharField(label='Número de identidad', max_length=18, widget=forms.TextInput(attrs={'placeholder': '', 'class': 'form-control'}))
  password_field = forms.CharField(label='Contraseña', max_length=50, widget=forms.PasswordInput(attrs={'placeholder': '', 'class': 'form-control'}))
  password_confirm_field = forms.CharField(label='Confirma tu contraseña', max_length=50, widget=forms.PasswordInput(attrs={'placeholder': '', 'class': 'form-control'}))
