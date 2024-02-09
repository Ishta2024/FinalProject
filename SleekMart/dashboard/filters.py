# filters.py
import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Product Name')
    description = django_filters.CharFilter(lookup_expr='icontains')
    seller__name = django_filters.CharFilter(lookup_expr='icontains', label='Seller Name')
    subcategory__name = django_filters.CharFilter(lookup_expr='icontains', label='Subcategory Name')

    class Meta:
        model = Product
        fields = ['name', 'description', 'seller__name', 'subcategory__name']
