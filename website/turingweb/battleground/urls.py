from django.urls import path, include
import views

urlpatterns = [
    path('playground/', views.playground)
]