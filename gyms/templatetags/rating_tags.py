from math import floor

from django import template


register = template.Library()


@register.filter
def star_states(rating):
    if rating is None:
        rounded_rating = 0
    else:
        rounded_rating = floor(float(rating) + 0.5)

    rounded_rating = max(0, min(5, rounded_rating))
    return ['filled' if index < rounded_rating else 'empty' for index in range(5)]


@register.filter
def rating_label(rating):
    if rating is None:
        return 'No ratings yet'

    rating_value = float(rating)
    if rating_value.is_integer():
        return f'{int(rating_value)}/5'

    return f'{rating_value:.1f}/5'
