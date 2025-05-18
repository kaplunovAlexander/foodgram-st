from django.http import HttpResponse
from django.db.models import Sum
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    Recipe, Ingredient, RecipeIngredient,
    ShoppingCart, Favorite
)
from .serializers import (
    RecipeSerializer, IngredientSerializer, ShortRecipeSerializer)
from .pagination import RecipePagination
from .filters import IngredientSearchFilter, RecipeSearchFilter
from .permissions import IsAuthorOrReadOnly


class RecipesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = RecipePagination
    filter_backends = (RecipeSearchFilter,)
    search_fields = ('author__id',)
    ordering_fields = ('pub_date',)
    ordering = ('-pub_date',)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')

        if is_in_shopping_cart == '1':
            if user.is_authenticated:
                queryset = queryset.filter(in_shopping_carts__user=user)
            else:
                return Recipe.objects.none()

        is_favorited = self.request.query_params.get('is_favorited')

        if is_favorited == '1':
            if user.is_authenticated:
                queryset = queryset.filter(favorited_by__user=user)
            else:
                return Recipe.objects.none()

        return queryset

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_code = f'{recipe.id:04x}'
        short_link = f'https://foodgram.example.org/s/{short_code}'
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
            detail=False,
            methods=['get'],
            url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,)
        )
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(
            in_shopping_carts__user=request.user).distinct()
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in=recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total=Sum('amount'))
        )

        print("DEBUG INGREDIENTS:", list(ingredients))

        lines = []
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            total = item['total']
            lines.append(f"{name} ({unit}) - {total}")
        content = '\n'.join(lines)

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response

    def _handle_add_remove(self, request, model, error_message):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            deleted, _ = model.objects.filter(
                user=user, recipe=recipe).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт не найден.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
            detail=True,
            methods=['post', 'delete'],
            url_path='shopping_cart',
            permission_classes=(IsAuthenticated,)
        )
    def shopping_cart(self, request, pk=None):
        return self._handle_add_remove(
            request,
            ShoppingCart,
            'Рецепт уже в списке покупок.')

    @action(
            detail=True,
            methods=['post', 'delete'],
            url_path='favorite',
            permission_classes=(IsAuthenticated,)
        )
    def favorite(self, request, pk=None):
        return self._handle_add_remove(
            request,
            Favorite,
            'Рецепт уже в избранном.')


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
