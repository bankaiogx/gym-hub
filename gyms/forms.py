import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Gym, Review


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        # Add Bootstrap styling to the built-in login fields.
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })


class SignupForm(UserCreationForm):
    # Email is required so accounts can be identified more clearly.
    email = forms.EmailField(
        label='Email',
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('email', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Gym Hub ID'
        self.fields['username'].help_text = (
            '3-20 characters. Letters, numbers, periods, and underscores only.'
        )
        self.fields['password1'].help_text = (
            'Use at least 8 characters, 1 uppercase letter, and 1 number.'
        )
        self.fields['password2'].help_text = ''

        placeholders = {
            'email': 'you@example.com',
            'username': 'username',
            'password1': 'Create password',
            'password2': 'Confirm password',
        }
        autocomplete = {
            'email': 'email',
            'username': 'username',
            'password1': 'new-password',
            'password2': 'new-password',
        }

        # Apply the same styling and autocomplete hints to every signup field.
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = placeholders.get(field_name, '')
            field.widget.attrs['autocomplete'] = autocomplete.get(field_name, '')

    def clean_email(self):
        # Prevent two users from registering with the same email address.
        email = self.cleaned_data['email'].strip().lower()
        user_model = get_user_model()
        if user_model.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_username(self):
        # Keep the public Gym Hub ID simple and URL-friendly.
        username = self.cleaned_data['username'].strip().lower()
        if not re.fullmatch(r'[a-z0-9._]{3,20}', username):
            raise forms.ValidationError(
                'User IDs must be 3-20 characters and only use letters, numbers, periods, or underscores.'
            )
        if username in {'admin', 'support', 'root', 'owner', 'gymhub', 'gymhubuk'}:
            raise forms.ValidationError('Please choose a different User ID.')
        return username

    def clean_password2(self):
        # Keep the password rules clear without adding a complex password UI.
        password1 = self.cleaned_data.get('password1') or ''
        password2 = self.cleaned_data.get('password2') or ''
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('The two password fields did not match.')
        if password1 and (len(password1) < 8 or not re.search(r'[A-Z]', password1) or not re.search(r'\d', password1)):
            raise forms.ValidationError(
                'Use at least 8 characters, 1 uppercase letter, and 1 number.'
            )
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class GymForm(forms.ModelForm):
    class Meta:
        model = Gym
        # Includes manual fields plus hidden fields filled by Google Places.
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
            'image',
            'image_url',
            'website',
            'phone_number',
            'description',
            'price_range',
            'opening_hours',
            'amenities',
        ]
        widgets = {
            # Limit the upload picker to image files.
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
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
        # Match Django form widgets to the existing Bootstrap/Gym Hub styling.
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
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
            # Give review comments enough space without making the form huge.
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep review fields visually consistent with the rest of the site.
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-control'

            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_classes} {css_class}".strip()
