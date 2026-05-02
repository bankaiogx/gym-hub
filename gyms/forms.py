from django import forms

from .models import Gym, Review


class GymForm(forms.ModelForm):
    class Meta:
        model = Gym
        fields = [
            'name',
            'city',
            'address',
            'postcode',
            'latitude',
            'longitude',
            'google_place_id',
            'google_rating',
            'opening_hours_text',
            'image_url',
            'website',
            'phone_number',
            'description',
            'price_range',
            'opening_hours',
            'amenities',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amenities': forms.CheckboxSelectMultiple(),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'google_place_id': forms.HiddenInput(),
            'google_rating': forms.HiddenInput(),
            'opening_hours_text': forms.HiddenInput(),
            'image_url': forms.HiddenInput(),
            'website': forms.HiddenInput(),
            'phone_number': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                css_class = 'amenity-checkbox-list'
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{existing_classes} {css_class}".strip()
                continue

            if isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            elif isinstance(field.widget, forms.Textarea):
                css_class = 'form-control'
            else:
                css_class = 'form-control'

            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_classes} {css_class}".strip()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-control'

            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_classes} {css_class}".strip()
