"""Define forms for article, newsletter, and user registration."""
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, CustomUser, Newsletter 


class ArticleForm(forms.ModelForm):
    """Form for journalists to create and edit their articles."""

    class Meta:
        """Define the article fields and form widgets."""
        model = Article
        fields = ["title", "content", "publisher"]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Enter your article title",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "rows": 10,
                    "placeholder": "Write your article here",
                }
            ),
        }


class RegistrationForm(UserCreationForm):
    """Allow new users to register as readers or journalists."""

    role = forms.ChoiceField(
        choices=[
            (CustomUser.Role.READER, "Reader"),
            (CustomUser.Role.JOURNALIST, "Journalist"),
        ],
        initial=CustomUser.Role.READER,
        label="Register as",
    )

    class Meta:
        """Define the fields included in the registration form."""
        model = CustomUser
        fields = [
            "username",
            "email",
            "role",
        ]

    def save(self, commit=True):
        """Save the registered user with the selected role."""
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]

        if commit:
            user.save()

        return user

class NewsletterForm(forms.ModelForm):
    """Form for journalists to create and edit newsletters."""

    class Meta:
        """Define the newsletter fields and form widgets."""
        model = Newsletter
        fields = ["title", "content", "publisher", "articles"]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Enter your newsletter title",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "rows": 10,
                    "placeholder": "Write your newsletter here",
                }
            ),
            "articles": forms.CheckboxSelectMultiple(),
        }