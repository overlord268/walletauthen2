from django.urls import path
from .views import clsIndex

urlpatterns = [
  path('', clsIndex.as_view(), name='home'),
]