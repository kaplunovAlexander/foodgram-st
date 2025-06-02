from rest_framework import filters
import django_filters
from django_filters import rest_framework as filters

from .models import Recipe


class RecipeSearchFilter(filters.SearchFilter):
    search_param = "author"


class IngredientSearchFilter(filters.SearchFilter):
    search_param = "name"


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')
    author = filters.NumberFilter(field_name='author__id')
    
    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated or not value:
            return queryset
        return queryset.filter(favorited_by__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated or not value:
            return queryset
        return queryset.filter(in_shopping_carts__user=user)