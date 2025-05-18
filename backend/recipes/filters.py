from rest_framework import filters


class RecipeSearchFilter(filters.SearchFilter):
    search_param = 'author'


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'
