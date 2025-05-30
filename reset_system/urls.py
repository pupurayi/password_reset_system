from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_reset_request, name='submit_reset'),
]
