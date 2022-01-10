from django.urls import path
from .views import registerIndex

urlpatterns = [
  path('register', registerIndex.as_view(), name='register'),
]
