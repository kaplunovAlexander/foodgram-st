from django.db.models import Sum
from django.conf import settings
from django.http import HttpResponse
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, redirect

from .filters import IngredientSearchFilter, RecipeSearchFilter, RecipeFilter
from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart
)
from .pagination import RecipePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeSerializer, ShortRecipeSerializer
)


class RecipesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = RecipePagination
    filter_backends = (
        RecipeSearchFilter, filters.OrderingFilter, DjangoFilterBackend
    )
    filterset_class = RecipeFilter
    search_fields = ("author__id",)
    ordering_fields = ("pub_date",)
    ordering = ("-pub_date",)

    def get_queryset(self):
        return Recipe.objects.all()

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_code = f'{recipe.id:04x}'
        short_link = f'{settings.SHORT_LINK_BASE_URL}/s/{short_code}/'
        return Response({'short_link': short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in_shopping_carts__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total=Sum("amount"))
        )

        lines = []
        for item in ingredients:
            name = item["ingredient__name"]
            unit = item["ingredient__measurement_unit"]
            total = item["total"]
            lines.append(f"{name} ({unit}) - {total}")
        content = "\n".join(lines)

        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="shopping_list.txt"'

        return response

    def _handle_add_remove(self, request, model, error_message):
        recipe = self.get_object()
        user = request.user

        if request.method == "POST":
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            deleted, _ = model.objects.filter(user=user, recipe=recipe).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Рецепт не найден."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        return self._handle_add_remove(
            request, ShoppingCart, "Рецепт уже в списке покупок."
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="favorite",
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        return self._handle_add_remove(
            request, Favorite, "Рецепт уже в избранном."
        )


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)


@api_view(['GET'])
def follow_short_link(request, code):
    try:
        recipe_id = int(code, 16)
    except ValueError:
        return Response({'detail': 'Некорректный код.'},
                        status=status.HTTP_400_BAD_REQUEST
                        )

    recipe = get_object_or_404(Recipe, id=recipe_id)
    return redirect(f'/api/recipes/{recipe.id}/')
