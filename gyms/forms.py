from django import forms

from .models import Gym


class GymForm(forms.ModelForm):
    class Meta:
        model = Gym
        fields = [
            'name',
            'city',
            'address',
            'postcode',
            'description',
            'price_range',
            'opening_hours',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            elif isinstance(field.widget, forms.Textarea):
                css_class = 'form-control'
            else:
                css_class = 'form-control'

            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_classes} {css_class}".strip()
