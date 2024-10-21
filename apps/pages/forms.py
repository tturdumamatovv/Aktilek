from django import forms
from .models import StaticPage
from django.utils.translation import gettext_lazy as _


class StaticPageAdminForm(forms.ModelForm):
    class Meta:
        model = StaticPage
        fields = '__all__'  # Include all fields or specify which ones you want

    def clean(self):
        cleaned_data = super().clean()
        languages = ['ru', 'en', 'ky']  # Add your language codes here

        for lang in languages:
            title_field = f'title_{lang}'  # Adjust the naming according to your translation scheme
            description_field = f'description_{lang}'

            if not cleaned_data.get(title_field):
                self.add_error(title_field, _("This field is required."))

            if not cleaned_data.get(description_field):
                self.add_error(description_field, _("This field is required."))

        return cleaned_data
