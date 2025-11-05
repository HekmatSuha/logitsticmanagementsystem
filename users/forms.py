from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class StyledAuthenticationForm(AuthenticationForm):
    """Authentication form with Tailwind-compatible styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_classes = {
            "username": {
                "placeholder": "Enter your username",
                "autofocus": True,
            },
            "password": {"placeholder": "Enter your password"},
        }
        for name, field in self.fields.items():
            base_attrs = {
                "class": "w-full rounded-lg border border-border-light bg-white/80 px-4 py-3 text-sm text-gray-700 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50",
            }
            base_attrs.update(field_classes.get(name, {}))
            field.widget.attrs.update(base_attrs)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "you@example.com",
                "class": "w-full rounded-lg border border-border-light bg-white/80 px-4 py-3 text-sm text-gray-700 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50",
            }
        ),
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "First name",
                "class": "w-full rounded-lg border border-border-light bg-white/80 px-4 py-3 text-sm text-gray-700 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50",
            }
        ),
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last name",
                "class": "w-full rounded-lg border border-border-light bg-white/80 px-4 py-3 text-sm text-gray-700 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Choose a username",
            "password1": "Create a password",
            "password2": "Confirm your password",
        }
        for name, field in self.fields.items():
            if name in {"email", "first_name", "last_name"}:
                continue
            field.widget.attrs.update(
                {
                    "class": "w-full rounded-lg border border-border-light bg-white/80 px-4 py-3 text-sm text-gray-700 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50",
                    "placeholder": placeholders.get(name, ""),
                }
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
