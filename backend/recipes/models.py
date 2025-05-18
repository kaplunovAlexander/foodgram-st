from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=254)
    measurement_unit = models.CharField('Единица измерения', max_length=16)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    name = models.CharField('Название', max_length=254)
    text = models.TextField('Описание')
    pub_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images',
        null=True,
        default=None
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиент',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (мин)',
        help_text='Укажите время в минутах',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        'Количество',
        help_text='Укажите количество ингредиента'
    )

    def __str__(self):
        return f'{self.ingredient} для {self.recipe}'

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recipe')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='in_shopping_carts')

    class Meta:
        unique_together = ('user', 'recipe')
