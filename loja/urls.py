from django.urls import path
from .views import index

urlpatterns = [
    path('', index, name='loja'),   # /  → site da loja
]
