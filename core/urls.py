from django.urls import path
from .views import *

urlpatterns = [
  path('', clsHome.as_view(), name='home'),

]