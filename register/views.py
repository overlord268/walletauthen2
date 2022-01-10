from django.shortcuts import render
from django.views.generic import TemplateView

from .forms import RegisterForm

class registerIndex(TemplateView):
  template_name = 'register/index.html'
  initial = {'key': 'value'}
  form_class = RegisterForm

  def get(self, request):
    form = self.form_class(initial=self.initial)
    return render(request, self.template_name, {'form': form})
