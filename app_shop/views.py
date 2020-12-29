from django.shortcuts import render

# Class based view
from django.views.generic import ListView, DetailView

# Models
from app_shop.models import Product

# Create your views here.


class Home(ListView):
    model = Product
    template_name = "app_shop/home.html"
