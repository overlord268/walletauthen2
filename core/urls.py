from django.urls import path
from .views import clsIndex, conversionBtcHnl

urlpatterns = [
  path('', clsIndex.as_view(), name='home'),
  path('conversion/', conversionBtcHnl.as_view()),
]