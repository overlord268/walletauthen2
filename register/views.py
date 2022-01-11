from django.db import transaction
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.generic import TemplateView
from .forms import RegisterForm
from django.contrib.auth.models import User
from .models import Customer

class registerIndex(TemplateView):
  template_name = 'register/index.html'
  initial = {'key': 'value'}
  form_class = RegisterForm
  mensaje = ''
  creado = False

  def get(self, request):
    form = self.form_class(initial=self.initial)
    return render(request, self.template_name, {'form': form, 'mensaje': self.mensaje})

  def post(self, request):
    try:
      with transaction.atomic():
        form = self.form_class(request.POST)
        if form.is_valid():
          email = form.cleaned_data['email_field']
          telefono = form.cleaned_data['telefono_field']
          nombre = form.cleaned_data['nombre_field']
          apellidos = form.cleaned_data['apellidos_field']
          numero_id = form.cleaned_data['id_field']
          password = form.cleaned_data['password_field']
          password_confirm = form.cleaned_data['password_confirm_field']

          if password == password_confirm:
            try:
              user = User.objects.create_user(username=email,
                                      email=email,
                                      password=password,
                                      first_name=nombre,
                                      last_name=apellidos)
              customer = Customer(user=user, telefono=telefono, numero_ID=numero_id)
              customer.save()
              self.mensaje = 'El usuario se creó correctamente'
              self.creado = True
            except Exception as e:
              self.mensaje = 'Error al crear el usuario'
          else:
            self.mensaje = 'Las contraseñas no coinciden'
        else:
          self.mensaje = 'Error en el formulario'
        return render(request, self.template_name, {'form': form, 'mensaje': self.mensaje, 'creado': self.creado})
    except Exception as e:
      print("EXCEPTION: ", str(e))
      #return redirect(reverse_lazy('register'))
      self.mensaje = str(e)
      form = self.form_class(initial=self.initial)
      return render(request, self.template_name, {'form': form, 'mensaje': self.mensaje, 'creado': self.creado})
