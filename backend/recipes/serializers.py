import base64

from django.core.files.base import ContentFile
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart)


class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = (
            "name",
            "measurement_unit",
        )

    def get_amount(self, obj):
        recipe = self.context.get("recipe")
        if recipe:
            try:
                recipe_ingredient = RecipeIngredient.objects.get(
                    recipe=recipe, ingredient=obj
                )
                return recipe_ingredient.amount
            except RecipeIngredient.DoesNotExist:
                return None
        return None


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientAmountSerializer(many=True, write_only=True)
    image = Base64ImageField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "image",
            "text",
            "cooking_time",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def validate(self, attrs):
        if self.instance and "ingredients" not in attrs:
            raise serializers.ValidationError(
                {"ingredients": (
                    "Поле ingredients обязательно при обновлении рецепта."
                )}
            )
        return super().validate(attrs)

    def validate_ingredients(self, value):
        ingredients_ids = [
            item["id"].id if isinstance(item["id"], Ingredient) else item["id"]
            for item in value
        ]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                "Ингредиенты должны быть уникальными."
                )
        if not ingredients_ids:
            raise serializers.ValidationError(
                "Поле ingredients не может быть пустым."
                )
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Время приготовления должно быть не меньше 1 минуты."
            )
        return value

    def get_author(self, obj):
        from users.serializers import CustomUserSerializer

        serializer = CustomUserSerializer(obj.author, context=self.context)
        return serializer.data

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["ingredients"] = IngredientRecipeSerializer(
            instance.ingredients.all(),
            many=True,
            context={"recipe": instance, **self.context},
        ).data
        return rep

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        )

    def _save_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            ) for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        author = self.context["request"].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients_data is not None:
            self._save_ingredients(instance, ingredients_data)
        return instance


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
