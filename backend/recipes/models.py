from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

from backend.const import (INGREDIENT_NAME_MAX_LENGTH,
                           MEASUREMENT_UNIT_MAX_LENGTH, RECIPE_NAME_MAX_LENGTH)
from .validators import validate_cooking_time

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name="Название ингредиента",
        help_text="Введите название ингредиента (например, Соль)",
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name="Единица измерения",
        help_text="Введите единицу измерения (например, г, мл, шт.)",
    )

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name="Название рецепта",
        help_text="Введите название рецепта (например, Борщ)",
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
        help_text="Опишите пошагово, как приготовить блюдо",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        help_text="Дата и время, когда рецепт был опубликован",
    )
    image = models.ImageField(
        upload_to="recipes/images",
        null=True,
        default=None,
        verbose_name="Изображение блюда",
        help_text="Загрузите изображение блюда",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
        help_text="Пользователь, добавивший рецепт",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты",
        help_text="Список ингредиентов, используемых в рецепте",
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (в минутах)",
        help_text="Введите время приготовления в минутах",
        validators=[validate_cooking_time],
    )

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text="Рецепт, в котором используется ингредиент",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name="Ингредиент",
        help_text="Ингредиент, используемый в рецепте",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество",
        help_text="Введите количество ингредиента",
    )

    class Meta:
        verbose_name = "ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"
        constraints = [
            UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique_recipe_ingredient"
            )
        ]

    def __str__(self):
        return f"{self.ingredient} для {self.recipe}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
        help_text="Пользователь, добавивший рецепт в избранное",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Рецепт",
        help_text="Рецепт, добавленный в избранное",
    )

    class Meta:
        verbose_name = "избранное"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            UniqueConstraint(fields=["user", "recipe"], name="unique_favorite")
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
        help_text="Пользователь, добавивший рецепт в корзину покупок",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_carts",
        verbose_name="Рецепт",
        help_text="Рецепт, добавленный в корзину покупок",
    )

    class Meta:
        verbose_name = "корзина покупок"
        verbose_name_plural = "Корзина покупок"
        constraints = [
            UniqueConstraint(fields=["user", "recipe"], name="unique_shopping_cart")
        ]
