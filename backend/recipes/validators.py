from django.core.exceptions import ValidationError


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError(
            'Время приготовления должно быть не меньше 1 минуты.'
            )
