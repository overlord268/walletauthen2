from django.urls import path
from .views import clsIndex, conversionBtcHnl
from django.contrib.auth.decorators import login_required

urlpatterns = [
  path('', login_required(clsIndex.as_view()), name='home'),
  path('conversion/', conversionBtcHnl.as_view()),
]