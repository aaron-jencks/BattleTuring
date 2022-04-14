from django.urls import path, include
from battleground import views

urlpatterns = [
    path('playground/', views.playground)
]