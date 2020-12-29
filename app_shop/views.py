from django.shortcuts import render

# Class based view
from django.views.generic import ListView, DetailView

# Models
from app_shop.models import Product

# Mixin
from django.contrib.auth.mixins import LoginRequiredMixin


class Home(ListView):
    model = Product
    template_name = "app_shop/home.html"


class ProductDetail(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "app_shop/product_detail.html"